import os
import shutil
import hashlib
import requests
import uvicorn
import gradio as gr
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, Body
from fastapi.responses import FileResponse
from LHM.utils.download_utils import download_from_url
from app import create_demo_config, create_demo, core_fn
from app_config import AppDict
 
app = FastAPI()

# 检查接口是否可用
@app.get("/available")
def hello():
    return {"state": 200, "msg": "ok"}

# 文件下载
@app.get("/exps/works/{task_id}/{file_name}")
def download_file(task_id: str, file_name: str):
    working_dir = get_working_dir(task_id)
    file_path = os.path.join(working_dir, task_id, file_name)
    return FileResponse(path=file_path, filename=file_name)

# 获取当前任务状态
@app.get("/task/status")
def current_task_status():
    task_id = app.state.task_id
    if task_id is None:
        return {"state": 200, "msg": "ok", "data": {"task_id": None, "status": 0, "waiting_num": 0}}
    status = app.state.task_status.get(task_id, 0)
    result = app.state.task_result.get(task_id, None)
    data = {"task_id": task_id, "status": status, "waiting_num": 0}
    if status == 4 and result is not None:
        data["output_image_path"] = result.get("output_image_path", "")
        data["output_video_path"] = result.get("output_video_path", "")
        data["mask_video_path"] = result.get("mask_video_path", "")
    return {"state": 200, "msg": "ok", "data": data}

# 查询task_id的任务状态
# 0: 没有找到这个任务
# 1: 任务排队中
# 2: 任务进行中
# 3: 任务失败
# 4: 任务完成
@app.get("/task/status/{task_id}")
def task_status(task_id: str):
    status = app.state.task_status.get(task_id, 0)
    result = app.state.task_result.get(task_id, None)
    data = {"task_id": task_id, "status": status, "waiting_num": get_waiting_num(task_id)}
    # 如果是任务完成，返回结果
    if status == 4 and result is not None:
        data["output_image_path"] = result.get("output_image_path", "")
        data["output_video_path"] = result.get("output_video_path", "")
        data["mask_video_path"] = result.get("mask_video_path", "")
    return {"state": 200, "msg": "ok", "data": data}

# 删除推理任务
@app.get("/task/remove/{task_id}")
def task_remove(task_id: str):
    status = app.state.task_status.get(task_id, 0)
    data = {"task_id": task_id, "status": status, "waiting_num": get_waiting_num(task_id)}
    # 删除任务
    app.state.task_status.remove(task_id)
    # 如果任务已完成，删除工作目录
    if status == 4:
        clear_working_dir(task_id)
    return {"state": 200, "msg": "ok", "data": data}

# 执行推理任务，生成视频
@app.post("/inference")
def inference(
    background_tasks: BackgroundTasks,
    motion_name: str = Body(None),
    image_url: str = Body(None)):
    if motion_name is None:
        return {"state": 500, "msg": "motion_name is null"}
    if image_url is None:
        return {"state": 500, "msg": "image_url is null"}
    # 生成task_id
    task_id = generate_task_id(f'{motion_name}_{image_url}')
    task_status = 1 # 等待处理
    app.state.task_status.set(task_id, task_status)
    background_tasks.add_task(execute_core_fn, task_id, motion_name, image_url)
    data = {"task_id": task_id, "status": task_status, "waiting_num": get_waiting_num(task_id)}
    return {"state": 200, "msg": "already add task", "data": data}

def generate_task_id(string):
    task_id = hashlib.md5(string.encode('utf8')).hexdigest()
    return task_id

def get_project_dir():
    return Path(__file__).parent.resolve()

def get_motion_dir():
    motion_dir = get_project_dir() / 'train_data' / 'motion_video'
    return motion_dir

def get_working_dir(task_id: str):
    working_dir = get_project_dir() / 'exps' / 'works' / task_id
    return working_dir

def get_waiting_num(task_id: str):
    num = 0
    if task_id is None:
        return num
    if len(task_id) == 0:
        return num
    task_status = app.state.task_status
    status = task_status.get(task_id, 0)
    if status != 1:
        return num
    for k, v in task_status:
        if k == task_id:
            break
        if v == 1:
            num += 1
    return num

def clear_working_dir(task_id: str):
    if task_id is None:
        return
    if len(task_id) == 0:
        return
    try:
        app.state.task_status.remove(task_id)
        working_dir = get_working_dir(task_id)
        if working_dir.exists() and working_dir.is_dir():
            shutil.rmtree(working_dir)
    except Exception as e:
        print(f'clean working_dir failed: {e}')

def clear_task_if_needed():
    if len(app.state.task_result) > 20:
        result_dict = app.state.task_result.dequeue()
        task_id = None if len(result_dict.keys()) == 0 else list(result_dict.keys())[0]
        clear_working_dir(task_id)

def execute_core_fn(task_id: str, motion_name: str, image_url: str):
    task_status = app.state.task_status.get(task_id, 0)
    # 已删除的任务直接返回
    if task_status == 0:
        return
    # 更新任务状态为执行中
    task_status = 2
    app.state.task_status.set(task_id, task_status)
    task_result = None
    task_msg = 'ok'
    try:
        motion_dir = get_motion_dir()
        motion_path = os.path.join(motion_dir, motion_name)
        working_dir = get_working_dir(task_id)
        os.makedirs(working_dir, exist_ok=True)
        file_name = os.path.basename(image_url)
        image_path = os.path.join(working_dir, file_name)
        # 文件不存在则下载
        if not os.path.exists(image_path):
            download_from_url(image_url, working_dir)
        print('image_url: ', image_url)
        print('image_path: ', image_path)
        print('motion_path: ', motion_path)
        # 执行视频生成任务
        app.state.task_id = task_id
        app.state.working_dir = working_dir
        output_image_path, output_video_path, mask_video_path = core_fn(image_path, motion_path, app.state.c, app.state.demo_config)
        project_dir = get_project_dir()
        task_result = {
            'output_image_path': str(Path(output_image_path).relative_to(project_dir)), 
            'output_video_path': str(Path(output_video_path).relative_to(project_dir)), 
            'mask_video_path': str(Path(mask_video_path).relative_to(project_dir))
        }
        app.state.task_result.set(task_id, task_result)
        task_status = 4
        task_msg = 'generate video success'
        print('execute core_fn success, result: ', task_result)
    except AssertionError as e:
        task_status = 3
        task_msg = str(e) # The input image is illegal (表示没有检测到人体，后端可根据该字符串判断)
        print(f'execute core_fn failed: {task_msg}')
    except Exception as e:
        task_status = 3
        task_msg = str(e)
        print(f'execute core_fn failed: {task_msg}')
    
    app.state.task_status.set(task_id, task_status)
    # 1、视频转码，目前生成的视频较大，可能需要使用ffmpeg转码压缩（不上传到CDN，这个可以忽略）
    # 2、使用requests向服务端发送任务完成的请求，服务端需要尽快下载output.mp4和mask.mp4文件
    # 3、删除工作目录，这个可以做自动删除，或者通过接口请求删除
    json_data = {
        "task_id": task_id,
        "status": task_status,
        "task_msg": task_msg,
        "waiting_num": 0
    }
    if task_status == 4 and task_result is not None:
        json_data["output_image_path"] = task_result.get("output_image_path", "")
        json_data["output_video_path"] = task_result.get("output_video_path", "")
        json_data["mask_video_path"] = task_result.get("mask_video_path", "")
    
    print("POST: https://api.example.com/task/complete, json=", json_data)
    response = requests.post("https://api.example.com/task/complete", json=json_data)
    print("Response: ", response)
    # app.state.task_id = None
    # app.state.working_dir = None
    # 清理之前的任务空间
    clear_task_if_needed()

if __name__ == '__main__':
    demo_config = create_demo_config('LHM-1B-HF')
    app.state.demo_config = demo_config
    app.state.task_status = AppDict(capacity=100)
    app.state.task_result = AppDict(capacity=100)
    demo = create_demo(demo_config)
    gr.mount_gradio_app(app, demo, path='/gradio')
    uvicorn.run(app, host='0.0.0.0', port=8000)
 