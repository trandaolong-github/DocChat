from pydantic import BaseModel


class QueryInput(BaseModel):
    text: str


class QueryOutput(BaseModel):
    result: str
    sources: list[str]


class DataInput(BaseModel):
    file_path: str


class DataOutput(BaseModel):
    message: str
