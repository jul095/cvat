
from PIL import Image


from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data.detection_utils import read_image
from detectron2.utils.logger import setup_logger
from detectron2.engine import DefaultPredictor
from detectron2.data import MetadataCatalog
from detectron2.data.catalog import Metadata
import numpy as np
from imantics import Polygons, Mask


class ModelLoader:
    def __init__(self, config_path, model_path, confidence_threshold):
        self.cfg = get_cfg()
        self.cfg.merge_from_file(model_zoo.get_config_file(config_path))
        self.cfg.MODEL.DEVICE = 'cpu' # change if you want to use cuda hardware
        self.cfg.MODEL.ROI_HEADS.SCORE_TRESH_TEST = confidence_threshold
        self.cfg.MODEL.RETINANET.SCORE_THRESH_TEST = confidence_threshold
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = confidence_threshold
        self.cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = confidence_threshold
        self.cfg.MODEL.WEIGHTS = model_path
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 15
        self.predictor = DefaultPredictor(self.cfg)        
        #self.labels =
        #MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]).thing_classes
        my_metadata = Metadata()
        self.labels = my_metadata.set(thing_classes = ['car', 'cyclist', 'car trailer', 'truck', 'truck trailer', 'car-transporter-truck', 'motorcycle', 'bus', 'police car', 'firefighter truck', 'ambulance', 'pedestrian', 'pedestrian with stroller', 'pedestrian in wheelchair', 'scooter', 'transporter']).thing_classes

    def __del__(self):
        pass

    def infer(self, image, user_specified_threshold):
        output = self.predictor(image)['instances'].to('cpu')
        result = []
        for i in range(len(output)):
            if output[i].scores >= user_specified_threshold:
                label = self.labels[output.pred_classes[i]]
                polygons = Mask(np.asarray(output[i].pred_masks)[0]).polygons()
                if(len(polygons.points[0]) >= 3):
                    points = polygons.points[0].ravel().tolist()
                    result.append({"confidence": str(output[i].scores), "label": label, "points": points,  "type": "polygon",})
        return result

