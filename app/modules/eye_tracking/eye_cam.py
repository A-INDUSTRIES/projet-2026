import cv2
from cv2_enumerate_cameras import enumerate_cameras

eye = 0
front = 0

for camera_info in enumerate_cameras():
    print(f'Camera: {camera_info.name}, Path: {camera_info.path}, Index: {camera_info.index}')
    if "vid_0c45" in camera_info.path:
        eye = camera_info.index
    if "vid_058f" in camera_info.path:
        front = camera_info.index

# Initialize webcam
cap = cv2.VideoCapture(front)

while True:
    ret, frame = cap.read()
    cv2.imshow('Video Feed', frame)
    
    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()