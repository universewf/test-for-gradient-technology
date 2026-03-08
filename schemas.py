from pydantic import BaseModel, ConfigDict, Field


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=5000)


class PostRead(BaseModel):
    id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)
