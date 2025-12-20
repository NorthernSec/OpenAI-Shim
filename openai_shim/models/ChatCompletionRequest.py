from pydantic import BaseModel
from typing   import List, Optional, Union

from openai_shim.models.ChatAudio   import ChatAudio
from openai_shim.models.ChatMessage import ChatMessage

class ChatCompletionRequest(BaseModel):
    model:       str = "any"
    messages:    List[ChatMessage]
    stream:      Optional[bool]  = False
    max_tokens:  Optional[int]   = 512
    temperature: Optional[float] = 0.1
    top_p:       Optional[float] = 0.9
    n:           Optional[int]   = 1
    audio:                 Optional[ChatAudio] = None
    frequency_penalty:     Optional[float]     = None
    logit_bias:            Optional[dict]      = None
    logprobs:              Optional[bool]      = None
    max_completion_tokens: Optional[int]       = None
    metadata:              Optional[dict]      = None
    modalities:            Optional[List[str]] = None
    parallel_tool_calls:   bool                = True
    """prediction"""
    presence_penalty:       Optional[float] = 0
    prompt_cache_key:       Optional[str]   = None
    prompt_cache_retention: Optional[str]   = None
    reasoning_effort:       Optional[str]   = None
    """response_format"""
    safety_identifier: Optional[str]                   = None
    service_tier:      Optional[str]                   = "auto"
    stop:              Optional[Union[str, List[str]]] = None
    store:             Optional[bool]                  = False
    """stream_options"""
    """tool_choice"""
    """tools"""
    top_logprobs: Optional[int] = None
    verbosity:    Optional[str] = None
    """web_search_options"""
