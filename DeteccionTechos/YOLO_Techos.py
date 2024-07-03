import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt

dir = "prueba.jpg"
img = cv2.imread(dir)

model = YOLO('RoofModel.pt')
results = model.predict(img)[0]

Area = 0
for box in results[0].boxes.xyxy:
    R = np.array(box).astype(int)
    Area += (abs(R[2]-R[0])*abs(R[3]-R[1]))*0.0236**2
Area = Area*((5000**2)/10000) #Escala/Conversion a m

# print(Area)

# res = results[0].plot()
# cv2.imwrite("final.jpg",res)