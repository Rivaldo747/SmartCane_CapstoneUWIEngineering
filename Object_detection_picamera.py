import numpy as np
import subprocess
import cv2
from picamera2 import Picamera2

# Initialize the camera
picam = Picamera2(camera_num=0)

# Start the camera
picam.start()

# Load the pre-trained object detection model
net = cv2.dnn.readNetFromDarknet('/home/riv/Desktop/darknet/cfg/yolov3.cfg', '/home/riv/Desktop/darknet/yolov3.weights')

# Define the classes for object detection
classes = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
           'traffic light', 'fire hydrant', 'stop sign', 'bench', 'bird', 'cat',
           'dog', 'horse', 'sheep', 'cow', 'backpack',
           'umbrella', 'handbag', 'tie', 'suitcase', 'ball','kite'
           'bottle', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
           'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
           'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
           'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book',
           'clock', 'vase', 'scissors', 'toothbrush']

while True:
    # Capture a frame from the camera
    frame = picam.capture_array()
    
    # Ensure the image has 3 channels (RGB format)
    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    
    # Detect objects in the frame
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (416, 416)), 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(net.getUnconnectedOutLayersNames())
    
    # Process the detected objects
    boxes = []
    confidences = []
    classIDs = []
    
    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > 0.3:
                # Object detected
                center_x = int(detection[0] * frame.shape[1])
                center_y = int(detection[1] * frame.shape[0])
                width = int(detection[2] * frame.shape[1])
                height = int(detection[3] * frame.shape[0])
                # Rectangle coordinates
                x = int(center_x - width / 2)
                y = int(center_y - height / 2)
                boxes.append([x, y, width, height])
                confidences.append(float(confidence))
                classIDs.append(classID)
    
    # to eliminate redundant overlapping boxes with lower confidences
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    
    # Display the detected objects
    for i in indices:
        if isinstance(i, int):  # Check if i is an integer
            box = boxes[i]
            x = box[0]
            y = box[1]
            width = box[2]
            height = box[3]
            
            label = f"{classes[classIDs[i]]}: {confidences[i]:.2f}"
            
            if classes[classIDs[i]] == 'hole' or classes[classIDs[i]] == 'dip':
                detected_object = f"Obstacle detected: {classes[classIDs[i]]}"
            else:
                detected_object = f"Object detected: {classes[classIDs[i]]}"
            
            # Draw the bounding box and label
            cv2.rectangle(frame, (x, y), (x+width, y+height), (255, 0, 0), 2)
            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36,255,12), 2)
            
            # Speak the detected object using espeak
            subprocess.run(['espeak', detected_object])
    
    # Display the resulting frame
    cv2.imshow('Object Detection', frame)
    
    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
picam.stop()
picam.close()
cv2.destroyAllWindows()
