from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
import models
import schemas
from database import engine, get_db
from auth import hash_password, authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = hash_password(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks", response_model=list[schemas.Task])
def get_tasks(
        db: Session = Depends(get_db),
        sort_by: str = Query(None, description="Сортировать по: title, status, creation_time"),
        order: str = Query("asc", description="Порядок сортировки: asc(в порядке возрастания) или desc(в порядке убывания)"),
        top_n: int = Query(None,
                           description="Вернуть топ-N задач (сортировка по возрастанию приоритета, при равенстве — по убыванию времени)"),
        search: str = Query(None,
                            description="Поиск задач по тексту в title или description (нечувствителен к регистру)")):
    query = db.query(models.Task)

    if search:
        query = query.filter(or_(models.Task.title.ilike("%" + search + "%"), models.Task.description.ilike("%" + search + "%")))
    if top_n is not None:
        if top_n <= 0:
            raise HTTPException(status_code=400, detail="top_n должен быть положительным числом")
        query = query.order_by(asc(models.Task.priority), desc(models.Task.creation_time)).limit(top_n)
    else:
        if sort_by:
            if sort_by not in ["title", "status", "creation_time"]:
                raise HTTPException(status_code=400,
                                    detail="Недопустимый критерий сортировки. Используйте: title, status, creation_time")
            sort_order = asc if order == "asc" else desc
            if sort_by == "title":
                query = query.order_by(sort_order(models.Task.title))
            elif sort_by == "status":
                query = query.order_by(sort_order(models.Task.status))
            elif sort_by == "creation_time":
                query = query.order_by(sort_order(models.Task.creation_time))
    tasks = query.all()
    return tasks


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Задачи с данным id не существует, эхб")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=400, detail="Задачи с данным id не существует, эхб")
    for key, value in task.model_dump().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Задачи с данным id не существует, эхб")
    db.delete(db_task)
    db.commit()
    return {"message": f"Задача с id {task_id} удалена"}