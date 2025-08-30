from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any

from ...crud import crud_user, crud_travel
from ...schemas.user import User, UserCreate, UserUpdate, UserWithRelations
from ...schemas.travel import Travel
from ...models.user import UserRole, User as UserModel
from ..deps import get_db, get_current_admin_user

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_admin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get admin dashboard data with controllers and their assigned employees."""
    
    # Get all controllers with their employees
    controllers = await crud_user.get_controllers(db)
    
    # Get unassigned employees
    result = await db.execute(
        text("""
            SELECT id, name, email, department, cost_center
            FROM users 
            WHERE role = 'employee' AND controller_id IS NULL
            ORDER BY name
        """)
    )
    unassigned_employees = [
        {
            "id": row[0],
            "name": row[1], 
            "email": row[2],
            "department": row[3],
            "cost_center": row[4]
        }
        for row in result.fetchall()
    ]
    
    # Get statistics
    stats_result = await db.execute(
        text("""
            SELECT 
                COUNT(CASE WHEN role = 'controller' THEN 1 END) as controller_count,
                COUNT(CASE WHEN role = 'employee' THEN 1 END) as employee_count,
                COUNT(CASE WHEN role = 'employee' AND controller_id IS NOT NULL THEN 1 END) as assigned_employees,
                COUNT(CASE WHEN role = 'employee' AND controller_id IS NULL THEN 1 END) as unassigned_employees
            FROM users
        """)
    )
    stats = stats_result.fetchone()
    
    return {
        "controllers": [
            {
                "id": controller.id,
                "name": controller.name,
                "email": controller.email,
                "department": controller.department,
                "employee_count": len(controller.employees),
                "employees": [
                    {
                        "id": emp.id,
                        "name": emp.name,
                        "email": emp.email,
                        "department": emp.department,
                        "cost_center": emp.cost_center
                    }
                    for emp in controller.employees
                ]
            }
            for controller in controllers
        ],
        "unassigned_employees": unassigned_employees,
        "statistics": {
            "total_controllers": stats[0],
            "total_employees": stats[1], 
            "assigned_employees": stats[2],
            "unassigned_employees": stats[3]
        }
    }


@router.post("/controllers", response_model=User, status_code=201)
async def create_controller(
    *,
    db: AsyncSession = Depends(get_db),
    controller_data: UserCreate,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Create a new controller (admin only)."""
    if controller_data.role != UserRole.controller:
        raise HTTPException(status_code=400, detail="Role must be 'controller'")
    
    # Check if email already exists
    existing = await crud_user.get_by_email(db, email=controller_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    return await crud_user.create(db=db, obj_in=controller_data)


@router.post("/employees", response_model=User, status_code=201)
async def create_employee(
    *,
    db: AsyncSession = Depends(get_db),
    employee_data: UserCreate,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Create a new employee (admin only)."""
    if employee_data.role != UserRole.employee:
        raise HTTPException(status_code=400, detail="Role must be 'employee'")
    
    # Check if email already exists
    existing = await crud_user.get_by_email(db, email=employee_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    return await crud_user.create(db=db, obj_in=employee_data)


@router.put("/assign-employee/{employee_id}/to-controller/{controller_id}")
async def assign_employee_to_controller(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: int,
    controller_id: int,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Assign an employee to a controller (admin only)."""
    
    # Verify employee exists and is an employee
    employee = await crud_user.get(db, id=employee_id)
    if not employee or employee.role != UserRole.employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Verify controller exists and is a controller
    controller = await crud_user.get(db, id=controller_id)
    if not controller or controller.role != UserRole.controller:
        raise HTTPException(status_code=404, detail="Controller not found")
    
    # Assign employee to controller
    try:
        await crud_user.assign_controller(db, employee_id=employee_id, controller_id=controller_id)
        return {"message": f"Employee {employee.name} assigned to controller {controller.name}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/unassign-employee/{employee_id}")
async def unassign_employee(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: int,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Remove an employee from their controller (admin only)."""
    
    # Verify employee exists
    employee = await crud_user.get(db, id=employee_id)
    if not employee or employee.role != UserRole.employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Remove assignment
    try:
        await crud_user.assign_controller(db, employee_id=employee_id, controller_id=None)
        return {"message": f"Employee {employee.name} unassigned from controller"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Delete a user (admin only). Reassigns employees if deleting a controller."""
    
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If deleting a controller, first unassign all their employees
    if user.role == UserRole.controller:
        await db.execute(
            text("UPDATE users SET controller_id = NULL WHERE controller_id = :controller_id"),
            {"controller_id": user_id}
        )
        await db.commit()
    
    # Delete the user
    deleted_user = await crud_user.remove(db=db, id=user_id)
    return {"message": f"User {deleted_user.name} deleted successfully"}


@router.get("/controller-assignments")
async def get_controller_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get detailed controller-employee assignments for admin overview."""
    
    result = await db.execute(
        text("""
            SELECT 
                c.id as controller_id,
                c.name as controller_name,
                c.email as controller_email,
                c.department as controller_department,
                e.id as employee_id,
                e.name as employee_name,
                e.email as employee_email,
                e.department as employee_department,
                e.cost_center as employee_cost_center
            FROM users c
            LEFT JOIN users e ON c.id = e.controller_id
            WHERE c.role = 'controller'
            ORDER BY c.name, e.name
        """)
    )
    
    assignments = {}
    for row in result.fetchall():
        controller_id = row[0]
        if controller_id not in assignments:
            assignments[controller_id] = {
                "controller": {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "department": row[3]
                },
                "employees": []
            }
        
        if row[4]:  # Employee exists
            assignments[controller_id]["employees"].append({
                "id": row[4],
                "name": row[5],
                "email": row[6],
                "department": row[7],
                "cost_center": row[8]
            })
    
    return list(assignments.values())


@router.get("/travels", response_model=List[Travel])
async def get_all_travels(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get all travels (admin only)."""
    return await crud_travel.get_multi(db)
