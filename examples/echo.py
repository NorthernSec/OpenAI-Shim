from fastapi import FastAPI
from openai_shim.routers.TextCompletionRouter import BaseTextCompletionAPI

class MyTextCompletionAPI(BaseTextCompletionAPI):
    async def non_stream_response(self, request_data):
        prompt = request_data.prompt
        return {"response": {"response": f"Completed: {prompt}",
                "finish_reason": "stop"}}


    def stream_response(self, request_data: dict):
        prompt = request_data.prompt
        async def generator():
            yield {"response": {"response": ""},
                   "prompt": prompt}
            for i in range(3):
                yield {
                    "response": {"response": f"{i+1}..."},
                    "prompt": prompt}
            yield {
                "response": {"response": " Ready."},
                "prompt": prompt}

            yield {
                    "response": {"response": "1...2...3... Ready.",
                                 "finish_reason": "stop"},
                    "prompt": prompt}
        return generator


app = FastAPI()
api = MyTextCompletionAPI()
app.include_router(api.router)
