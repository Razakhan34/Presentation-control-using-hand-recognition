from HandTrackingModule import HandDetector
import cv2
import os
import numpy as np

def gen_video_frames_main():
    # Parameters
    width, height = 1280, 720
    folderPath = "video_presentation"
    
    # Video Files
    videoPaths = sorted([os.path.join(folderPath, vid) for vid in os.listdir(folderPath)], key=len)
    videoIndex = 0
    
    # Camera Setup
    img_cap = cv2.VideoCapture(0)
    img_cap.set(4, width)
    img_cap.set(5, height)

    # Hand Detector
    detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

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

    # Initialize the video capture for the first video
    cap = cv2.VideoCapture(videoPaths[videoIndex])
    if not cap.isOpened():
        print("Error: Cannot open video file")
        return

    isPlaying = True  # Flag to track play/pause state

    while True:
        # Get image frame
        success, img = img_cap.read()
        img = cv2.flip(img, 1)

        if isPlaying:
            # Read the video frame if playing
            success, frame = cap.read()
            if not success:  # If the video ends, go to the next one
                videoIndex = (videoIndex + 1) % len(videoPaths)  # Loop through videos
                cap.release()  # Release the current video capture
                cap = cv2.VideoCapture(videoPaths[videoIndex])  # Open the next video
                if not cap.isOpened():
                    print("Error: Cannot open next video file")
                    break
        else:
            # If paused, show the last frame
            frame = cv2.resize(frame, (width, height))

        frame = cv2.resize(frame, (width, height))

        # Hand Gesture Detection
        hands, img = detectorHand.findHands(img)  # Detect hands in frame

        if hands and buttonPressed is False:  # If hand is detected
            hand = hands[0]
            lmList = hand["lmList"]  # List of 21 Landmark points
            fingers = detectorHand.fingersUp(hand)  # List of which fingers are up

            indexFinger = lmList[8][0], lmList[8][1]

            # Play/Pause Gesture - Peace sign (index and middle fingers up)
            if fingers == [0, 0, 1, 1, 1]:
                isPlaying = not isPlaying  # Toggle play/pause
                buttonPressed = True
                
            # Forward 5 seconds if four fingers are up
            if fingers == [0, 1, 1, 1, 1]:
                buttonPressed = True
                current_position = cap.get(cv2.CAP_PROP_POS_MSEC)  # Get current position in milliseconds
                cap.set(cv2.CAP_PROP_POS_MSEC, current_position + 5000)  # Move forward by 5000 ms (5 seconds)

            # Rewind 5 seconds if all five fingers are up
            if fingers == [1, 1, 1, 1, 1]:
                buttonPressed = True
                current_position = cap.get(cv2.CAP_PROP_POS_MSEC)  # Get current position in milliseconds
                new_position = max(0, current_position - 5000)  # Move back by 5000 ms (ensure it doesn't go negative)
                cap.set(cv2.CAP_PROP_POS_MSEC, new_position)


            # Go to prev video if thumb is shown
            if fingers == [1, 0, 0, 0, 0]:
                buttonPressed = True
                videoIndex = max(0, videoIndex - 1)
                annotations = [[]]
                annotationNumber = -1
                annotationStart = False
                cap.release()  # Release the current video capture
                cap = cv2.VideoCapture(videoPaths[videoIndex])  # Open the new video
                if not cap.isOpened():
                    print("Error: Cannot open previous video file")
                    break

            # Go to next video if last finger is shown
            if fingers == [0, 0, 0, 0, 1]:
                buttonPressed = True
                videoIndex = min(len(videoPaths) - 1, videoIndex + 1)
                annotations = [[]]
                annotationNumber = -1
                annotationStart = False
                cap.release()  # Release the current video capture
                cap = cv2.VideoCapture(videoPaths[videoIndex])  # Open the new video
                if not cap.isOpened():
                    print("Error: Cannot open next video file")
                    break

            # Annotating with index finger
            if fingers == [0, 1, 0, 0, 0]:
                if annotationStart is False:
                    annotationStart = True
                    annotationNumber += 1
                    annotations.append([]) 
                annotations[annotationNumber].append(indexFinger)
                cv2.circle(frame, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            else:
                annotationStart = False

            if fingers == [0, 1, 1, 0, 0]:
                cv2.circle(frame, indexFinger, 12, (0, 255, 255), cv2.FILLED)

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
                    cv2.line(frame, annotation[j - 1], annotation[j], (0, 0, 200), 12)

        # Overlay small window with hand gesture frame in top-right corner
        imgSmall = cv2.resize(img, (ws, hs))
        h, w, _ = frame.shape
        frame[0:hs, w - ws: w] = imgSmall

        # Encode and yield the frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frameImage = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frameImage + b'\r\n') 
