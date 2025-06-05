from pydantic import BaseModel, ConfigDict


class UserEmPasSchema(BaseModel):
    email: str
    password: str
    model_config = ConfigDict(extra="forbid")  # запрещает принимать неожидаемые параметры

class Data(BaseModel):
    text: str
    key: str

class EncodeResponse(BaseModel):
    encoded_data: str
    key: str
    huffman_codes: dict
    padding: int
