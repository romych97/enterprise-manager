from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Task, Client, User, TaskPriority
from routers.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    client_id: int
    assigned_to: int
    priority: TaskPriority
    due_date: datetime


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    client_name: str
    assigned_to_name: str

    class Config:
        from_attributes = True


@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = db.query(Client).filter(Client.id == task.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    assigned_user = db.query(User).filter(User.id == task.assigned_to).first()
    if not assigned_user:
        raise HTTPException(status_code=404, detail="Assigned user not found")

    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return TaskResponse(
        **db_task.__dict__,
        client_name=client.name,
        assigned_to_name=assigned_user.full_name,
    )


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    is_completed: Optional[bool] = None,
    priority: Optional[TaskPriority] = None,
    client_id: Optional[int] = None,
    assigned_to: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Task)

    if is_completed is not None:
        query = query.filter(Task.is_completed == is_completed)
    if priority:
        query = query.filter(Task.priority == priority)
    if client_id:
        query = query.filter(Task.client_id == client_id)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    tasks = query.offset(skip).limit(limit).all()

    response = []
    for task in tasks:
        client = db.query(Client).filter(Client.id == task.client_id).first()
        assigned_user = db.query(User).filter(User.id == task.assigned_to).first()
        response.append(
            TaskResponse(
                **task.__dict__,
                client_name=client.name,
                assigned_to_name=assigned_user.full_name,
            )
        )
    return response


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    client = db.query(Client).filter(Client.id == task.client_id).first()
    assigned_user = db.query(User).filter(User.id == task.assigned_to).first()

    return TaskResponse(
        **task.__dict__,
        client_name=client.name,
        assigned_to_name=assigned_user.full_name,
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.assigned_to:
        assigned_user = db.query(User).filter(User.id == task.assigned_to).first()
        if not assigned_user:
            raise HTTPException(status_code=404, detail="Assigned user not found")

    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)

    client = db.query(Client).filter(Client.id == db_task.client_id).first()
    assigned_user = db.query(User).filter(User.id == db_task.assigned_to).first()

    return TaskResponse(
        **db_task.__dict__,
        client_name=client.name,
        assigned_to_name=assigned_user.full_name,
    )


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
