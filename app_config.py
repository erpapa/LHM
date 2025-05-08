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


class AppnInstance(object):
    config = None

