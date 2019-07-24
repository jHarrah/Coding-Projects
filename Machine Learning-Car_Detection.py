import os
import numpy as np
import mrcnn.config
import mrcnn.utils
import imp
from mrcnn.model import MaskRCNN
from pathlib import Path 
import time
import cv2
import math

import tensorflow as tf


# Configuration that will be used by the Mask-RCNN library
class MaskRCNNConfig(mrcnn.config.Config):
    NAME = "coco_pretrained_model_config"
    IMAGES_PER_GPU = 1
    GPU_COUNT = 1
    NUM_CLASSES = 1 + 80  # COCO dataset has 80 classes + one background class
    DETECTION_MIN_CONFIDENCE = 0.6


# Filter a list of Mask R-CNN detection results to get only the detected cars / trucks
def get_car_boxes(boxes, class_ids):
    car_boxes = []

    for i, box in enumerate(boxes):
        # If the detected object isn't a car / truck, skip it
        if class_ids[i] in [3, 8, 6]:
            car_boxes.append(box)
           
    return np.array(car_boxes)
def DataPush(LotName,CalculatedUseData):   
 # FUNCTION PURPOSE: This function is intended to push calculated data to the database 
 # for storage and to ArcGis for presentation 
    #ArcGIS Portion: 
    from arcgis.gis import GIS 
    from arcgis.features import FeatureLayer 
    from pathlib import Path  
    from dotenv import load_dotenv
    import os 
    # testing to ensure that CalculatedUseData dict was successfully sent to function
    print(CalculatedUseData)     
    #This dictionary is a "Key". It will map lot names to its related ID #
    KeyDict={'FoyLot':6,'TechLot':9,'MMCS_8th':8}

    #Using dotenv-Python to obscure ALL login
    #environmental var "username" returns username of logged in user, not what is present in the .env file
    load_dotenv(dotenv_path=".\Auth.env" )
    gis = GIS('https://arcgis.com',os.getenv("ArcGIS_username"),os.getenv("password"))
    UpdateParking=gis.content.get("be4c926a720445968f8e99cd89152d05")
    TestUpdate=UpdateParking.layers[0]

    #Var used as loop input control 
    DictLen= len(CalculatedUseData)
    
    #LOOP Note: This loop will verify that the lot name is found in both dictionaries, then proceed to push data to AGO.
    for loopCtl in range(DictLen):  
        name= LotName[loopCtl]
        print(LotName[loopCtl])
        if name in KeyDict and CalculatedUseData:  
                print(KeyDict[name])
                col_id= KeyDict.get(name)
                ReturnedPercent= CalculatedUseData.get(name)
                print(TestUpdate.calculate(where='"id"={}'.format(col_id) ,calc_expression={"field":"PercentFull","value":ReturnedPercent}))
        else: 
                print("The provided keys were not found.")
                continue    


def CalPercent(NumOfCars,name): 
    # CalDict holds lot parking capacity
    calDict={'FoyLot':529,'TechLot':215,'MMCS_8th':189}
    print("Lot name = " + name+ " - From CalPercent")
    if name in calDict: 
         capacity= calDict[name]
    else: 
        print("The provided key was not found.")
    # Trunc returns a nice real number    
    return math.trunc((NumOfCars/capacity) * 100) 

# MAIN

if __name__ == "__main__":
    carsCounted=0
    # Root directory of the project
    ROOT_DIR = Path(".")

    # Directory to save logs and trained model
    MODEL_DIR = os.path.join(ROOT_DIR, "logs")

    # Local path to trained weights file
    COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

    # Download COCO trained weights from Releases if needed
    if not os.path.exists(COCO_MODEL_PATH):
        mrcnn.utils.download_trained_weights(COCO_MODEL_PATH)

    # Directory of images to run detection on
    #IMAGE_DIR = os.path.join(ROOT_DIR, "c:/users/Justin/Videos/")

    # Video file or camera to process - set this to 0 to use your webcam instead of a video file
    #'''VIDEO_SOURCE = "TESTVideo.mp4"'''

    # Create a Mask-RCNN model in inference mode
    model = MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=MaskRCNNConfig())

    # Load pre-trained model
    model.load_weights(COCO_MODEL_PATH, by_name=True)

    # Location of parking spaces
    parked_car_boxes = None

 
    

    #Introduce a frame analysis delay 
    framesAnalysed=0 

     ## FIND NUMBER OF file(IMAGES) IN TARGET DIRECTORY AND USE THIS NUMBER AS A LOOP CONTROL
     # An ARRAY WILL BE USED TO PASS THE IMAGE LOCATION DATA 
     
     #!!! VAR 'dirs' is not used but removal causes an error with the nested FOR. !!! 
     
    ImagesForProcessing=[] #--> Used as a loop control
    LotName=[] #--> Used to handle lot names 
    CalculatedUseData={}#--> Dict used for holding calcluated use percentage for each lot. Will be used to feed data into 
    #DataPush function
    for root, dirs, files in os.walk("D:\GIS_Stuff\CapturedImageAPSUParking", topdown=True):
        for name in files:
            ImagesForProcessing.append(os.path.join(root, name))
            #Stripping image type designation since it is needed for lot identification  
            nameUpdated= name.strip('.jpg')
            LotName.append(nameUpdated)  
    
    for InputImage in range(len(ImagesForProcessing)):
        
        # Load the video file we want to run detection on. THis statement relies on the iteration of the FOR loop to continue to 
        # The next image
            video_capture = cv2.VideoCapture(ImagesForProcessing[InputImage])

            # Loop over each frame of video
            while video_capture.isOpened():
                success, frame = video_capture.read()
                if not success:
                    break

                # Convert the image from BGR color (which OpenCV uses) to RGB color
                rgb_image = frame[:, :, ::-1]

                # Run the image through the Mask R-CNN model to get results.
                results = model.detect([rgb_image], verbose=0)

                # Mask R-CNN assumes we are running detection on multiple images.
                # We only passed in one image to detect, so only grab the first result.
                r = results[0]

                # The r variable will now have the results of detection:
                # - r['rois'] are the bounding box of each detected object
                # - r['class_ids'] are the class id (type) of each detected object
                # - r['scores'] are the confidence scores for each detection
                # - r['masks'] are the object masks for each detected object (which gives you the object outline)

                # Filter the results to only grab the car / truck bounding boxes
                car_boxes = get_car_boxes(r['rois'], r['class_ids'])
                #Reset car counter to 0 after each frame cycle
                carsCounted=0
                
                print("Cars found in frame of video:")

                # Draw each box on the frame
                for box in car_boxes:
                
                
                    print("Car: ", box)
                    
                    y1, x1, y2, x2 = box

                    # Draw the box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
                    #count of Boxes
                    carsCounted=carsCounted+1
                    
                   
                print(carsCounted)
                ReturnedPercentage=CalPercent(carsCounted,LotName[InputImage]) 
                CalculatedUseData.update({LotName[InputImage]:ReturnedPercentage})

                # Show the frame of video on the screen
                cv2.imshow('Video', frame)

                # Hit 'q' to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                

            # Clean up everything when finished 
        
            time.sleep(10)
            video_capture.release()
            cv2.destroyAllWindows() 
    
    DataPush(LotName,CalculatedUseData)  
