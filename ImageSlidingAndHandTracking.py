from HandTrackingModule import HandDetector
import cv2
import os

def gen_video_frames_main():
    # Parameters
    width, height = 1280, 720
    folderPath = "video_presentation"
    
    # Video Files
    videoPaths = sorted([os.path.join(folderPath, vid) for vid in os.listdir(folderPath)], key=len)
    videoIndex = 0

    # Hand Detector
    detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

    # Variables
    annotations = [[]]
    annotationNumber = -1
    annotationStart = False
    drawMode = False
    delay = 30
    buttonPressed = False
    counter = 0

    while True:
        # Load the current video
        cap = cv2.VideoCapture(videoPaths[videoIndex])
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break  # Move to the next video if the current one ends

            frame = cv2.resize(frame, (width, height))
            frame = cv2.flip(frame, 1)

            # Hand Gesture Detection
            hands, img = detectorHand.findHands(frame)  # Detect hands in frame

            if hands and not buttonPressed:
                hand = hands[0]
                lmList = hand["lmList"]  # List of 21 Landmark points
                fingers = detectorHand.fingersUp(hand)  # List of which fingers are up
                indexFinger = lmList[8][0], lmList[8][1]

                # Go to prev video if thumb is shown
                if fingers == [1, 0, 0, 0, 0]:
                    buttonPressed = True
                    videoIndex = max(0, videoIndex - 1)
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                    break

                # Go to next video if last finger is shown
                if fingers == [0, 0, 0, 0, 1]:
                    buttonPressed = True
                    videoIndex = min(len(videoPaths) - 1, videoIndex + 1)
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
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

                # Undo annotation with 3 fingers
                if fingers == [0, 1, 1, 1, 0]:
                    if annotations:
                        annotations.pop(-1)
                        annotationNumber -= 1
                        buttonPressed = True

            # Draw Annotations
            for annotation in annotations:
                for i in range(1, len(annotation)):
                    cv2.line(frame, annotation[i - 1], annotation[i], (0, 0, 255), 12)

            # Manage button press delay
            if buttonPressed:
                counter += 1
                if counter > delay:
                    counter = 0
                    buttonPressed = False

            # Encode and yield the frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frameImage = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frameImage + b'\r\n')

        cap.release()
