#!/usr/bin/env python3
"""
Database migration script to add User table and employee-controller relationships.
This script adds:
1. New 'users' table with employee-controller relationships
2. employee_id foreign key to 'travels' table
3. Migrates existing travel data to use the new user relationships
"""

import asyncio
import sqlite3
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
    
    # Add employee_id column to travels table if it doesn't exist
    async with SessionLocal() as db:
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
    
    # Create demo users and assign controller relationships
    async with SessionLocal() as db:)
    
    # Create demo users and assign controller relationships
    async with SessionLocal() as db:
        # Create controllers
        controller1 = User(
            email="controller1@demo.com",
            name="Anna Controlling",
            role=UserRole.controller,
            company="Demo GmbH",
            department="Finance",
            is_active=True
        )
        
        controller2 = User(
            email="controller2@demo.com", 
            name="Thomas Controller",
            role=UserRole.controller,
            company="Demo GmbH",
            department="Management",
            is_active=True
        )
        
        db.add(controller1)
        db.add(controller2)
        await db.commit()
        await db.refresh(controller1)
        await db.refresh(controller2)
        print("✓ Controllers created")
        
        # Create employees and assign to controllers
        employees = [
            User(
                email="max.mustermann@demo.com",
                name="Max Mustermann",
                role=UserRole.employee,
                company="Demo GmbH",
                department="Sales",
                cost_center="SALES-001",
                controller_id=controller1.id,
                is_active=True
            ),
            User(
                email="sarah.schmidt@demo.com",
                name="Sarah Schmidt", 
                role=UserRole.employee,
                company="Demo GmbH",
                department="Marketing",
                cost_center="MKT-002",
                controller_id=controller1.id,
                is_active=True
            ),
            User(
                email="michael.weber@demo.com",
                name="Michael Weber",
                role=UserRole.employee,
                company="Demo GmbH", 
                department="Development",
                cost_center="DEV-003",
                controller_id=controller2.id,
                is_active=True
            ),
            User(
                email="lisa.mueller@demo.com",
                name="Lisa Müller",
                role=UserRole.employee,
                company="Demo GmbH",
                department="HR",
                cost_center="HR-004", 
                controller_id=controller2.id,
                is_active=True
            )
        ]
        
        for employee in employees:
            db.add(employee)
        await db.commit()
        print("✓ Employees created and assigned to controllers")
        
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
