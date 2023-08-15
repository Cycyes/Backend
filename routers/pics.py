import base64
import os
import uuid
from fastapi import APIRouter, File, UploadFile, Depends
from pydantic import BaseModel
from starlette.responses import FileResponse
from database import models
from dependencies import IMAGE_DIR, get_current_user

router = APIRouter()

class ImageRequest(BaseModel):
    file: str
    fileName: str


# 定义一个生成随机文件名的函数
def random_filename():
    return str(uuid.uuid4())

IP = '119.3.178.68:8000'

# 定义一个上传文件的接口，返回一个链接
@router.post("/uploadImage")
async def upload_file(r: ImageRequest, current_user: models.User = Depends(get_current_user)):
    ext = r.fileName.split(".")[-1]
    fileName = f"{random_filename()}.{ext}"
    filepath = os.path.join(IMAGE_DIR, fileName)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(r.file.split(',')[1]))
    return { "code": 0, "msg": "success", "data": {"url": f"/images/{fileName}"} }

# 定义一个显示图片的接口，根据文件名返回图片内容
@router.get("/images/{filename}")
async def show_image(filename: str):
    filepath = os.path.join(IMAGE_DIR, filename)
    if os.path.isfile(filepath):
        return FileResponse(filepath)
    else:
        return {"error": "File not found"}