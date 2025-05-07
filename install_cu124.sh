# install torch 2.4.1
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
pip install -U xformers==0.0.28.post1 --index-url https://download.pytorch.org/whl/cu124
pip install -U tb_nightly==2.14.0a20230808 --index-url https://mirrors.aliyun.com/pypi/simple

# install dependencies
pip install -r requirements.txt
pip install pydantic==2.10.6
pip install httpx[socks]
pip install rembg

# install from source code to avoid the conflict with torchvision
pip uninstall basicsr

cd ..
# pip install git+https://github.com/XPixelGroup/BasicSR
git clone --recursive https://github.com/XPixelGroup/BasicSR.git
pip install -v ./BasicSR


# install pytorch3d
# pip install "git+https://github.com/facebookresearch/pytorch3d.git"
git clone --recursive https://github.com/facebookresearch/pytorch3d.git
pip install -v ./pytorch3d

# install sam2
# pip install git+https://github.com/hitsz-zuoqi/sam2/

# or
git clone --recursive https://github.com/hitsz-zuoqi/sam2.git
pip install -v ./sam2

# install diff-gaussian-rasterization
# pip install git+https://github.com/ashawkey/diff-gaussian-rasterization/

# or
git clone --recursive https://github.com/ashawkey/diff-gaussian-rasterization.git
pip install -v ./diff-gaussian-rasterization

# install simple-knn
# pip install git+https://github.com/camenduru/simple-knn/

# or
git clone https://github.com/camenduru/simple-knn.git
pip install -v ./simple-knn
