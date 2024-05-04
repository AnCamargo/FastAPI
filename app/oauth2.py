from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from . import schema, database, models

oauth2_shceme = OAuth2PasswordBearer(tokenUrl="login")

#SECRET_KEY: It has to go in env vars
#Algorithm
#expiration time of token

SECRET_KEY = "09d25e094fgdfkwiodnvhgt76b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_shceme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED
                                          , detail="Could not validate credentials"
                                          , headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user

def verify_access_token(token: str, credentials_exception):
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: int = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schema.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data
