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
    delay = 30
    buttonPressed = False
    counter = 0
    ws, hs = int(120 * 1), int(213 * 1)  # Width and height of small image

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

            if hands:
                # Creating a small window showing the frame with hand annotations
                hand_frame = frame.copy()  # Optional: process separately for hand visuals
                imgSmall = cv2.resize(hand_frame, (ws, hs))  # Resize the hand frame to a small window
                h, w, _ = frame.shape

                # Overlay the small image at the top-right corner
                frame[0:hs, w - ws:w] = imgSmall  # Place in the top-right corner

            # Encode and yield the frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frameImage = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frameImage + b'\r\n')

            # Reset button press delay
            if buttonPressed:
                counter += 1
                if counter > delay:
                    counter = 0
                    buttonPressed = False

            # End of inner video loop
        cap.release()

        # Optional: Display frame for debugging
        cv2.imshow("Video with Hand Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break
    cv2.destroyAllWindows()

