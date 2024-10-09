from HandTrackingModule import HandDetector
import cv2
import os
import numpy as np
import dlib

def gen_frames_main():
    # Parameters
    width, height = 1280, 720
    folderPath = "Presentation"
    
    # Camera Setup
    cap = cv2.VideoCapture(0)
    cap.set(4, width)
    cap.set(5, height)

    # Hand Detector
    detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

    # Face Detector Setup
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    rotation_threshold = 10  # degrees for left and right rotation
    
    # Doubly Linked List class for image nodes
    class ImageNode:
        def __init__(self, imgNumber):
            self.imgNumber = imgNumber
            self.next = None
            self.prev = None

    def insertIntoDLL(head, data):
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
        head = insertIntoDLL(head, item)
        
    current_imgNumber_node = head
    currImageNumber = current_imgNumber_node.imgNumber

    # Variables
    imgList = []
    delay = 30
    buttonPressed = False
    counter = 0
    drawMode = False
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

        # Hand Gesture Detection
        hands, img = detectorHand.findHands(img)  # with draw

        if hands and buttonPressed is False:  # If hand is detected
            hand = hands[0]
            lmList = hand["lmList"]  # List of 21 Landmark points
            fingers = detectorHand.fingersUp(hand)  # List of which fingers are up
            indexFinger = lmList[8][0], lmList[8][1]

            # Go to prev slide if thumb is shown
            if fingers == [1, 0, 0, 0, 0]:
                buttonPressed = True
                if current_imgNumber_node.prev is not None:
                    current_imgNumber_node = current_imgNumber_node.prev
                    currImageNumber = current_imgNumber_node.imgNumber
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                    
            # Go to next slide if pinky is shown
            if fingers == [0, 0, 0, 0, 1]:
                buttonPressed = True
                if current_imgNumber_node.next is not None:
                    current_imgNumber_node = current_imgNumber_node.next
                    currImageNumber = current_imgNumber_node.imgNumber
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False

            # Drawing Mode with two fingers
            if fingers == [0, 1, 1, 0, 0]:
                cv2.circle(imgCurrent, indexFinger, 12, (0, 255, 255), cv2.FILLED)

            # Annotating
            if fingers == [0, 1, 0, 0, 0]:
                if annotationStart is False:
                    annotationStart = True
                    annotationNumber += 1
                    annotations.append([])
                annotations[annotationNumber].append(indexFinger)
                cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            else:
                annotationStart = False

            # Undo annotation with 3 fingers
            if fingers == [0, 1, 1, 1, 0]:
                if annotations:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True

        else:
            annotationStart = False

        # Manage button press delay
        if buttonPressed:
            counter += 1
            if counter > delay:
                counter = 0
                buttonPressed = False

        # Draw Annotations
        for i, annotation in enumerate(annotations):
            for j in range(len(annotation)):
                if j != 0:
                    cv2.line(imgCurrent, annotation[j - 1], annotation[j], (0, 0, 200), 12)

        # Display Hand Gesture in small corner window
        imgSmall = cv2.resize(img, (ws, hs))
        h, w, _ = imgCurrent.shape
        imgCurrent[0:hs, w - ws: w] = imgSmall

        # Face Rotation Detection code
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        for face in faces:
            landmarks = predictor(gray, face)

            left_eye = landmarks.part(36)
            right_eye = landmarks.part(45)

            dx = right_eye.x - left_eye.x
            dy = right_eye.y - left_eye.y
            angle = np.degrees(np.arctan2(dy, dx))

            rotation_direction = "Centered"
            if angle < -rotation_threshold:
                #left rotate means you are tring to go next slides
                rotation_direction = "Left Rotated"
                if current_imgNumber_node.next is not None:
                    current_imgNumber_node = current_imgNumber_node.next
                    currImageNumber = current_imgNumber_node.imgNumber
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
            if angle > rotation_threshold:
                #right rotate means you are trying to go previous slides
                rotation_direction = "Right Rotated"
                if current_imgNumber_node.prev is not None:
                    current_imgNumber_node = current_imgNumber_node.prev
                    currImageNumber = current_imgNumber_node.imgNumber
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False

            cv2.putText(imgCurrent, rotation_direction, (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Encode and yield the final frame
        ret1, buffer1 = cv2.imencode('.jpg', imgCurrent)
        frameImage = buffer1.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frameImage + b'\r\n')
