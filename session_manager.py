from itsdangerous import URLSafeSerializer
from fastapi import HTTPException
from fastapi import Request
from uuid import UUID

SECRET_KEY = "super-secret-key"
serializer = URLSafeSerializer(SECRET_KEY)

def create_session(studentName: str, matricNo: str, studentId: str):
    return serializer.dumps({
        "name": studentName,
        "matricNo": matricNo,
        "id": studentId
        })

def get_username_from_session(session_token: str):
    try:
        data = serializer.loads(session_token)
        #return data.get("matricNo")
        return data
    except Exception:
        return None


def require_login(request: Request):
    token = request.cookies.get("session_token")
    data = get_username_from_session(token)
    if not data:
        return data
        #raise HTTPException(status_code=403, detail="Not authenticated")
    return data  # you can return more user info if needed

