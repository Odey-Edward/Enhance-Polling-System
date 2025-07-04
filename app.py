from database import create_db_and_tables, SessionDep

from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from models import SignUp, Student, Questions, Choices, Vote, Admin

import os
from pydantic import BaseModel
from sqlmodel import select
from typing import Annotated
from urllib.parse import urlencode
from uuid import UUID
import uvicorn

from session_manager import create_session, require_login
from shema import PollData
from sqlalchemy.orm import selectinload


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




class AdminFormData(BaseModel):
    username: str
    password: str
    model_config = {"extra": "forbid"}



@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
        return templates.TemplateResponse("signup.html", {"request": request})



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
        token = create_session(
                dbStudent.name, data.matricNo, str(dbStudent.id)
        )
        """
        params = urlencode({
            "user": dbStudent.name,
            "matric": dbStudent.MatricNo
        })

        path = url=f"/student/dashboard?{params}"

        response = RedirectResponse(url=path, status_code=302)
        """

        student = {
                "name": dbStudent.name,
                "matricNo": dbStudent.MatricNo
        }

        statement = select(Questions).options(selectinload(Questions.options))
        questions = session.exec(statement).all()

        response = templates.TemplateResponse(
            "student_dashboard.html",
            {
                "request": request,
                "student": student,
                "questions": questions
            },
            status_code=200
        )

        response.set_cookie(key="session_token", value=token, httponly=True)

        return response

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Invalid credentials"
    }, status_code=401)




"""
Signup Logic
"""
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(student: Annotated[Student, Form()], session: SessionDep):
    session.add(student)
    session.commit()
    session.refresh(student)
    return RedirectResponse(url="/login", status_code=302)



"""
Student Dashboard

"""



@app.get("/student/dashboard", response_class=HTMLResponse)
async def student_dashboard(request: Request, session: SessionDep, userData: dict = Depends(require_login)):
    if not userData:
        return RedirectResponse(url="/login", status_code=302)

    statement = select(Questions).options(selectinload(Questions.options))
    questions = session.exec(statement).all()


    return templates.TemplateResponse("student_dashboard.html", {
        "request": request,
        "student": userData,
        "questions": questions
        },
        status_code=200
    )

    

"""
@app.get("/poll", response_class=HTMLResponse)
async def student_poll(request: Request):
    return templates.TemplateResponse("poll.html", {"request": request})
"""


@app.get("/poll/{poll_id}")
def show_poll(request: Request, poll_id: UUID, session: SessionDep):
    statement = (
        select(Questions)
        .where(Questions.id == poll_id)
        .options(selectinload(Questions.options))
    )
    question = session.exec(statement).first()

    total_votes = sum([c.vote_count for c in question.options])

    for c in question.options:
        c.percentage = (c.vote_count / total_votes * 100) if total_votes else 0


    return templates.TemplateResponse("poll.html", {
        "request": request,
        "question": question
    })


@app.get("/history", response_class=HTMLResponse)
async def poll_history(request: Request):
    return templates.TemplateResponse("poll_history.html", {"request": request})


@app.get("/create_poll", response_class=HTMLResponse)
async def create_poll(request: Request):
    return templates.TemplateResponse("create_poll.html", {"request": request})

@app.post("/create_poll")
async def create_poll(request: Request, data: Annotated[PollData, Form()], session: SessionDep):
    question = Questions(value=data.question)
    session.add(question)
    session.commit()
    session.refresh(question)

    choices_texts = [
        data.choice1, data.choice2, data.choice3,
        data.choice4, data.choice5
    ]

    choices = [
        Choices(text=text, question_id=question.id)
        for text in choices_texts if text
    ]

    session.add_all(choices)
    session.commit()

    return RedirectResponse(url="/admin/dashboard", status_code=302)

@app.post("/vote")
async def vote(request: Request, session: SessionDep,
        choice_id: str = Form(),
        user: dict = Depends(require_login)):

    # Update vote count for selected choice

    #return user['id']

    choice = session.get(Choices, choice_id)

    if not choice:
        return {"error": "Invalid choice"}


    existing_vote = session.exec(
        select(Vote).where(
            Vote.user_id == user['id'],
            Vote.question_id == choice.question_id
        )
    ).first()

    if existing_vote:
        return RedirectResponse(url=f"/poll/{choice.question_id}", status_code=303)

    vote = Vote(user_id=user['id'], question_id=choice.question_id, choice_id=choice.id)
    session.add(vote)

    choice.vote_count += 1
    session.add(choice)

    session.commit()

    return RedirectResponse(url=f"/poll/{choice.question_id}", status_code=303)




"""

Administrator

"""

@app.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.post("/admin/login")
async def admin_login(request: Request, data: Annotated[AdminFormData, Form()], session: SessionDep):
    
    statement = select(Admin).where(Admin.username == data.username)
    result = session.exec(statement)

    dbAdmin = result.first()

    if dbAdmin and dbAdmin.password == data.password:
        token = create_session(
                dbAdmin.name, data.username, str(dbAdmin.id)
        )


        response = RedirectResponse(url="/admin/dashboard", status_code=303)


        response.set_cookie(key="session_token", value=token, httponly=True)

        return response



@app.get("/admin/logout")
def admin_logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("session_token")
    return response



@app.get("/admin/dashboard", response_class=HTMLResponse)
async def student_dashboard(request: Request, session: SessionDep,
        adminUser: dict = Depends(require_login)):

    if not adminUser:
        return RedirectResponse(url="/admin/login", status_code=302)

    statement = select(Questions).options(selectinload(Questions.options))
    questions = session.exec(statement).all()

    statement = select(Student)
    students = session.exec(statement).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "questions": questions,
        "students": students
    })



@app.get("/admin/poll/{poll_id}")
def show_poll_for_admin(request: Request, poll_id: UUID, session: SessionDep):
    statement = (
        select(Questions)
        .where(Questions.id == poll_id)
        .options(selectinload(Questions.options))
    )
    question = session.exec(statement).first()

    total_votes = sum([c.vote_count for c in question.options])

    for c in question.options:
        c.percentage = (c.vote_count / total_votes * 100) if total_votes else 0


    return templates.TemplateResponse("admin_poll.html", {
        "request": request,
        "question": question
    })


"""

Logout Logic

"""

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session_token")
    return response



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
