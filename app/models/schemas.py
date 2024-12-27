from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):  # 'table=True' makes it a database table
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str

class UserCreate(SQLModel):
    name: str
    email: str
