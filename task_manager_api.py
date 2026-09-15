from sqlite3 import dbapi2
from pydantic import BaseModel,Field
from fastapi import FastAPI,HTTPException
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from typing import Optional
import os

DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./tasks.db")
if DATABASE_URL.startswith("sqlite"):#veri tabanına bağlanamaızı sağlar
    engine=create_engine(DATABASE_URL,connect_args={"check_same_theard":False})
else:
    engine=create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # veritabanı modellerinin temel sınıfı

class TaskDB(Base):
    __tablename__="tasks" #veri tabanındaki tablonun adı
    
    id=Column(Integer,primary_key=True, index=True)
    title=Column(String)
    completed=Column(Boolean, default=False)
    owner=Column(String)
    category=Column(String,nullable=True)#veri tabanına yeni bir sütun ekliyor
    priority=Column(String, default="normal") #görevlerin öncelik sırasını belirtiyor
    created_at=Column(DateTime,default=datetime.utcnow)

class TaskCreate(BaseModel):
    title:str = Field(min_length=1)
    category: Optional[str]= None
    priority: str = "normal"

class TaskUpdate(BaseModel):
    completed: bool

class UserCreate(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)

class UserDB(Base):

    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String)
    hashed_password=Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal() #veritabanı oturumu açıyor
    try:
        yield db
    finally:
        db.close()

app=FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "gizli-bir-anahtar-buraya-degistir"
ALGORITHM = "HS256"

def create_access_token(username:str):
    expire=datetime.utcnow()+timedelta(hours=1)
    data={"sub": username,"exp":expire}
    token=jwt.encode(data,SECRET_KEY,algorithm=ALGORITHM)
    return token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


class Task(BaseModel):#görevin neye benzediğini tanımlamamızı sağlar
    id: int
    title: str
    completed: bool
    owner: str #her görevin kime ait oldugunu gösterecek

tasks:list[Task]=[]#burada görevleri tutucaz
next_id=1


@app.post("/tasks")
def post_tasks(task: TaskCreate,current_user: str = Depends(get_current_user),db = Depends(get_db)):#yeni görev ekliyoruz
    new_task=TaskDB(title=task.title,completed=False,owner=current_user,category=task.category,priority=task.priority)
    db.add(new_task) #eklenecekler listesine koyuyoruz
    db.commit() #asıl işlemi gerçekleştirip eklenecekler listesine koyuyoruz
    db.refresh(new_task) #veri tabanının atadığı id'yi geri çekip new task nesnesine ekliyoruz
    return new_task

@app.get("/tasks/{task_id}")#bu şekilde tek bir görevi getiricez
def path_parameter(task_id:int, current_user: str = Depends(get_current_user), db= Depends(get_db)):
    task= db.query(TaskDB).filter(TaskDB.id == task_id,TaskDB.owner == current_user).first()
    if not task:
       raise HTTPException(status_code=404, detail="task not found")
           
    return task
   
            
@app.put("/tasks/{task_id}")
def update_task(task_id: int,task_update: TaskUpdate,current_user: str = Depends(get_current_user), db=Depends(get_db)):#burada kullanıcadan girilen veriye göre görevi guncelliyoruz
    task= db.query(TaskDB).filter(TaskDB.id == task_id,TaskDB.owner == current_user).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    task.completed = task_update.completed  #completed değerini alıyoruz
    db.commit() #veri tabanına yazmanı sağlıyor
    db.refresh(task) #nesneyi güncel veritabanı durumuyla sekronize ediyor
    return task
    

@app.delete("/tasks/{task_id}")
def delete_task(task_id:int,current_user: str= Depends(get_current_user), db=Depends(get_db)): #bu şekilde istediğimiz görevi listeden silebiliriz
        task= db.query(TaskDB).filter(TaskDB.id == task_id,TaskDB.owner == current_user).first()
        if not task:
            raise HTTPException(status_code=404,detail="task not found")
       
        db.delete(task) #burada görevi siliyoruz
        db.commit()
        return {"message": "Task deleted"}

class User(BaseModel): #kullanıcı girişi yapılması için sınıf oluşturuyoruz
    id:int
    username:str
    hashed_password: str

users:list[User]=[] #kullanıcıları tutmak için liste oluşturuyoruz
next_user_id=1

@app.post("/register")
def register_user(user: UserCreate,db = Depends(get_db)):
    existing_user=db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400,detail ="This username already exists.")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = UserDB(username=user.username,hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Registration successful", "username": new_user.username}



@app.post("/login") #kullanıcı kayıt sistemi
def login_user(from_data: OAuth2PasswordRequestForm = Depends(),db = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == from_data.username).first()
    if not user:
        raise HTTPException(status_code=401,detail="incorrect username")
    if not pwd_context.verify(from_data.password,user.hashed_password):
        raise HTTPException(status_code=401,detail="incorrect password")
    token=create_access_token(user.username)
    return{"access_token": token}


@app.get("/tasks")#API endpoint
def bring_tasks(current_user:str = Depends(get_current_user),db= Depends(get_db),completed:bool= None,priority: str= None,category:str = None,skip: int = 0,limit: int= 10 ):
    query= db.query(TaskDB).filter(TaskDB.owner == current_user)
    
    if completed is not None:
        query=query.filter(TaskDB.completed== completed)
    if priority is not None:
        query = query.filter(TaskDB.priority == priority)
    if category is not None:
        query = query.filter(TaskDB.category == category)

    return query.offset(skip).limit(limit).all()# bunun sayesinde görevleri istediğimiz kadarlı görebilicez

def test_gecersiz_id_ile_erisim():
    response = client.get("/tasks/abc")
    assert response.status_code == 422




