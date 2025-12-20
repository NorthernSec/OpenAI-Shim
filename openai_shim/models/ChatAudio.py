from pydantic import BaseModel

class ChatAudio(BaseModel):
    format: str
    voice:  str
