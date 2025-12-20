from pydantic import BaseModel
from typing   import List, Optional

class TextCompletionRequest(BaseModel):
    prompt:            str
    model:             str = "any"
    stream    :        Optional[bool]      = False
    max_tokens:        Optional[int]       = 512
    temperature:       Optional[float]     = 0.1
    top_p:             Optional[float]     = 0.9
    frequency_penalty: Optional[float]     = 0
    presence_penalty:  Optional[float]     = 0
    stop:              Optional[List[str]] = []
