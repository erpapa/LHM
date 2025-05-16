### 1、ModuleNotFoundError: No module named 'requests'

```
pip install requests
```

### 2、libGL.so.1: cannot open shared object file: No such file or directory

```
sudo apt-get install libgl1
```

### 3、更换机型后运行报错pytorch3d/ops/knn.py，需要重新安装pytorch3d

```
File "/data/ubuntu/anaconda3/envs/LHM/lib/python3.10/site-packages/pytorch3d/ops/knn.py", line 74, in forward
    idx, dists = _C.knn_points_idx(p1, p2, lengths1, lengths2, norm, K, version)
RuntimeError: CUDA error: no kernel image is available for execution on the device
CUDA kernel errors might be asynchronously reported at some other API call, so the stacktrace below might be incorrect.
For debugging consider passing CUDA_LAUNCH_BLOCKING=1
Compile with `TORCH_USE_CUDA_DSA` to enable device-side assertions.
```