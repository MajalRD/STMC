import cv2
import torch
import numpy as np
from tracker import *
import datetime
import os
import csv
import math
import time 
from datetime import date
import datetime
from GUI import GUI
import pandas as pd
import matplotlib.pyplot as plt
import json
import requests

plt.rcParams.update({'lines.linewidth': 7, 'axes.linewidth': 7})

i=0
import torch
torch.cuda.is_available()


#Creation of figure for Graphs
def createfig(times,vehicule,vehicule2,vehicule_name,name):
   
    fig, ax = plt.subplots(figsize=(16, 11))
    ax.plot(times, vehicule, color="#03436B", marker='o')
    ax.plot(times, vehicule2, color="#C67F41", marker='o')
    ax.fill_between(times, vehicule, where=(vehicule > 0), interpolate=True, color='#03436B', alpha=0.15)
    ax.fill_between(times, vehicule2, where=(vehicule2 > 0), interpolate=True, color='#C67F41', alpha=0.15)
    ax.tick_params(axis='y', which='major', labelsize=42, colors='#03436B')
    ax.tick_params(axis='x', which='major', labelsize=35, colors='#03436B')
    ax.spines['left'].set_color('#000C1B')
    ax.spines['bottom'].set_color('#000C1B')
    ax.spines['right'].set_color('#000C1B')
    ax.spines['top'].set_color('#000C1B')
    ax.tick_params(axis='x', rotation=30)
    plt.savefig(name, transparent=True)
    plt.close()

#Create arrays for current graph representations
cars = np.zeros(10) 
motos = np.zeros(10)
trucks = np.zeros(10)
buses = np.zeros(10)
#Create arrays for previous graph representations
cars2 = np.zeros(10) 
motos2 = np.zeros(10)
trucks2 = np.zeros(10)
buses2 = np.zeros(10)
val = datetime.datetime.now().strftime("%H-%M")[:-1]
times=[val+'0',val+'1',val+'2',val+'3',val+'4',val+'5',val+'6',val+'7',val+'8',val+'9']

n = 0
#create line graph 
createfig(times,cars,cars2,"cars","cars.png")
createfig(times,motos,motos2,"Motorcycles","Motos.png")
createfig(times,trucks,trucks2,"Trucks","Trucks.png")
createfig(times,buses,buses2,"Buses","Buses.png")
#Calling GUI
gui = GUI()
#importing weights
model = torch.hub.load('ultralytics/yolov5', 'yolov5m', pretrained=True)
classes = model.names


font = cv2.FONT_HERSHEY_SIMPLEX
start = datetime.datetime.now()
filename = "Rapport " + start.strftime("%Y-%m-%d %H-%M")+".csv"
if os.path.isfile(filename):
    True
else:
    # If the file doesn't exist, create it and write the header row
    with open(filename, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Début","Fin","Voiture ","Camion ","Moto","Bus"])

#Video source ( uncomment the needed one )
#cap = cv2.VideoCapture('RTSP Live viedeo')
#cap = cv2.VideoCapture("input_video.mp4")

#Creating count variables
count = 0
bus=set()
truck=set()
motorcycle=set()
car=set()
ncar = 0
ntruck = 0
nbus = 0
nmot = 0
n=0

#import tracker
tracker = Tracker()

#Create counting area ( should be done manually for this version )
area=[(397, 305),(475,337),(850,272),(710, 240)]
#part of image to apply vehicle detection
roi = [(200, 100), (900, 500)] 
start = datetime.datetime.now()
st = start.strftime("%H-%M-%S")
names = ['car','motorcycle','bus','truck']


while True:
    # For optimization and fluent detection, we skip frames efficiently using grab and retrieve 
    cap.grab()
    count += 1
    if count % 8 != 0:
        continue
    ret , frame = cap.retrieve()
    if not ret:
        #cap = cv2.VideoCapture('rtsp:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        continue
    frame = cv2.resize(frame, (1020, 600))  # resize the frame
    frame_height, frame_width = frame.shape[:2]
    cropped_frame = frame[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]  # crop the frame within the ROI
    results = model(cropped_frame)  # perform object detection on the cropped frame
    lists = []
    
    # Extracting informations from results
    for index, rows in results.pandas().xyxy[0].iterrows():
        x = int(rows[0]) + roi[0][0]
        y = int(rows[1]) + roi[0][1]
        x1 = int(rows[2]) + roi[0][0]
        y1 = int(rows[3]) + roi[0][1]
        b = str(rows['name'])
        conf = rows['confidence']
        if b in names and conf>0.5:
            clas = b
            lists.append([x,y,x1,y1,clas])
        #update tracker to count new cars
    idx_bbox = tracker.update(lists)
    for bbox in idx_bbox:
        x2,y2,x3,y3,clas,ids = bbox
    
        result=cv2.pointPolygonTest(np.array(area,np.int32),(((x3+x2)/2,y3)),False)
        if clas in names:
            if result > 0:
                exec(clas+".add(ids)")

    current = datetime.datetime.now()
    cur = current.strftime("%H-%M-%S")
    delta = current - start
    seconds = delta.total_seconds()
    # Show the frame with the GUI
    gui.show(n,str(ncar+len(car)),str(nmot+len(motorcycle)),str(ntruck+len(truck)),str(nbus+len(bus)),frame)
    
    if cv2.waitKey(0) & 0xFF == 27:
        break
    if seconds > 5:
        
        #Update the csv every x seconds( here 5 seconds )
        row = [st,cur,len(car),len(truck),len(motorcycle),len(bus)]
        with open(filename, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row) 
        s = int(start.strftime("%H-%M")[-1])

        n = n+math.ceil(cars[s]/5)
        #Updating count
        cars[s] = cars[s]+len(car)
        motos[s] = motos[s]+len(motorcycle)
        trucks[s] = trucks[s]+len(truck)
        buses[s] = buses[s]+len(bus)
        times[s] = start.strftime("%H-%M")
        #Check time to see if we update the graph and csv report
        if start.strftime("%H-%M") != current.strftime("%H-%M"):
            filename = "Rapport " + start.strftime("%Y-%m-%d %H-%M")+".csv"
        if start.strftime("%H-%M")[:-1] != current.strftime("%H-%M")[:-1]:
            #If 10 minutes passed ( threshold to update graphs ) : reset counts whule saving graph
            print("a")
            for ve in range(len(cars)) :
                cars2[ve] = cars[ve]
                trucks2[ve] = trucks[ve]
                buses2[ve] = buses[ve]
                motos2[ve] = motos[ve]
            cars = np.zeros(10) 
            motos = np.zeros(10)
            trucks = np.zeros(10)
            buses = np.zeros(10)
            ncar = 0
            ntruck = 0
            nbus = 0
            nmot = 0
            val = current.strftime("%H-%M")[:-1]
            times=[val+'0',val+'1',val+'2',val+'3',val+'4',val+'5',val+'6',val+'7',val+'8',val+'9']
        createfig(times,cars,cars2,"cars","cars.png")
        createfig(times,motos,motos2,"Motorcycles","Motos.png")
        createfig(times,trucks,trucks2,"Trucks","Trucks.png")
        createfig(times,buses,buses2,"Buses","Buses.png")
        nmot = nmot + len(motorcycle)
        ncar = ncar + len(car)
        ntruck = ntruck + len(truck)
        nbus = nbus + len(bus)
        car = set()
        bus=set()
        truck=set()
        motorcycle=set()
        lists=[]
        tracker = Tracker()
        start = current
        st=cur
cap.release()
cv2.destroyAllWindows()