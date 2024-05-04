from passlib.context import CryptContext
#Set the algorithm bcrypt to be used in passlib CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify_pwd(plain_password, hashed_password):
    return pwd_context.verify(plain_password,hashed_password)