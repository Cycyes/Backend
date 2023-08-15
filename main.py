# uvicorn main:app --reload --host 0.0.0.0 --port 8000
# gunicorn main:app -b 0.0.0.0:8000  -w 4 -k uvicorn.workers.UvicornH11Worker --daemon 
# pstree -ap|grep gunicorn
# rm -rf backend
# git clone --branch cyclone git@codehub.devcloud.cn-north-4.huaweicloud.com:md00002/backend.git
# lsof -i:8000
# git add . && git commit -m "update" && git push origin cyclone
# up
import os
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_422_UNPROCESSABLE_ENTITY
from dependencies import IMAGE_DIR

from routers import register, login, profile, memories, follow, comments, notice, pics, chat, room, draft, match, block

# 创建一个存放图片的文件夹
os.makedirs(IMAGE_DIR, exist_ok=True)

async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    捕捉422报错并进行自定义处理
    :param request:
    :param exc:
    :return:
    """
    x = exc.errors()
    ret = {}
    ret['host'] = request.client.host
    ret['port'] = request.client.port
    ret['method'] = request.method
    ret['base_url'] = request.base_url
    ret['headers'] = request.headers
    ret['cookies'] = request.cookies
    ret['form'] = request.form()
    ret['body'] = request.body()
    print(ret)

    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors())},
    )

app = FastAPI()

app.include_router(register.router)
app.include_router(login.router)
app.include_router(profile.router)
app.include_router(memories.router)
app.include_router(follow.router)
app.include_router(comments.router)
app.include_router(notice.router)
app.include_router(pics.router)
app.include_router(chat.router)
app.include_router(room.router)
app.include_router(draft.router)
app.include_router(match.router)
app.include_router(block.router)

app.add_exception_handler(RequestValidationError, request_validation_exception_handler)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
