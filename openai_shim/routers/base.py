from abc     import ABC, abstractmethod
from fastapi import APIRouter


def endpoint(path: str, methods: list[str]):
    def decorator(fn):
        fn._route_info = {"path": path, "methods": methods}
        return fn
    return decorator


class BaseModule(ABC):
    def __init__(self):
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        # Scan methods for _route_info
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_route_info"):
                info = attr._route_info
                self.router.add_api_route(info["path"],
                                          attr,
                                          methods=info["methods"])


    @endpoint("/v1/models", ["GET"])
    async def handle_model_info_request(self):
        data = self.get_model_info()
        data = data or {}
        return {
                "object": "list",
                "data": [
                    {
                        "id":       data.get('model', "Unknown"),
                        "object":   "model",
                        "owned_by": data.get('owner', "Unknown"),
                    }
                ],
            }


    def get_model_info(self):
        return {"model": "Unknown (not implemented)",
                "owner": "Unknown (not implemented)"}
