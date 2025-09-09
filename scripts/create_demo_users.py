#!/usr/bin/env python3
"""
Create demo users for TravelExpense app
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from backend.app.db.session import engine
from backend.app.models.user import User, UserRole
from backend.app.core.auth import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def create_demo_users():
    """Create all demo users from DEMO_CREDENTIALS.md"""
    
    # Define all demo users
    demo_users = [
        # Admin
        {
            "email": "admin@demo.com",
            "password": "admin123",
            "full_name": "System Administrator",
            "department": "IT",
            "role": UserRole.admin,
            "cost_center": None,
            "controller_id": None
        },
        # Controllers
        {
            "email": "controller1@demo.com",
            "password": "controller123",
            "full_name": "Anna Controlling",
            "department": "Finance",
            "role": UserRole.controller,
            "cost_center": None,
            "controller_id": None
        },
        {
            "email": "controller2@demo.com",
            "password": "controller123",
            "full_name": "Thomas Controller",
            "department": "Management",
            "role": UserRole.controller,
            "cost_center": None,
            "controller_id": None
        },
        # Employees
        {
            "email": "max.mustermann@demo.com",
            "password": "employee123",
            "full_name": "Max Mustermann",
            "department": "Sales",
            "role": UserRole.employee,
            "cost_center": "SALES-001",
            "controller_email": "controller1@demo.com"
        },
        {
            "email": "sarah.schmidt@demo.com",
            "password": "employee123",
            "full_name": "Sarah Schmidt",
            "department": "Marketing",
            "role": UserRole.employee,
            "cost_center": "MKT-002",
            "controller_email": "controller1@demo.com"
        },
        {
            "email": "michael.weber@demo.com",
            "password": "employee123",
            "full_name": "Michael Weber",
            "department": "Development",
            "role": UserRole.employee,
            "cost_center": "DEV-003",
            "controller_email": "controller2@demo.com"
        },
        {
            "email": "lisa.mueller@demo.com",
            "password": "employee123",
            "full_name": "Lisa Müller",
            "department": "HR",
            "role": UserRole.employee,
            "cost_center": "HR-004",
            "controller_email": "controller2@demo.com"
        },
        {
            "email": "malte@demo.com",
            "password": "employee123",
            "full_name": "Malte",
            "department": "Software",
            "role": UserRole.employee,
            "cost_center": "Jesus123",
            "controller_email": "controller1@demo.com"
        },
        {
            "email": "integration.test@demo.com",
            "password": "employee123",
            "full_name": "Integration Test Employee",
            "department": "Testing",
            "role": UserRole.employee,
            "cost_center": "TEST-001",
            "controller_email": "controller1@demo.com"
        },
        {
            "email": "test.employee@demo.com",
            "password": "employee123",
            "full_name": "Test Employee",
            "department": "Testing",
            "role": UserRole.employee,
            "cost_center": "TEST-001",
            "controller_email": "controller1@demo.com"
        },
        {
            "email": "newuser@test.com",
            "password": "employee123",
            "full_name": "New User",
            "department": "General",
            "role": UserRole.employee,
            "cost_center": "N/A",
            "controller_email": "controller1@demo.com"
        },
        {
            "email": "test123@test.com",
            "password": "employee123",
            "full_name": "test employee",
            "department": "test",
            "role": UserRole.employee,
            "cost_center": "test",
            "controller_email": "controller1@demo.com"
        }
    ]
    
    async with AsyncSession(engine) as session:
        print("🔍 Checking existing users...")
        
        # Check if users already exist
        result = await session.execute(select(User))
        existing_users = result.scalars().all()
        
        if existing_users:
            print(f"Found {len(existing_users)} existing users. Clearing database...")
            for user in existing_users:
                await session.delete(user)
            await session.commit()
        
        print("👥 Creating demo users...")
        
        # Create users in two passes: first controllers, then employees
        controllers = {}
        
        # Pass 1: Create admins and controllers
        for user_data in demo_users:
            if user_data["role"] in [UserRole.admin, UserRole.controller]:
                hashed_password = get_password_hash(user_data["password"])
                
                user = User(
                    email=user_data["email"],
                    hashed_password=hashed_password,
                    full_name=user_data["full_name"],
                    department=user_data["department"],
                    role=user_data["role"],
                    cost_center=user_data.get("cost_center"),
                    is_active=True
                )
                
                session.add(user)
                await session.flush()  # Get the ID
                
                if user_data["role"] == UserRole.controller:
                    controllers[user_data["email"]] = user.id
                
                print(f"✓ Created {user_data['role'].value}: {user_data['full_name']} ({user_data['email']})")
        
        await session.commit()
        
        # Pass 2: Create employees with controller references
        for user_data in demo_users:
            if user_data["role"] == UserRole.employee:
                hashed_password = get_password_hash(user_data["password"])
                
                controller_id = None
                if "controller_email" in user_data:
                    controller_id = controllers.get(user_data["controller_email"])
                
                user = User(
                    email=user_data["email"],
                    hashed_password=hashed_password,
                    full_name=user_data["full_name"],
                    department=user_data["department"],
                    role=user_data["role"],
                    cost_center=user_data.get("cost_center"),
                    controller_id=controller_id,
                    is_active=True
                )
                
                session.add(user)
                print(f"✓ Created employee: {user_data['full_name']} ({user_data['email']}) -> Controller ID: {controller_id}")
        
        await session.commit()
        
        # Verify creation
        result = await session.execute(select(User))
        all_users = result.scalars().all()
        
        print(f"\n🎉 Successfully created {len(all_users)} demo users!")
        print("\nUser Summary:")
        for user in all_users:
            controller_info = f" (Controller: {user.controller_id})" if user.controller_id else ""
            print(f"  - {user.role.value}: {user.full_name} ({user.email}){controller_info}")

if __name__ == "__main__":
    asyncio.run(create_demo_users())
