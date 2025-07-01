from database import create_db_and_tables, SessionDep

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from models import SignUp, Student

from pydantic import BaseModel
from sqlmodel import select
from typing import Annotated

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


class FormData(BaseModel):
    matricNo: str
    password: str
    model_config = {"extra": "forbid"}


@app.get("/")
async def root():
    return {"message": "Hello World"}



"""
Login Logic
"""
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, data: Annotated[FormData, Form()], session: SessionDep):
    
    statement = select(Student).where(Student.MatricNo == data.matricNo)
    result = session.exec(statement)

    dbStudent = result.first()

    if dbStudent and dbStudent.password == data.password:
        return RedirectResponse(url=f"/student/dashboard?user={dbStudent.name}&matric={dbStudent.MatricNo}", status_code=302)
    return template.TemplateResponse("login.html", {"request": request})





"""
Signup Logic
"""
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def login(student: Annotated[Student, Form()], session: SessionDep):
    session.add(student)
    session.commit()
    session.refresh(student)
    return RedirectResponse(url="/login", status_code=302)


"""
Student Dashboard

"""

@app.get("/student/dashboard", response_class=HTMLResponse)
async def student_dashboard(request: Request, user: str, matric: str):
    return templates.TemplateResponse("student_dashboard.html", {"request": request, "name": user, "matricNo": matric})


"""

Admin Dashboard

"""

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def student_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

