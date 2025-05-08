import os
import uvicorn
import gradio as gr
import hashlib
from pathlib import Path
from fastapi import FastAPI, Body, BackgroundTasks
from LHM.utils.download_utils import download_from_url
from app import create_demo_config, create_demo, core_fn
 
app = FastAPI()
 
@app.get("/hello")
def hello():
    return {"state": 200, "msg": "hello"}

@app.post("/inference")
def inference(
    background_tasks: BackgroundTasks,
    image_url: str = Body(None),
    motion_path: str = Body(None)):
    background_tasks.add_task(execute_core_fn, image_url, motion_path)
    return {"state": 200, "message": "execute_core_fn"}

def string_to_md5(string):
    md5_val = hashlib.md5(string.encode('utf8')).hexdigest()
    return md5_val

def prepare_working_dir(image_url: str):
    image_dir = string_to_md5(image_url)
    working_dir = Path(__file__).parent.resolve() / 'exps' / 'works' / image_dir
    os.makedirs(working_dir, exist_ok=True)
    return working_dir

def execute_core_fn(image_url: str, motion_path: str):
    working_dir = prepare_working_dir(image_url)
    file_name = os.path.basename(image_url)
    image_path = os.path.join(working_dir, file_name)
    # 文件不存在则下载
    if not os.path.exists(image_path):
        download_from_url(image_url, working_dir)
    print('image_url: ', image_url)
    print('image_path: ', image_path)
    print('motion_path: ', motion_path)
    # 执行视频生成任务
    app.state.working_dir = working_dir
    core_fn(app.state.demo_config, image_path, motion_path, app.state.working_dir)
    print('output_image: ', os.path.join(working_dir, 'output.png'))
    print('output_video: ', os.path.join(working_dir, 'output.mp4'))
    print('output_mask: ', os.path.join(working_dir, 'mask.mp4'))
    # 1、视频转码，目前生成的视频较大，可能需要使用ffmpeg转码压缩
    # 2、向服务器发送任务完成的请求，服务器下载output.mp4和mask.mp4文件
    # 3、删除工作目录
    # try:
    #     os.removedirs(app.state.working_dir.name)
    #     print(f"Delete {app.state.working_dir.name} Success")
    # except OSError as e:
    #     print(f"Delete {app.state.working_dir.name} Failed: {e}")

if __name__ == '__main__':
    demo_config = create_demo_config('LHM-1B-HF')
    app.state.demo_config = demo_config
    demo = create_demo(demo_config)
    gr.mount_gradio_app(app, demo, path="/gradio")
    uvicorn.run(app, host='0.0.0.0', port=8000)
 