import json
import time

from abc     import ABC, abstractmethod
from hashlib import sha256
from fastapi           import APIRouter, Request
from fastapi.responses import StreamingResponse

from openai_shim.models.ChatCompletionRequest import ChatCompletionRequest
from openai_shim.routers.base                 import endpoint, BaseModule


class BaseChatCompletionAPI(BaseModule):
    @endpoint("/v1/chat/completions", ["POST"])
    async def handle_completion(self, request: ChatCompletionRequest):
        if request.stream:
            generator = self.stream_response(request)
            return StreamingResponse(self._response_wrapped_generator(generator),
                                     media_type="application/json")
        else:
            response_data = await self.non_stream_response(request)
            return self.create_response(response_data)


    async def _response_wrapped_generator(self, generator):
        async for x in generator():
            data  = self.create_response(x)
            chunk = f"data: {json.dumps(data)}\n"
            if data.get('choices',[{}])[0].get('finish_reason'):
                chunk += "data: [DONE]\n\n"
            else:
                chunk += "\n"
            yield chunk


    def create_response(self, data):
        prompt    = data.get('prompt', '')
        prompt_id = data.get('id', "cmpl-" + sha256(prompt.encode()).hexdigest())
        created   = data.get('created_time', int(time.time()))
        model     = data.get('model', "unknown")
        if 'response' in data.keys():
            responses = [data['response']]
        else:
            responses = data.get('responses', [])

        template = {
            "id":      prompt_id,
            "object":  "chat.completion",
            "created": created,
            "model":   model,
            "choices": [
                {
                    "index":         i,
                    "message":{
                        "role":     resp.get("role", "assistant"),
                        "content":  resp.get("response"),
                        "logprobs": resp.get("logprobs"),
                    },
                    "finish_reason": resp.get("finish_reason")
                }
                for i, resp in enumerate(responses)],
        }
        return template


    @abstractmethod
    async def non_stream_response(self, request_data: dict):
        pass

    @abstractmethod
    def stream_response(self, request_data: dict):
        pass
