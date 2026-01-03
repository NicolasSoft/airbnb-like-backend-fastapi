from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.db.session import get_db
from app.models import models
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
existing = db.query(models.User).filter(models.User.email == user_in.email).first()
if existing:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
user = models.User(
name=user_in.name,
email=user_in.email,
password_hash=get_password_hash(user_in.password),
is_host=user_in.is_host,
)
db.add(user)
db.commit()
db.refresh(user)
return user

@router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
# NOTE: for simplicity use same schema; in production use OAuth2PasswordRequestForm
user = db.query(models.User).filter(models.User.email == form_data.email).first()
if not user or not verify_password(form_data.password, user.password_hash):
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
token = create_access_token(subject=str(user.id))
return {"access_token": token, "token_type": "bearer"}