from HandTrackingModule import HandDetector
import cv2
import os
import numpy as np

def gen_frames_main():
    # Parameters
    width, height = 1280, 720
    #gestureThreshold = 300
    folderPath = "Presentation"

    # Camera Setup
    cap = cv2.VideoCapture(0)
    cap.set(4, width)
    cap.set(5, height)

    # Hand Detector
    detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

    # defining doubly linked list class
    class ImageNode:
        def __init__(self, imgNumber):
            self.imgNumber = imgNumber
            self.next = None
            self.prev = None


    def insertIntoDLL(head,data):
        new_node = ImageNode(data)
        if head is None:
            head = new_node
        else:
            current = head
            while current.next:
                current = current.next
            current.next = new_node
            new_node.prev = current
        return head 

    # Initialize doubly linked list for images
    head = None
    total_images = len(os.listdir(folderPath))
    for item in range(total_images):
        head = insertIntoDLL(head,item)
        
    current_imgNumber_node = head
    currImageNumber = current_imgNumber_node.imgNumber


    # Variables
    imgList = []
    delay = 30
    buttonPressed = False
    counter = 0
    drawMode = False
    # imgNumber = 0
    delayCounter = 0
    annotations = [[]]
    annotationNumber = -1
    annotationStart = False
    hs, ws = int(120 * 1), int(213 * 1)  # width and height of small image

    # Get list of presentation images
    pathImages = sorted(os.listdir(folderPath), key=len)

    while True:
        # Get image frame
        success, img = cap.read()
        img = cv2.flip(img, 1)
        pathFullImage = os.path.join(folderPath, pathImages[currImageNumber])
        imgCurrent = cv2.imread(pathFullImage)

        # Find the hand and its landmarks
        hands, img = detectorHand.findHands(img)  # with draw
        # Draw Gesture Threshold line
        #cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

        if hands and buttonPressed is False:  # If hand is detected
            hand = hands[0]
            cx, cy = hand["center"]
            lmList = hand["lmList"]  # List of 21 Landmark points
            fingers = detectorHand.fingersUp(hand)  # List of which fingers are up

            # #  Constrain values for easier drawing
            # xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
            # yVal = int(np.interp(lmList[8][1], [150, height-150], [0, height]))
            # print(xVal,yVal)
            indexFinger = lmList[8][0],lmList[8][1]
            
            

            #if cy <= gestureThreshold:  # If hand is at the height of the face (optional features)
            # Go to prev slide if thumb shown
            if fingers == [1, 0, 0, 0, 0]:
                # print("Left")
                buttonPressed = True
                if current_imgNumber_node.prev is not None:
                    current_imgNumber_node = current_imgNumber_node.prev
                    currImageNumber = current_imgNumber_node.imgNumber
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                    
            # Go to next slide if last finger shown  shown
            if fingers == [0, 0, 0, 0, 1]:
                # print("Right")
                buttonPressed = True
                if current_imgNumber_node.next is not None:
                    current_imgNumber_node = current_imgNumber_node.next
                    currImageNumber = current_imgNumber_node.imgNumber
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False

            if fingers == [0, 1, 1, 0, 0]:
                cv2.circle(imgCurrent, indexFinger, 12, (0, 255, 255), cv2.FILLED)
                
            # if fingers == [1,1,1,1,1]:
            #     break
            
            if fingers == [0, 1, 0, 0, 0]:
                if annotationStart is False:
                    annotationStart = True
                    annotationNumber += 1
                    annotations.append([])
                # print(annotationNumber)
                annotations[annotationNumber].append(indexFinger)
                cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)

            else:
                annotationStart = False

            if fingers == [0, 1, 1, 1, 0]:
                if annotations:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True

        else:
            annotationStart = False

        if buttonPressed:
            counter += 1
            if counter > delay:
                counter = 0
                buttonPressed = False

        for i, annotation in enumerate(annotations):
            for j in range(len(annotation)):
                if j != 0:
                    cv2.line(imgCurrent, annotation[j - 1], annotation[j], (0, 0, 200), 12)

        imgSmall = cv2.resize(img, (ws, hs))
        h, w, _ = imgCurrent.shape
        imgCurrent[0:hs, w - ws: w] = imgSmall
        
        ret1, buffer1 = cv2.imencode('.jpg', imgCurrent)
        frameImage = buffer1.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frameImage + b'\r\n')

        # cv2.imshow("Slides", imgCurrent)
        # cv2.imshow("Image", img)

        # key = cv2.waitKey(1)
        # if key == ord('q'):
        #     break