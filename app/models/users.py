from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship


class UserBase(SQLModel):
    name: str
    email: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: UUID


class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, nullable=False)

    courses: list["Course"] = Relationship(back_populates="creator")
