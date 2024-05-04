from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    #pydantic.v1 -> In Response clasess, the class should have this:
    # class Config:
    #     orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def pwd_validate(cls, pwd: str) -> str:
        if not len(pwd) >= 8:
            raise ValueError('password should have at least 8 characters')
        elif not re.match('.*[A-Z]',pwd):
            raise ValueError('password should have at least one Upper case')
        elif not re.match('.*[a-z]',pwd):
            raise ValueError('password should have at least one lower case')
        elif not re.match('.*[0-9]',pwd):
            raise ValueError('password should have at least one number')
        elif not re.match('.*[*?¿\\/|\-_+(¨~`^)·:;.,]',pwd):
            raise ValueError('password should have at least one symbol: *?¿\\/|-_+(¨~`^)·:;.,')
        else:
            return pwd
        
class UserCreateResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str

class TokenData(BaseModel):
    id: Optional[int] = None