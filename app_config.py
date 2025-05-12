# from accelerate import Accelerator
# from omegaconf import OmegaConf, DictConfig, ListConfig
# from LHM.utils.face_detector import VGGHeadDetector
# from engine.pose_estimation.pose_estimator import PoseEstimator
# from engine.pose_estimation.video2motion import Video2MotionPipeline
# try:
#     from engine.SegmentAPI.SAM import SAM2Seg
# except:
#     print("\033[31mNo SAM2 found! Try using rembg to remove the background. This may slightly degrade the quality of the results!\033[0m")
#     from rembg import remove

class AppConfig(object):
    def __init__(self, pose_estimator, face_detector, parsing_net, lhm, cfg):
        super(AppConfig, self).__init__()
        self.pose_estimator = pose_estimator
        self.face_detector = face_detector
        self.parsing_net = parsing_net
        self.lhm = lhm
        self.cfg = cfg

    @staticmethod
    def create(pose_estimator, face_detector, parsing_net, lhm, cfg):
        config = AppConfig(pose_estimator, face_detector, parsing_net, lhm, cfg)
        return config

class AppDict(object):
    def __init__(self, capacity=10000):
        super(AppDict, self).__init__()
        self.capacity = capacity
        self.iter_index = 0
        self.list = []
        self.dict = {}

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __delitem__(self, key):
        self.remove(key)

    def __len__(self):
        return len(self.dict)

    def __str__(self):
        return str(self.dict)

    def __iter__(self):
        self.iter_index = 0
        return self

    def __next__(self):
        if self.iter_index >= len(self.list):
            raise StopIteration
        key = self.list[self.iter_index]
        value = self.dict.get(key, None)
        return key, value

    def get(self, key: str): 
        return self.dict.get(key)
    
    def get(self, key: str, default: any): 
        return self.dict.get(key, default)
    
    def set(self, key: str, value: any):
        self.list.append(value)
        self.dict[key] = value
        if self.len() > self.capacity:
            self.dequeue()

    def enqueue(self, key: str, value: any):
        self.set(key, value)

    def dequeue(self):
        if self.count() == 0:
            return None
        key = self.list.pop(0)
        val = self.dict.pop(key)
        return {key: val}

    def remove(self, key: str):
        if key in self.list:
            del self.list[self.list.index(key)]
        if key in self.dict:
            del self.dict[key]

    def count(self):
        return len(self.list)

    def clear(self):
        self.list.clear()
        self.dict.clear()

class AppInstance(object):
    config = None

