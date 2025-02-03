from fastapi import FastAPI, Depends, HTTPException,Path

from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session
from models import Base, Todo
from database import engine, SessionLocal
from typing import Annotated

app = FastAPI()

Base.metadata.create_all(bind=engine)

class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3, max_length=2000)
    priority: int = Field(gt=0, lt=6)
    complate: bool 


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/get_all")
async def get_all(db : db_dependency):
    return db.query(Todo).all()

@app.get("/get_by_id/{todo_id}", status_code=status.HTTP_200_OK)
async def get_by_id(db: db_dependency, todo_id:int = Path(gt=0)):
    todo=db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

@app.post("/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request:TodoRequest):
    todo = Todo(**todo_request.dict())
    db.add(todo)
    db.commit()

@app.put("/update_todo", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request:TodoRequest, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complate = todo_request.complate

    db.add(todo)
    db.commit()

@app.delete("delete_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(db:db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()