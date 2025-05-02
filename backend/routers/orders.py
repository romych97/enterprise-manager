from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Order, Client, User, OrderStatus
from routers.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class OrderBase(BaseModel):
    client_id: int
    status: OrderStatus
    total_amount: float
    description: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    total_amount: Optional[float] = None
    description: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    client_name: str

    class Config:
        from_attributes = True


@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = db.query(Client).filter(Client.id == order.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    db_order = Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Add client name to response
    response = OrderResponse(**db_order.__dict__, client_name=client.name)
    return response


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Order)

    if status:
        query = query.filter(Order.status == status)
    if client_id:
        query = query.filter(Order.client_id == client_id)

    orders = query.offset(skip).limit(limit).all()

    # Add client names to response
    response = []
    for order in orders:
        client = db.query(Client).filter(Client.id == order.client_id).first()
        response.append(OrderResponse(**order.__dict__, client_name=client.name))
    return response


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    client = db.query(Client).filter(Client.id == order.client_id).first()
    return OrderResponse(**order.__dict__, client_name=client.name)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    for key, value in order.model_dump(exclude_unset=True).items():
        setattr(db_order, key, value)

    db.commit()
    db.refresh(db_order)

    client = db.query(Client).filter(Client.id == db_order.client_id).first()
    return OrderResponse(**db_order.__dict__, client_name=client.name)


@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}
