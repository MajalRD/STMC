from GUI import GUI
from STREAM import VideoStreamPlayer
import cv2
import numpy as np
import logging
import time
import yaml

with open('src/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

stream_urls = config['streams']
emails = config['emails']

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("logs/stream_logfile.log"),
                        logging.StreamHandler()
                    ])

# streams = ["https://cam.visitthirsk.uk/images/webcam70/mjpg/video.mjpg", 
# "rtsp://admin:Admin12345@Bhascommune.ddns.net:554/cam/realmonitor?channel=1&subtype=0",
#            "http://90.94.183.168:8080/mjpg/video.mjpg"
#               , "rtsp://admin:Admin12345@192.168.1.107:554/cam/realmonitor?channel=1&subtype=0"
#            ]

streams = [
    # Maclati1 | TAXI
    # "rtsp://admin:b12345678@bhastaxi.ddns.net:554/cam/realmonitor?channel=1&subtype=0",

    # Commune
    "rtsp://admin:Admin12345@bhascommune.ddns.net:554/cam/realmonitor?channel=1&subtype=0",

    # # Majal
    # "rtsp://admin:Admin12345@bhasmajal.ddns.net:554/cam/realmonitor?channel=1&subtype=0",
    # "rtsp://admin:Admin12345@102.50.246.170:554/cam/realmonitor?channel=1&subtype=0",
    "rtsp://admin:Admin12345@192.168.1.107:554/cam/realmonitor?channel=1&subtype=0"

    # # Moulouya
    # "rtsp://admin:Admin12345@emoulouya0.ddns.net:554/cam/realmonitor?channel=1&subtype=0",

    # Province Ch1
    # "rtsp://admin:admin123@10.0.0.200:554/h264/ch1/main/av_stream",

    # #Province Ch2
    # "rtsp://admin:admin123@10.0.0.200:554/h264/ch2/main/av_stream",

    # #Province Ch3
    # "rtsp://admin:admin123@10.0.0.200:554/h264/ch4/main/av_stream",
    
    # #Province parking
    # "rtsp://admin:admin@10.0.92.83:554/cam/realmonitor?channel=1&subtype=0",
]

gui = GUI()
stream = VideoStreamPlayer(streams)

mean_doggo = 0
all_dogs = 0

frames_len = stream.frames_len

max_bad_frames = 10
estim_iters = 10
update_interval = 400

logger = True

cap_list = [None] * frames_len
frames = [None] * frames_len
rets = [None] * frames_len
fps_list = [None] * frames_len
bad_streams = [0] * frames_len
inference_times = [0] * frames_len
good_rets = [0] * frames_len
res_estimations = [0] * frames_len
frame_skippers = [0] * frames_len
is_reconnecting = [False] * frames_len



start = time.monotonic()

for i, stream_url in enumerate(streams):
    cap = cv2.VideoCapture(stream_url)
    cap_list[i] = cap
    fps_list[i] = cap.get(cv2.CAP_PROP_FPS)

# logging.info(
#     f"Streams captured in {round((time.monotonic() - start), 2)}...")


no_feed = np.zeros(
    (int(gui.video_height / 3), int(gui.width / 3), 3), dtype=np.uint8)
cv2.putText(no_feed, "No FEED", (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

while True:
    start_it = time.monotonic()

    str_prc = stream.instance_counter % frames_len
    stream.instance_counter += 1

    if stream.instance_counter == update_interval:
        # logging.info("Streams are being reinitilized ...")
        cap_list = [cv2.VideoCapture(stream) for stream in streams]
        stream.instance_counter = 0
        logger = True
        #logging.info("Streams reinitilized ...")


    if stream.instance_counter <= estim_iters:
        if logger:
            # logging.info("Streams' inference times are being estimated...")
            logger = False
        for i, cap in enumerate(cap_list):
            read_begin = time.monotonic()
            ret, frame = cap.read()
            if ret:
                stream.process_frame(frame, i)
                inference_times[i] += (time.monotonic() - read_begin)
                good_rets[i] += 1
            else:
                frame = no_feed

            frames[i] = frame
            rets[i] = ret

        if stream.instance_counter == estim_iters:
            res_estimations = [round(inf/good_rets[idx], 2) if good_rets[idx] > 0 else 0.4 for idx, inf in enumerate(inference_times)]

            for idx, est in enumerate(res_estimations):
                if est > .000001:
                    frame_skippers[idx] = round(fps_list[idx]*est*frames_len)
               

                # logging.info(f"Stream {idx} inference times is estimated at: {est}...")
                # logging.info(f"Stream {idx} frame skippers is set to: {frame_skippers[idx]}...")


    else:
        for i, cap in enumerate(cap_list):

            for _ in range(frame_skippers[i]):
                cap.grab()

            ret, frame = cap.retrieve()

            if not ret:
                if not is_reconnecting[i]:
                    # logging.warning(f"Reconnecting stream {i}....")
                    cap_list[i] = cv2.VideoCapture(streams[i])
                    is_reconnecting[i] = True

                if bad_streams[i] < max_bad_frames:
                    logging.warning(f"No feed stream {i}....")
                    frame = no_feed
                    bad_streams[i] += 1
                else:
                    # logging.warning(
                        # f"stream {i} passed the maximal number of retrying....")
                    frame = np.zeros(
                        (int(gui.video_height / 3), int(gui.width / 3), 3), dtype=np.uint8)()

                frame= no_feed
            else:
                is_reconnecting[i] = False
                bad_streams[i] = 0

            frames[i] = frame
            rets[i] = ret

        if rets[str_prc]:
            #logging.info(f"Stream {str_prc} is bieng processed ...")
            start = time.monotonic()
            dets = stream.process_frame(frames[str_prc], str_prc)
            mean_doggo = len(dets.class_id)
            # logging.info(
            #     f"Stream {str_prc} processed in {round((time.monotonic() - start), 2)} with {mean_doggo} dogs detected...")
            if mean_doggo != 0:
                mean_conf = np.mean(dets.confidence)
                stream.alert_system(frames[str_prc], str_prc, mean_doggo, mean_conf)
                stream.log_detections(mean_doggo, str_prc, mean_conf)
                logging.info(f"Stream nbr : {str_prc}  detected classes : {mean_doggo}")
                all_dogs += mean_doggo
                
    
    frame_to_show = gui.get_streams_grid(frames, stream.grid)

    gui.show(stream.num_mail, all_dogs, mean_doggo, frame_to_show)