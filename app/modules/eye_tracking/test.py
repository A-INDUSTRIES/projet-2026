import cv2
import cv2.aruco as aruco
import numpy as np

# External camera / screen params (for 640x480)
EXT_WIDTH = 1920
EXT_HEIGHT = 1080
EXT_CX = EXT_WIDTH // 2
EXT_CY = EXT_HEIGHT // 2

marker_size = 100 # Taille en pixels, donc pas trop grands ig
aruco_static_corners = np.array([
    (50, 50),
    (EXT_WIDTH - 50, 50),
    (EXT_WIDTH - 50, EXT_HEIGHT - 50),
    (50, EXT_HEIGHT - 50)
], dtype=np.float32)
Hom_gaze_to_cam = None

max_calib_frames = 20

prev_darkest_point = None

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
aruco_params = aruco.DetectorParameters()
aruco_detector = aruco.ArucoDetector(aruco_dict, aruco_params)
aruco_markers_centers = None
M_homography_screen = None
calib_gaze_pts = []
calib_cam_corners = []

# Pour essayer de faire une collecte mutliple des points à la calibration et faire une moyenne
is_collecting = False
collecting_frames_count = 0
max_calib_frames = 20
current_step_gaze_buffer = []
current_step_cam_buffer = []

calibration_step = 0

# For the calibration process and to smoothen the way the red circle "jitters" right now
smoothed_u = None
smoothed_v = None

# Un offset pour essayer de recalibrer de temps en temps
# Au début = 0 pour ne rien corriger, sauf si on le demande
offset_x = 0
offset_y = 0

# Crop the image to maintain a specific aspect ratio (width:height) before resizing.
def crop_to_aspect_ratio(image, width=640, height=480):
    current_height, current_width = image.shape[:2]
    desired_ratio = width / height
    current_ratio = current_width / current_height

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

def get_aruco_markers_centers(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = aruco_detector.detectMarkers(gray_frame)
    # print(f"ids : {ids}") # debug
    
    if ids is not None: #q and len(ids) >= 4:
        found_ids = ids.flatten()
        points = {}
        for i, marker_id in enumerate(found_ids):
            # Moyenne des coordonnées des 4 sommets pour avoir le centre de chaque marqueurs
            # Sinon on pourrait prendre le coin supérieur gauche pour celui en haut à gauche etc
            # Mais azy au moins ça fait une seule boucle ig
            corners_i = corners[i][0]
            marker_center = (np.mean(corners_i[:,0]), np.mean(corners_i[:,1]))
            points[marker_id] = marker_center
            
        if all(i in points for i in [0, 1, 2, 3]):
            return np.array([points[0], points[1], points[2], points[3]])
    
    return None

# Pour dessiner la frame sur laquelle afficher les marqueurs ArUco (sur fond blanc pour avoir gros contraste car ArUco noirs)
def draw_screen():
    canvas = np.ones((EXT_HEIGHT, EXT_WIDTH, 3), dtype=np.uint8) * 255
    
    positions = [
        (0, 0),
        (0, EXT_WIDTH - marker_size),
        (EXT_HEIGHT - marker_size, EXT_WIDTH - marker_size),
        (EXT_HEIGHT - marker_size, 0)
    ]
    
    for marker_id, (row, col) in enumerate(positions):
        marker = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size - 30)
        
        padding = cv2.copyMakeBorder(marker, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255)
        background_with_padding = cv2.cvtColor(padding, cv2.COLOR_GRAY2BGR)
        
        canvas[row:row+marker_size, col:col+marker_size] = background_with_padding
        
    return canvas

def calibrate_step(frame):
    global calibration_step, calib_gaze_pts, calib_cam_corners, Hom_gaze_to_cam, calibrated
    global is_collecting, current_step_gaze_buffer, current_step_cam_buffer, collecting_frames_count

    # if last_gaze_dir is None: return
    
    cam_corners = get_aruco_markers_centers(frame)
    if cam_corners is None: return

    # Abandon du code du type sur Github pour remplacer par homographie avec seulement l'estimation de la pupille en 2D
    # Je deviens fou ? Je pleure en direct ?
    ## print("JE SUIS ICI HAHAHAHAHHAAHAHAHAAH"*10) # debug
    #gz = last_gaze_dir[2]
    #if abs(gz) < 1e-6: return
    
    ## Projection 2D du regard => stockée dans le vecteur qui sert à faire homographie quand étape 4
    #gaze_proj = (last_gaze_dir[0]/gz, last_gaze_dir[1]/gz)
    #current_step_gaze_buffer.append(gaze_proj)
    #current_step_cam_buffer.append(cam_corners[calibration_step])
    #collecting_frames_count += 1
    
    pupil_2D = (float(prev_darkest_point[0]), float(prev_darkest_point[1]))
    
    current_step_gaze_buffer.append(pupil_2D)
    current_step_cam_buffer.append(cam_corners[calibration_step])
    collecting_frames_count += 1
    
    # Si on dépasse le nombre de frames demandées pour avoir une moyenne correcte, on calibre
    if collecting_frames_count >= max_calib_frames:
        avg_gaze = np.mean(current_step_gaze_buffer, axis=0)
        avg_cam = np.mean(current_step_cam_buffer, axis=0)
        
        calib_gaze_pts.append(avg_gaze)
        calib_cam_corners.append(avg_cam)
    
        print(f"Point {calibration_step+1}/4 capturé : {calib_gaze_pts}") # debug
        print(f"{collecting_frames_count} points utilisés.") # debug
        
        # reset du compteur de frames pour la calibrtion à 0
        is_collecting = False
        collecting_frames_count = 0
        current_step_cam_buffer = []
        current_step_gaze_buffer = []
        calibration_step += 1

    if calibration_step == 4:
        # Là on fait homographie entre regard et caméra frontale
        # print("JE FAIS LA MATRICE LA"*100) # debug
        src = np.array(calib_gaze_pts, dtype=np.float32)
        dst = np.array(calib_cam_corners, dtype=np.float32)
        Hom_gaze_to_cam, _ = cv2.findHomography(src, dst)
        print(Hom_gaze_to_cam)
        
        calibrated = True

# Finds the pupil in an individual frame and returns the center point
def process_frame(frame):
    global prev_darkest_point
    frame = cv2.GaussianBlur(frame, (5,5), 0)
    # Crop and resize frame
    frame = crop_to_aspect_ratio(frame)

    #find the darkest point
    darkest_point = (0, 0)

    # Convert to grayscale to handle pixel value operations
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (9, 9), 0)
    darkest_pixel_value = gray_frame[darkest_point[1], darkest_point[0]]
    
    (_, _, minLoc, _) = cv2.minMaxLoc(gray_frame)
    new_darkest = minLoc
    
    if prev_darkest_point is None:
        darkest_point = new_darkest
    else:
        alpha = 0.2
        darkest_point = (
            int(alpha * new_darkest[0] + (1 - alpha) * prev_darkest_point[0]),
            int(alpha * new_darkest[1] + (1 - alpha) * prev_darkest_point[1])
        )
        
    prev_darkest_point = darkest_point

# Process video from the selected eye camera + external camera preview
def process_camera(eye_cam, front_cam):
    global selected_camera, circle_x, circle_y, calibrated, smoothed_u, smoothed_v

    # ---- Eye camera (existing) ----
    eye_cap = cv2.VideoCapture(eye_cam)
    if not eye_cap.isOpened():
        print(f"Error: Could not open eye camera at index {eye_cam}.")
        return

    # ---- External camera (new) ----
    external_cap = cv2.VideoCapture(front_cam)

    if external_cap.isOpened():
        external_cap.set(cv2.CAP_PROP_FRAME_WIDTH, EXT_WIDTH)
        external_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, EXT_HEIGHT)
        print(f"External camera opened at index {front_cam} ({EXT_WIDTH}x{EXT_HEIGHT}).")
    else:
        print(f"Warning: Could not open external camera at index {front_cam}.")
        external_cap = None

    # Initial red circle at center (for calibration)
    circle_x, circle_y = EXT_CX, EXT_CY
    calibrated = False

    # Make sure the eye-frame window exists and hook mouse callback
    # cv2.namedWindow("Frame with Ellipse and Rays")
    # cv2.setMouseCallback("Frame with Ellipse and Rays", on_mouse_frame_with_rays)

    while True:
        cv2.namedWindow("Screen", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Screen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        screen = draw_screen()
        
        cv2.circle(screen, (EXT_CX, EXT_CY), 2, (0, 0, 0), -1)
        
        # ----- Eye camera frame -----
        ret_eye, eye_frame = eye_cap.read()
        if not ret_eye:
            print("Failed to read frame from eye camera.")
            break

        # Flip + process for ellipse / gaze vector
        #eye_frame_flipped = cv2.flip(eye_frame, 0)
        process_frame(eye_frame)  # this updates last_gaze_dir via compute_gaze_vector

        # ----- External camera frame -----
        if external_cap is not None:
            ret_ext, ext_frame = external_cap.read()
            if ret_ext:
                ext_frame_resized = cv2.resize(ext_frame, (EXT_WIDTH, EXT_HEIGHT))
                current_cam_corners = get_aruco_markers_centers(ext_frame_resized)
                
                global is_collecting
                if is_collecting and calibration_step < 4:
                    calibrate_step(ext_frame_resized)
                    
                # Afficher infos de collection
                if not calibrated and calibration_step < 4:
                    marker_target = aruco_static_corners[calibration_step]
                    
                    cv2.circle(screen, (int(marker_target[0]), int(marker_target[1])), 5, (0, 0, 255), -1)
                                        
                    if is_collecting:
                        cv2.putText(screen, "collection de frames", (EXT_WIDTH // 2 - 250, EXT_HEIGHT // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                        
                    else:
                        cv2.putText(screen, "Fixer le point rouge quelques instants et appuyez sur C", (EXT_WIDTH // 2 - 250, EXT_HEIGHT // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                
                # Renvoie None si pas 4 markers détectés
                if calibrated and current_cam_corners is not None and prev_darkest_point is not None:
                    # print("JE SUIS ICI HAHAHAHAHHAAHAHAHAAH") # debug
                    # print(f"Cam corners : {current_cam_corners}") # debug pour voir s'il y a bien 4 cam corners
                    # Tracer le contour estimé de l'écran ?
                    #cv2.polylines(ext_frame_resized, [aruco_markers_centers.astype(np.int32)], True, (0, 255, 0), 2)
                    
                    # J'abandonne la 3D pour tester avec juste la pupille 
                    ## D'abord homographie entre regard et caméra frontale
                    #gz = last_gaze_dir[2]
                    #gaze_proj_point = np.array([[[last_gaze_dir[0]/gz, last_gaze_dir[1]/gz]]], dtype=np.float32)
                    #point_in_cam = cv2.perspectiveTransform(gaze_proj_point, Hom_gaze_to_cam)[0][0]
                    
                    pupil_point = np.array([[[float(prev_darkest_point[0]), float(prev_darkest_point[1])]]], dtype=np.float32)
                    point_in_cam = cv2.perspectiveTransform(pupil_point, Hom_gaze_to_cam)[0][0]
                    
                    # Homographie entre les point détectés par la caméra frontales (markers) et les coordonnées statiques des markers
                    H_cam_to_screen, _ = cv2.findHomography(current_cam_corners, aruco_static_corners)
                    
                    # Et projection finale du regard sur l'écran
                    point_in_cam_2 = np.array([[[point_in_cam[0], point_in_cam[1]]]], dtype=np.float32)
                    point_on_screen = cv2.perspectiveTransform(point_in_cam_2, H_cam_to_screen)[0][0]
                    
                    u, v = point_on_screen[0], point_on_screen[1]
                    
                    if smoothed_u is None:
                        smoothed_u, smoothed_v = u, v
                    else:
                        alpha = 0.1
                        smoothed_u = alpha * u + (1 - alpha) * smoothed_u
                        smoothed_v = alpha * v + (1 - alpha) * smoothed_v
                    
                    global offset_x, offset_y
                    u_offset = smoothed_u + offset_x
                    v_offset = smoothed_v + offset_y
                        
                    circle_x = int(np.clip(u_offset, 0, EXT_WIDTH - 1))
                    circle_y = int(np.clip(v_offset, 0, EXT_HEIGHT - 1))
                        
                    cv2.circle(screen, (circle_x, circle_y), 10, (0, 0, 255), -1)
                        
                    
                    # Si c'est calibré, on calcule l'homographie dynamique de l'écran
                    #if calibrated:
                    #    M_homography_screen, _ = cv2.findHomography(np.array(calib_gaze_pts, dtype=np.float32), aruco_markers_centers)
                    #    
                    #    # Trouver position regard
                    #    gz = last_gaze_dir[2]
                    #    vec = np.array([[[last_gaze_dir[0]/gz, last_gaze_dir[1]/gz]]], dtype=np.float32)
                    #    
                    #    gaze_target = cv2.perspectiveTransform(vec, M_homography_screen)
                    #    u = gaze_target[0][0][0]
                    #    v = gaze_target[0][0][1]
                    #    
                    #    alpha = 0.15
                    #    
                    #    smoothed_u = alpha * u + (1 - alpha) * smoothed_u
                    #    smoothed_v = alpha * v + (1 - alpha) * smoothed_v
                    #    
                    #    circle_x = int(np.clip(smoothed_u, 0, EXT_WIDTH - 1))
                    #    circle_y = int(np.clip(smoothed_v, 0, EXT_HEIGHT - 1))
                    #    
                    #    #update_gaze_circle_from_current_gaze()

                    #    # Draw small red circle representing gaze on external view
                        
                else:
                    cv2.putText(screen, "Marqueurs ArUco non detectes", (EXT_CX//2, EXT_CY//2), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                #if not calibrated:
                #    # On récupère la cible actuelle
                #    target_pos = calib_points_screen[calibration_step]
                #    
                #    # Cercle vide pour la cible (extérieur) 
                #    cv2.circle(ext_frame_resized, target_pos, 10, (0, 255, 0), 2)
                #    # Cible = là où il faut regarder à chaque étape
                #    cv2.circle(ext_frame_resized, target_pos, 5, (0, 255, 0), -1)
                #    
                #    # Petit texte indicatif
                #    cv2.putText(ext_frame_resized, f"Regardez ici et appuyez sur 'C' ({calibration_step+1}/4)", 
                #            (target_pos[0]-50, target_pos[1]-30), 
                #            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                cv2.imshow("External Camera (Gaze)", ext_frame_resized)
                
            else:
                print("Failed to read frame from external camera.")
                
        cv2.imshow("Screen", screen)

        # ----- Key controls -----
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            # Pause until another key press
            cv2.waitKey(0)
        elif key == ord('c') and calibration_step < 4:
            # print("AIZUHDIUAHZDIUHAZODIUHAOZHDOAZIHUD") # debug (je pète un cable)
            # Calibrate so current gaze ray hits the center of the external screen
            if not is_collecting:
                print(f"Démarrage calibration {calibration_step}")
                is_collecting = True
            #calibrate_gaze_to_external() (celle là est rendue inutile par l'homographie mais je la garde au cas où on sait jamais)
        elif key == ord('o'):
            # Essayer de recalibrer le truc par rapport à un offset en regardant au centre de l'écran 
            # A utiliser quand le point rouge se décale un peu trop de la réalité
            offset_x = EXT_WIDTH // 2 - circle_x
            offset_y = EXT_HEIGHT // 2 - circle_y
        elif key == ord('r'):
            smoothed_u, smoothed_v = None, None # Au cas où ça foire en regardant or écran / valeur trop (pas devoir relancer l'app, jsp)
            offset_x, offset_y = 0, 0 # comme ça on reset tout du'un coup

    # Cleanup
    eye_cap.release()
    if external_cap is not None:
        external_cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    from cv2_enumerate_cameras import enumerate_cameras

    eye = 0
    front = 0

    for camera_info in enumerate_cameras():
        print(f'Camera: {camera_info.name}, VID: {camera_info.vid}, Index: {camera_info.index}')
        if 0xc45 == camera_info.vid:
            eye = camera_info.index
        if 0x58f == camera_info.vid:
            front = camera_info.index
            
    process_camera(eye, front)