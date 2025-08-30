#!/usr/bin/env python3
"""
Database migration script to add User table and employee-controller relationships.
This script adds:
1. New 'users' table with employee-controller relationships
2. employee_id foreign key to 'travels' table
3. Migrates existing travel data to use the new user relationships
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from backend.app.core.config import settings
from backend.app.db.session import SessionLocal, init_db
from backend.app.models.user import User, UserRole
from backend.app.models.travel import Travel


async def migrate_database():
    """Run the database migration."""
    print("Starting database migration...")
    
    # Initialize database with new tables
    await init_db()
    print("✓ New tables created")
    
    async with SessionLocal() as db:
        # Add employee_id column to travels table if it doesn't exist
        try:
            # Check if employee_id column exists
            result = await db.execute(text("PRAGMA table_info(travels)"))
            columns = result.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'employee_id' not in column_names:
                print("Adding employee_id column to travels table...")
                await db.execute(text("ALTER TABLE travels ADD COLUMN employee_id INTEGER"))
                await db.commit()
                print("✓ employee_id column added")
            else:
                print("✓ employee_id column already exists")
        except Exception as e:
            print(f"Error adding column: {e}")
            await db.rollback()
            return

        # Create controllers (check if they already exist)
        existing_controller1 = await db.execute(
            text("SELECT id FROM users WHERE email = 'controller1@demo.com'")
        )
        controller1_row = existing_controller1.fetchone()
        
        if not controller1_row:
            controller1 = User(
                email="controller1@demo.com",
                name="Anna Controlling",
                role=UserRole.controller,
                company="Demo GmbH",
                department="Finance",
                is_active=True
            )
            db.add(controller1)
            await db.commit()
            await db.refresh(controller1)
            print("✓ Controller 1 created")
        else:
            # Get existing controller
            result = await db.execute(
                text("SELECT * FROM users WHERE email = 'controller1@demo.com'")
            )
            controller1_data = result.fetchone()
            controller1 = User(
                id=controller1_data[0],
                email=controller1_data[1],
                name=controller1_data[2],
                role=UserRole.controller,
                company=controller1_data[4],
                department=controller1_data[5],
                is_active=True
            )
            print("✓ Controller 1 already exists")
        
        existing_controller2 = await db.execute(
            text("SELECT id FROM users WHERE email = 'controller2@demo.com'")
        )
        controller2_row = existing_controller2.fetchone()
        
        if not controller2_row:
            controller2 = User(
                email="controller2@demo.com", 
                name="Thomas Controller",
                role=UserRole.controller,
                company="Demo GmbH",
                department="Management",
                is_active=True
            )
            db.add(controller2)
            await db.commit()
            await db.refresh(controller2)
            print("✓ Controller 2 created")
        else:
            # Get existing controller
            result = await db.execute(
                text("SELECT * FROM users WHERE email = 'controller2@demo.com'")
            )
            controller2_data = result.fetchone()
            controller2 = User(
                id=controller2_data[0],
                email=controller2_data[1],
                name=controller2_data[2],
                role=UserRole.controller,
                company=controller2_data[4],
                department=controller2_data[5],
                is_active=True
            )
            print("✓ Controller 2 already exists")
        
        # Create employees and assign to controllers (check if they already exist)
        employee_data = [
            {
                "email": "max.mustermann@demo.com",
                "name": "Max Mustermann",
                "department": "Sales",
                "cost_center": "SALES-001",
                "controller_id": controller1.id if hasattr(controller1, 'id') else controller1_row[0]
            },
            {
                "email": "sarah.schmidt@demo.com",
                "name": "Sarah Schmidt",
                "department": "Marketing",
                "cost_center": "MKT-002",
                "controller_id": controller1.id if hasattr(controller1, 'id') else controller1_row[0]
            },
            {
                "email": "michael.weber@demo.com",
                "name": "Michael Weber",
                "department": "Development",
                "cost_center": "DEV-003",
                "controller_id": controller2.id if hasattr(controller2, 'id') else controller2_row[0]
            },
            {
                "email": "lisa.mueller@demo.com",
                "name": "Lisa Müller",
                "department": "HR",
                "cost_center": "HR-004",
                "controller_id": controller2.id if hasattr(controller2, 'id') else controller2_row[0]
            }
        ]
        
        created_count = 0
        for emp_data in employee_data:
            existing = await db.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": emp_data["email"]}
            )
            if not existing.fetchone():
                employee = User(
                    email=emp_data["email"],
                    name=emp_data["name"],
                    role=UserRole.employee,
                    company="Demo GmbH",
                    department=emp_data["department"],
                    cost_center=emp_data["cost_center"],
                    controller_id=emp_data["controller_id"],
                    is_active=True
                )
                db.add(employee)
                created_count += 1
        
        if created_count > 0:
            await db.commit()
            print(f"✓ {created_count} employees created and assigned to controllers")
        else:
            print("✓ All employees already exist")
        
        # Update existing travels to link to employees by name
        result = await db.execute(text("SELECT id, employee_name FROM travels"))
        travels = result.fetchall()
        
        for travel_id, employee_name in travels:
            # Find matching user by name
            result = await db.execute(
                text("SELECT id FROM users WHERE name = :name"),
                {"name": employee_name}
            )
            user_row = result.fetchone()
            
            if user_row:
                user_id = user_row[0]
                await db.execute(
                    text("UPDATE travels SET employee_id = :user_id WHERE id = :travel_id"),
                    {"user_id": user_id, "travel_id": travel_id}
                )
                print(f"✓ Linked travel {travel_id} to user {user_id} ({employee_name})")
        
        await db.commit()
        print("✓ Existing travels linked to users")
        
        # Print summary
        controller_count = await db.execute(
            text("SELECT COUNT(*) FROM users WHERE role = 'controller'")
        )
        employee_count = await db.execute(
            text("SELECT COUNT(*) FROM users WHERE role = 'employee'")
        )
        linked_travels = await db.execute(
            text("SELECT COUNT(*) FROM travels WHERE employee_id IS NOT NULL")
        )
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"   📋 Controllers: {controller_count.scalar()}")
        print(f"   👥 Employees: {employee_count.scalar()}")
        print(f"   ✈️  Linked travels: {linked_travels.scalar()}")
        
        # Show controller assignments
        print(f"\n👔 Controller Assignments:")
        result = await db.execute(
            text("""
                SELECT c.name as controller_name, 
                       COUNT(e.id) as employee_count,
                       GROUP_CONCAT(e.name, ', ') as employees
                FROM users c
                LEFT JOIN users e ON c.id = e.controller_id  
                WHERE c.role = 'controller'
                GROUP BY c.id, c.name
                ORDER BY c.name
            """)
        )
        
        for row in result.fetchall():
            controller_name, emp_count, employees = row
            employees_list = employees if employees else "No employees assigned"
            print(f"   • {controller_name}: {emp_count} employees ({employees_list})")


if __name__ == "__main__":
    asyncio.run(migrate_database())
