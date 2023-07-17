import cv2
import numpy as np
from datetime import datetime

from supervision.tools.detections import Detections, BoxAnnotator
from supervision.draw.color import ColorPalette

from ultralytics import YOLO
import ultralytics
import os
import csv
from alert import Alert
ultralytics.checks()


MODEL = "yolov8l.pt"

model = YOLO(MODEL)
model.fuse()
boxx = BoxAnnotator(ColorPalette(), thickness=1,text_thickness=2, text_scale=1)
CLASS_NAMES_DICT = model.model.names
CLASS_ID = [16]


class VideoStreamPlayer:

    def __init__(self, streams):
        self.streams = streams
        self.text_stream = None
        self.instance_counter = 0
        self.frames_len = len(streams)
        self.num_mail = 0
        self.all_dogs = 0
        
        begin_clock = datetime.now()

        if self.frames_len == 1:
            self.grid = (1, 1)
        elif self.frames_len == 2:
            self.grid = (1, 2)
        elif self.frames_len in range(3, 5):
            self.grid = (2, 2)
        elif self.frames_len in range(5, 10):
            self.grid = (3, 3)
        elif self.frames_len in range(10, 17):
            self.grid = (4, 4)


        # Create an empty dictionary for streams and their time counters
        self.stream_times = {
            i: begin_clock for i in range(self.frames_len)}

        # Initiating alert object
        self.alert = Alert()
        self.alert.connect()

        print("Stream object intialized....")

    def update_dict(self, key):
        self.stream_times[key] = datetime.now()

    # ! ALERT SYSTEM
    def alert_system(self, frame, index_frame, mean_doggo, mean_conf,  email_thresh=2,  receivers=None):

        if receivers is None:
            receivers = ["walid-berkane@outlook.com",
                         "wiamrabhi2000@gmail.com",
                         "fatima.eljaimi17@gmail.com"]

        end_clock = datetime.now()

        diff_clock = (
            end_clock - self.stream_times[index_frame]).total_seconds()
        

        if (diff_clock > email_thresh):
            print("if True")
            cv2.imwrite('dogs_image.jpg', frame)
            print("image saved")
            self.update_dict(index_frame)
            self.alert.send_message(index_frame, "dogs_image.jpg", end_clock, mean_conf=mean_conf * 100, receivers=receivers, nbr=self.num_mail)
            # self.alert.send_alert(mean_doggo, index_frame, "dogs_image.jpg", end_clock, mean_conf=mean_conf * 100, receiver=receivers, nbr=self.num_mail)
            self.num_mail += 1

    def log_detections(self, dogs_detected, cameraID, confidence):
        fields = ["dogs_detected", "timestamp", "cameraID", "confidence"]
        file_exists = os.path.isfile("logs/detections.csv")
        with open("logs/detections.csv", "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "dogs_detected": dogs_detected,
                "timestamp": datetime.now(),
                "cameraID": cameraID,
                "confidence": confidence
            }) 

    def process_frame(self, frame, cameraID, annotate_frame=True, conf=0.8):
        try:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception:
            return None
        im_np = np.asarray(img)
        # model prediction on single frame and conversion to supervision Detections
        results = model(im_np, conf=conf, verbose=False)
        detections = Detections(
            xyxy=results[0].boxes.xyxy.cpu().numpy(),
            confidence=results[0].boxes.conf.cpu().numpy(),
            class_id=results[0].boxes.cls.cpu().numpy().astype(np.int32)
        )
        
        mask = np.isin(detections.class_id, CLASS_ID)
        detections.filter(mask=mask, inplace=True)
        # mean_doggo = len(detections.class_id)

        if annotate_frame:
            frame = boxx.annotate(frame=frame, detections=detections)

        # if mean_doggo > 0:
        #     self.log_detections(mean_doggo, cameraID, np.mean(detections.confidence))

        return detections