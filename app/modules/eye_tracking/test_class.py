import cv2
import cv2.aruco as aruco
import numpy as np
from cv2_enumerate_cameras import enumerate_cameras
from threading import Thread
from ..utils import Singleton
from ..logger import error, debug, warn

class EyeTracking(metaclass=Singleton):
    def __init__(self, screen_width=1920, screen_height=1080):
        self.listeners = []

        # External camera / screen params (for 640x480)
        self.EXT_WIDTH = screen_width
        self.EXT_HEIGHT = screen_height
        self.EXT_CX = self.EXT_WIDTH // 2
        self.EXT_CY = self.EXT_HEIGHT // 2

        self.marker_size = 150 # Taille en pixels, donc pas trop grands ig
        self.aruco_static_corners = np.array([
            (self.marker_size//2, self.marker_size//2),
            (self.EXT_WIDTH - self.marker_size//2, self.marker_size//2),
            (self.EXT_WIDTH - self.marker_size//2, self.EXT_HEIGHT - self.marker_size//2),
            (self.marker_size//2, self.EXT_HEIGHT - self.marker_size//2)
        ], dtype=np.float32)
        self.Hom_gaze_to_cam = None

        self.prev_darkest_point = None

        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.aruco_params = aruco.DetectorParameters()
        self.aruco_detector = aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        self.aruco_markers_centers = None
        self.calib_gaze_pts = []
        self.calib_cam_corners = []

        # Pour essayer de faire une collecte mutliple des points à la calibration et faire une moyenne
        self.is_collecting = False
        self.collecting_frames_count = 0
        self.max_calib_frames = 30
        self.current_step_gaze_buffer = []
        self.current_step_cam_buffer = []

        self.calibration_step = 0

        # For the calibration process and to smoothen the way the red circle "jitters" right now
        self.smoothed_u = None
        self.smoothed_v = None

        # Un offset pour essayer de recalibrer de temps en temps
        # Au début = 0 pour ne rien corriger, sauf si on le demande
        self.offset_x = 0
        self.offset_y = 0

    def crop_to_aspect_ratio(self, image, width=640, height=480):
        current_height, current_width = image.shape[:2]
        current_ratio = current_width / current_height
        
        desired_ratio = width / height

        if current_ratio > desired_ratio:
            # Current image is too wide
            new_width = int(desired_ratio * current_height)
            offset = (current_width - new_width) // 2
            cropped_img = image[:, offset:offset + new_width]
        else:
            # Current image is too tall
            new_height = int(current_width / desired_ratio)
            offset = (current_height - new_height) // 2
            cropped_img = image[offset:offset + new_height, :]

        return cv2.resize(cropped_img, (width, height))
    
    def get_aruco_markers_centers(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.aruco_detector.detectMarkers(gray_frame)
        # print(f"ids : {ids}") # debug
        
        if ids is not None: #q and len(ids) >= 4:
            found_ids = ids.flatten()
            points = {}
            
            if len(found_ids) > 0 and len(found_ids) < 4:
                debug(f"Seulement {len(found_ids)} marqueur(s) vu(s) : {found_ids}")

            for i, marker_id in enumerate(found_ids):
                # Moyenne des coordonnées des 4 sommets pour avoir le centre de chaque marqueurs
                # Sinon on pourrait prendre le coin supérieur gauche pour celui en haut à gauche etc
                # Mais azy au moins ça fait une seule boucle ig
                corners_i = corners[i][0]
                marker_center = (np.mean(corners_i[:,0]), np.mean(corners_i[:,1]))
                points[marker_id] = marker_center
                
            if all(i in points for i in [0, 1, 2, 3]):
                return np.array([points[0], points[1], points[2], points[3]])
            else:
                warn(f"4 marqueurs non detectes (IDs trouves : {found_ids}).")
                
        return None

    def calibrate_step(self, frame):
        cam_corners = self.get_aruco_markers_centers(frame)
        if cam_corners is None or self.prev_darkest_point is None: return

        pupil_2D = (float(self.prev_darkest_point[0]), float(self.prev_darkest_point[1]))
        
        self.current_step_gaze_buffer.append(pupil_2D)
        self.current_step_cam_buffer.append(cam_corners[self.calibration_step])
        self.collecting_frames_count += 1
        
        # Si on dépasse le nombre de frames demandées pour avoir une moyenne correcte, on calibre
        if self.collecting_frames_count >= self.max_calib_frames:
            avg_gaze = np.mean(self.current_step_gaze_buffer, axis=0)
            avg_cam = np.mean(self.current_step_cam_buffer, axis=0)
            
            self.calib_gaze_pts.append(avg_gaze)
            self.calib_cam_corners.append(avg_cam)
        
            print(f"Point {self.calibration_step+1}/4 capturé : {self.calib_gaze_pts}") # debug
            print(f"{self.collecting_frames_count} points utilisés.") # debug
            
            # reset du compteur de frames pour la calibrtion à 0
            self.is_collecting = False
            self.collecting_frames_count = 0
            self.current_step_cam_buffer = []
            self.current_step_gaze_buffer = []
            self.calibration_step = -1

        if len(self.calib_gaze_pts) == 4 and not self.calibrated:
            # Là on fait homographie entre regard et caméra frontale
            src = np.array(self.calib_gaze_pts, dtype=np.float32)
            dst = np.array(self.calib_cam_corners, dtype=np.float32)
            self.Hom_gaze_to_cam, _ = cv2.findHomography(src, dst)
            print(self.Hom_gaze_to_cam)
            
            self.calibrated = True

    # Finds the pupil in an individual frame and returns the center point
    def process_frame(self, frame):
        frame = cv2.GaussianBlur(frame, (5,5), 0)
        # Crop and resize frame
        frame = self.crop_to_aspect_ratio(frame)

        #find the darkest point
        darkest_point = (0, 0)

        # Convert to grayscale to handle pixel value operations
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (9, 9), 0)
        
        (_, _, minLoc, _) = cv2.minMaxLoc(gray_frame)
        new_darkest = minLoc
        
        if self.prev_darkest_point is None:
            darkest_point = new_darkest
        else:
            alpha = 0.2
            darkest_point = (
                int(alpha * new_darkest[0] + (1 - alpha) * self.prev_darkest_point[0]),
                int(alpha * new_darkest[1] + (1 - alpha) * self.prev_darkest_point[1])
            )
            
        self.prev_darkest_point = darkest_point

    # Process video from the selected eye camera + external camera preview
    def process_camera(self, eye_cam, front_cam):
        # ---- Eye camera (existing) ----
        eye_cap = cv2.VideoCapture(eye_cam)
        if not eye_cap.isOpened():
            error(f"Could not open eye camera at index {eye_cam}.")
            return

        # ---- External camera (new) ----
        external_cap = cv2.VideoCapture(front_cam)
        if not external_cap.isOpened():
            error(f"Could not open external camera at index {front_cam}.")
        
        external_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.EXT_WIDTH)
        external_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.EXT_HEIGHT)
        debug(f"External camera opened at index {front_cam} ({self.EXT_WIDTH}x{self.EXT_HEIGHT}).")

        # Initial red circle at center (for calibration)
        self.circle_x, self.circle_y = self.EXT_CX, self.EXT_CY
        self.calibrated = False

        while self.running:
            # ----- Eye camera frame -----
            ret_eye, eye_frame = eye_cap.read()
            if not ret_eye:
                error("Failed to read frame from eye camera.")
                break

            # Flip + process for ellipse / gaze vector
            #eye_frame_flipped = cv2.flip(eye_frame, 0)
            self.process_frame(eye_frame)  # this updates last_gaze_dir via compute_gaze_vector

            # ----- External camera frame -----
            ret_ext, ext_frame = external_cap.read()
            if not ret_ext:
                error("Failed to read frame from front camera.")
                break
            
            ext_frame_resized = cv2.resize(ext_frame, (self.EXT_WIDTH, self.EXT_HEIGHT))
            current_cam_corners = self.get_aruco_markers_centers(ext_frame_resized)
            
            # --- LIGNE DE DEBUG À DÉCOMMENTER POUR VOIR CE QUE LA CAMÉRA VOIT ---
            # cv2.imshow("Debug Camera Externe", ext_frame_resized)
            
            if self.is_collecting and self.calibration_step < 4 and not self.calibration_step == -1:
                self.calibrate_step(ext_frame_resized)
            
            # Renvoie None si pas 4 markers détectés
            if self.calibrated and current_cam_corners is not None and self.prev_darkest_point is not None:
                
                pupil_point = np.array([[[float(self.prev_darkest_point[0]), float(self.prev_darkest_point[1])]]], dtype=np.float32)
                point_in_cam = cv2.perspectiveTransform(pupil_point, self.Hom_gaze_to_cam)[0][0]
                
                # Homographie entre les point détectés par la caméra frontales (markers) et les coordonnées statiques des markers
                H_cam_to_screen, _ = cv2.findHomography(current_cam_corners, self.aruco_static_corners)
                
                # Et projection finale du regard sur l'écran
                point_in_cam_2 = np.array([[[point_in_cam[0], point_in_cam[1]]]], dtype=np.float32)
                point_on_screen = cv2.perspectiveTransform(point_in_cam_2, H_cam_to_screen)[0][0]
                
                u, v = point_on_screen[0], point_on_screen[1]
                
                if self.smoothed_u is None:
                    self.smoothed_u, self.smoothed_v = u, v
                else:
                    alpha = 0.1
                    self.smoothed_u = alpha * u + (1 - alpha) * self.smoothed_u
                    self.smoothed_v = alpha * v + (1 - alpha) * self.smoothed_v
                
                u_offset = self.smoothed_u + self.offset_x
                v_offset = self.smoothed_v + self.offset_y
                    
                self.circle_x = int(np.clip(u_offset, 0, self.EXT_WIDTH - 1))
                self.circle_y = int(np.clip(v_offset, 0, self.EXT_HEIGHT - 1))

                for listener in self.listeners:
                    listener((self.circle_x, self.circle_y))
            else:
                pass
                # warn("Marqueurs ArUco non detectes")

            # # ----- Key controls -----
            # key = cv2.waitKey(1) & 0xFF
            # if key == ord('q'):
            #     break
            # elif key == ord(' '):
            #     # Pause until another key press
            #     cv2.waitKey(0)
            # elif key == ord('c') and self.calibration_step < 4:
            #     # print("AIZUHDIUAHZDIUHAZODIUHAOZHDOAZIHUD") # debug (je pète un cable)
            #     # Calibrate so current gaze ray hits the center of the external screen
            #     if not self.is_collecting:
            #         print(f"Démarrage calibration {self.calibration_step}")
            #         self.is_collecting = True
            #     #calibrate_gaze_to_external() (celle là est rendue inutile par l'homographie mais je la garde au cas où on sait jamais)
            # elif key == ord('o'):
            #     # Essayer de recalibrer le truc par rapport à un offset en regardant au centre de l'écran 
            #     # A utiliser quand le point rouge se décale un peu trop de la réalité
            #     self.offset_x = self.EXT_WIDTH // 2 - self.circle_x
            #     self.offset_y = self.EXT_HEIGHT // 2 - self.circle_y
            # elif key == ord('r'):
            #     self.smoothed_u, self.smoothed_v = None, None # Au cas où ça foire en regardant or écran / valeur trop (pas devoir relancer l'app, jsp)
            #     self.offset_x, self.offset_y = 0, 0 # comme ça on reset tout du'un coup

        # Cleanup
        eye_cap.release()
        if external_cap is not None:
            external_cap.release()
        cv2.destroyAllWindows()

    def _run(self):
        eye = None
        front = None

        for camera_info in enumerate_cameras():
            if 0xc45 == camera_info.vid:
                eye = camera_info.index
            if 0x58f == camera_info.vid:
                front = camera_info.index

        if not eye:
            error("Eye camera not found")
            return
        if not front:
            error("Front camera not found")
            return
                
        self.process_camera(eye, front)

    # Fonctions liées à l'app directement
    def calibratePoint(self, index):
        # Calibre un point unique donné par son indexe
        if index == 0:
            self.calib_gaze_pts = []
            self.calib_cam_corners = []
            self.calibrated = False
        self.calibration_step = index
        self.is_collecting = True

    def connect(self, callback):
        # Listener vers eyeEvent
        self.listeners.append(callback)

    def stop(self):
        # Stop thread
        self.running = False
        self.thread.join()

    def run(self):
        # Start thread
        self.running = True
        self.thread = Thread(target=self._run)
        self.thread.start()

if __name__ == "__main__":
    tracker = EyeTracking()
    tracker._run()