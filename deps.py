from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
payload = decode_access_token(token)
if payload is None:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
user_id = payload.get("sub")
user = db.query(models.User).filter(models.User.id == int(user_id)).first()
if not user:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
return user