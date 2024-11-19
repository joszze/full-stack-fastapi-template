from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class URL(BaseModel):
    url: str
     
class TextData(BaseModel):
    data: str
    