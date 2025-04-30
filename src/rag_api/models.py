from pydantic import BaseModel


class QueryInput(BaseModel):
    query: str
    llm: str


class QueryOutput(BaseModel):
    result: str
    sources: list[str]


class DataInput(BaseModel):
    file_name: str


class DataOutput(BaseModel):
    message: str


class ModelOutput(BaseModel):
    models: list[str]
