import cv2
from cv2_enumerate_cameras import enumerate_cameras

eye = 0
front = 0

for camera_info in enumerate_cameras():
    print(f'Camera: {camera_info.name}, VID: {camera_info.vid}, Index: {camera_info.index}')
    if 0xc45 == camera_info.vid:
        eye = camera_info.index
    if 0x58f == camera_info.vid:
        front = camera_info.index
        
