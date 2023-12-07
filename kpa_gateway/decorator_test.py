
from typing import Callable


class APIRoute:
    def __init__(self, path: str, endpoint: Callable) -> None:
        self.path: str = path
        self.endpoint: Callable = endpoint

    def handle(self, data):
        ...

    def match(self, data):
        ...

class APIRouter:
    def __init__(self) -> None:
        self.routers: list[APIRoute] = []

    def __call__(self, data):
        for router in self.routers:
            if router.match(data):
                router.handle(data)

    def add_api_route(self, method: str, path: str, endpoint: Callable, ) -> None:
        self.routers.append(APIRoute(path, endpoint))

    def api_route(self, methodstr, path: str, *, response_model = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            self.add_api_route(methodstr, path, func)
            return func
        return decorator

    def get(self, path: str) -> Callable:
        return self.api_route('get', path)

    # def control_command(self, cmd_type: int, cmd_code: int):
    #     return self.api_route('control_command', )

class App:
    def __init__(self) -> None:
        self.router = APIRouter()

    def __call__(self, data):
        self.router(data)

    def get(self, path: str) -> Callable:
        return self.router.get(path)


if __name__ == '__main__':
    app = App()

    @app.get('bar')
    def foo():
        print('hello')