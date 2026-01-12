import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from fastapi import FastAPI
from openai_shim.routers.TextCompletionRouter import BaseTextCompletionAPI
from openai_shim.routers.ChatCompletionRouter import BaseChatCompletionAPI

from kani import PromptPipeline, ChatRole, Kani, AIFunction, ChatMessage
from kani.engines.llamacpp import LlamaCppEngine

model_path = "/models/meta-llama-3.1-8b-instruct-q4_k_m.gguf"

pipeline = (
    PromptPipeline()
        .wrap(role=ChatRole.SYSTEM,    prefix="<|start_header_id|>system<|end_header_id|>\n",    suffix="\n<|eot_id|>")
        .wrap(role=ChatRole.USER,      prefix="<|start_header_id|>user<|end_header_id|>\n",      suffix="\n<|eot_id|>")
        .wrap(role=ChatRole.ASSISTANT, prefix="<|start_header_id|>assistant<|end_header_id|>\n", suffix="\n<|eot_id|>")
        .conversation_fmt(             prefix="<|begin_of_text|>\n", sep="")
    )

engine = LlamaCppEngine(model_path=model_path, prompt_pipeline=pipeline)
agent  = Kani(engine)


_ROLES = {
    'system':    ChatMessage.system,
    'user':      ChatMessage.user,
    'assistant': ChatMessage.assistant
}

def parse_messages(messages):
    data = []
    for m in messages:
        if m.role not in _ROLES.keys():
            print("!!! UNKNOWN ROLE: ", m.role); continue
        data.append(_ROLES[m.role](m.content))
    return data


class MyTextCompletionAPI(BaseTextCompletionAPI):
    def __init__(self):
        self.agent  = agent
        super().__init__()


    async def non_stream_response(self, request):
        prompt = request.prompt
        self.agent.chat_history = []
        async for msg in self.agent.full_round(prompt, max_function_rounds = 2):
            response = msg.text
        return {
            "response": {"response": response, "finish_reason": "stop"},
            "prompt": prompt
        }


    def stream_response(self, request):
        prompt = request.prompt
        self.agent.chat_history = []
        async def generator():
            async for stream in self.agent.full_round_stream(prompt):
                if stream.role == ChatRole.ASSISTANT:
                    async for token in stream:
                        yield {
                            "response": {"response": token},
                            "prompt": prompt}
                    response = await stream.message()
            yield {
                "response": {"response": response.content,
                             "finish_reason": "stop"},
                "prompt": prompt}
        return generator


    def get_model_info(self):
        return {"model": "test", "owner": "me"}


class MyChatCompletionAPI(BaseChatCompletionAPI):
    def __init__(self):
        self.agent  = agent
        super().__init__()


    async def non_stream_response(self, request):
        self.agent.chat_history = parse_messages(request.messages)
        prompt = self.agent.chat_history.pop().content
        async for msg in self.agent.full_round(prompt, max_function_rounds = 2):
            response = msg.text
        return {
            "response": {"response": response, "finish_reason": "stop"},
            "prompt": prompt
        }


    def stream_response(self, request):
        self.agent.chat_history = parse_messages(request.messages)
        prompt = self.agent.chat_history.pop().content
        async def generator():
            async for stream in self.agent.full_round_stream(prompt):
                if stream.role == ChatRole.ASSISTANT:
                    async for token in stream:
                        yield {
                            "response": {"response": token},
                            "prompt": prompt}
                    response = await stream.message()
            yield {
                "response": {"response": response.content,
                             "finish_reason": "stop"},
                "prompt": prompt}
        return generator


    def get_model_info(self):
        return {"model": "test", "owner": "me"}



#BaseChatCompletionAPI

app      = FastAPI()
text_api = MyTextCompletionAPI()
chat_api = MyChatCompletionAPI()
app.include_router(text_api.router)
app.include_router(chat_api.router)
