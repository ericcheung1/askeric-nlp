from pydantic import BaseModel
from typing import List

class Texts(BaseModel):
    text_id: str | None = None
    text: str

class UserInputs(BaseModel):
    texts: List[Texts]

            
        

            