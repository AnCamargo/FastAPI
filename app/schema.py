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

class UserCreateResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

class Post(PostBase):
    id: int
    user_id: int
    created_at: datetime
    user: UserCreateResponse
    #pydantic.v1 -> In Response clasess, the class should have this:
    # class Config:
    #     orm_mode = True

class PostResponse(BaseModel):
    Post: Post
    Votes: int

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

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str

class TokenData(BaseModel):
    id: Optional[int] = None

class VoteReq(BaseModel):
    post_id: int
    vote_dir: int

    @field_validator('vote_dir')
    @classmethod
    def vote_dir_validate(cls, vote_dir: int) -> int:
        if vote_dir < -1 or vote_dir > 1:
            raise ValueError('vote_dir should be in (-1, 0, 1) values')
        return vote_dir