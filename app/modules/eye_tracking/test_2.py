import cv2
import random
import math
import numpy as np
import os
import tkinter as tk
from tkinter import ttk, filedialog
import sys
import time
import cv2.aruco as aruco

ray_lines = [] 
model_centers = []
max_rays = 100
prev_model_center_avg = (320,240)
max_observed_distance = 0  # Initialize adaptive radius
prev_darkest_point = None

# --- Gaze → external camera projection globals ---
last_sphere_center = None
last_gaze_dir = None

calibrated = False
R_gaze_to_cam = np.eye(3, dtype=np.float32)  # rotation from gaze-space to external cam space
calibrated_sphere_center = None 

sphere_center_locked_2d = False
locked_model_center_avg = prev_model_center_avg

# External camera / screen params (for 640x480)
EXT_WIDTH = 1920
EXT_HEIGHT = 1080
EXT_CX = EXT_WIDTH // 2
EXT_CY = EXT_HEIGHT // 2

# Locking for 2D sphere center in the eye image
sphere_center_locked_2d = False
locked_model_center_avg = prev_model_center_avg

# Current red circle position on external camera
circle_x = None
circle_y = None

# Un offset pour essayer de recalibrer de temps en temps
# Au début = 0 pour ne rien corriger, sauf si on le demande
offset_x = 0
offset_y = 0

# For the calibration process and to smoothen the way the red circle "jitters" right now
smoothed_u = None
smoothed_v = None

calibration_step = 0
# Les points où il faut regarder pour calibrer : rectangle ABCD avec A en haut à gauche et B à droite
calib_points_screen = [
    (100, 100),
    (EXT_WIDTH-100, 100),
    (EXT_WIDTH-100, EXT_HEIGHT-100),
    (100, EXT_HEIGHT-100)
]

# Pour essayer de faire une collecte mutliple des points à la calibration et faire une moyenne
is_collecting = False
collecting_frames_count = 0
max_calib_frames = 20
current_step_gaze_buffer = []
current_step_cam_buffer = []

# Création des marqueurs ArUco pour détecter l'écran
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
aruco_params = aruco.DetectorParameters()
aruco_detector = aruco.ArucoDetector(aruco_dict, aruco_params)
aruco_markers_centers = None
M_homography_screen = None
calib_gaze_pts = []
calib_cam_corners = []

marker_size = 100 # Taille en pixels, donc pas trop grands ig
aruco_static_corners = np.array([
    (50, 50),
    (EXT_WIDTH - 50, 50),
    (EXT_WIDTH - 50, EXT_HEIGHT - 50),
    (50, EXT_HEIGHT - 50)
], dtype=np.float32)
Hom_gaze_to_cam = None

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

# Function to detect available cameras
def detect_cameras(max_cams=10):
    available_cameras = []
    for i in range(max_cams):
        cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
        cap.set(cv2.CAP_PROP_FPS, 30)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    return available_cameras

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

# Apply thresholding to an image
def apply_binary_threshold(image, darkestPixelValue, addedThreshold):
    threshold = darkestPixelValue + addedThreshold
    _, thresholded_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY_INV)
    return thresholded_image

# Mask all pixels outside a square defined by center and size
def mask_outside_square(image, center, size):
    x, y = center
    half_size = size // 2

    mask = np.zeros_like(image)
    top_left_x = max(0, x - half_size)
    top_left_y = max(0, y - half_size)
    bottom_right_x = min(image.shape[1], x + half_size)
    bottom_right_y = min(image.shape[0], y + half_size)
    mask[top_left_y:bottom_right_y, top_left_x:bottom_right_x] = 255
    return cv2.bitwise_and(image, mask)

def optimize_contours_by_angle(contours, image):
    if len(contours) < 1:
        return contours

    # Holds the candidate points
    all_contours = np.concatenate(contours[0], axis=0)

    # Set spacing based on size of contours
    spacing = int(len(all_contours)/25)  # Spacing between sampled points

    # Temporary array for result
    filtered_points = []
    
    # Calculate centroid of the original contours
    centroid = np.mean(all_contours, axis=0)
    
    # Create an image of the same size as the original image
    point_image = image.copy()
    
    skip = 0
    
    # Loop through each point in the all_contours array
    for i in range(0, len(all_contours), 1):
    
        # Get three points: current point, previous point, and next point
        current_point = all_contours[i]
        prev_point = all_contours[i - spacing] if i - spacing >= 0 else all_contours[-spacing]
        next_point = all_contours[i + spacing] if i + spacing < len(all_contours) else all_contours[spacing]
        
        # Calculate vectors between points
        vec1 = prev_point - current_point
        vec2 = next_point - current_point
        
        with np.errstate(invalid='ignore'):
            # Calculate angles between vectors
            angle = np.arccos(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

        
        # Calculate vector from current point to centroid
        vec_to_centroid = centroid - current_point
        
        # Check if angle is oriented towards centroid
        # Calculate the cosine of the desired angle threshold (e.g., 80 degrees)
        cos_threshold = np.cos(np.radians(60))  # Convert angle to radians
        
        if np.dot(vec_to_centroid, (vec1+vec2)/2) >= cos_threshold:
            filtered_points.append(current_point)
    
    return np.array(filtered_points, dtype=np.int32).reshape((-1, 1, 2))

# Returns the largest contour that is not extremely long or tall
def filter_contours_by_area_and_return_largest(contours, pixel_thresh, ratio_thresh):
    max_area = 0
    largest_contour = None

    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= pixel_thresh:
            x, y, w, h = cv2.boundingRect(contour)
            length_to_width_ratio = max(w / h, h / w)
            if length_to_width_ratio <= ratio_thresh:
                if area > max_area:
                    max_area = area
                    largest_contour = contour

    return [largest_contour] if largest_contour is not None else []
#Fits an ellipse to the optimized contours and draws it on the image.
def fit_and_draw_ellipses(image, optimized_contours, color):
    if len(optimized_contours) >= 5:
        # Ensure the data is in the correct shape (n, 1, 2) for cv2.fitEllipse
        contour = np.array(optimized_contours, dtype=np.int32).reshape((-1, 1, 2))

        # Fit ellipse
        ellipse = cv2.fitEllipse(contour)

        # Draw the ellipse
        cv2.ellipse(image, ellipse, color, 2)  # Draw with green color and thickness of 2

        return image
    else:
        print("Not enough points to fit an ellipse.")
        return image

#checks how many pixels in the contour fall under a slightly thickened ellipse
#also returns that number of pixels divided by the total pixels on the contour border
#assists with checking ellipse goodness    
def check_contour_pixels(contour, image_shape, debug_mode_on):
    # Check if the contour can be used to fit an ellipse (requires at least 5 points)
    if len(contour) < 5:
        return [0, 0]  # Not enough points to fit an ellipse
    
    # Create an empty mask for the contour
    contour_mask = np.zeros(image_shape, dtype=np.uint8)
    # Draw the contour on the mask, filling it
    cv2.drawContours(contour_mask, [contour], -1, (255), 1)
   
    # Fit an ellipse to the contour and create a mask for the ellipse
    ellipse_mask_thick = np.zeros(image_shape, dtype=np.uint8)
    ellipse_mask_thin = np.zeros(image_shape, dtype=np.uint8)
    ellipse = cv2.fitEllipse(contour)
    
    # Draw the ellipse with a specific thickness
    cv2.ellipse(ellipse_mask_thick, ellipse, (255), 10) #capture more for absolute
    cv2.ellipse(ellipse_mask_thin, ellipse, (255), 4) #capture fewer for ratio

    # Calculate the overlap of the contour mask and the thickened ellipse mask
    overlap_thick = cv2.bitwise_and(contour_mask, ellipse_mask_thick)
    overlap_thin = cv2.bitwise_and(contour_mask, ellipse_mask_thin)
    
    # Count the number of non-zero (white) pixels in the overlap
    absolute_pixel_total_thick = np.sum(overlap_thick > 0)#compute with thicker border
    absolute_pixel_total_thin = np.sum(overlap_thin > 0)#compute with thicker border
    
    # Compute the ratio of pixels under the ellipse to the total pixels on the contour border
    total_border_pixels = np.sum(contour_mask > 0)
    
    ratio_under_ellipse = absolute_pixel_total_thin / total_border_pixels if total_border_pixels > 0 else 0
    
    return [absolute_pixel_total_thick, ratio_under_ellipse, overlap_thin]

#outside of this method, select the ellipse with the highest percentage of pixels under the ellipse 
#TODO for efficiency, work with downscaled or cropped images
def check_ellipse_goodness(binary_image, contour, debug_mode_on):
    ellipse_goodness = [0,0,0] #covered pixels, edge straightness stdev, skewedness   
    # Check if the contour can be used to fit an ellipse (requires at least 5 points)
    if len(contour) < 5:
        print("length of contour was 0")
        return 0  # Not enough points to fit an ellipse
    
    # Fit an ellipse to the contour
    ellipse = cv2.fitEllipse(contour)
    
    # Create a mask with the same dimensions as the binary image, initialized to zero (black)
    mask = np.zeros_like(binary_image)
    
    # Draw the ellipse on the mask with white color (255)
    cv2.ellipse(mask, ellipse, (255), -1)
    
    # Calculate the number of pixels within the ellipse
    ellipse_area = np.sum(mask == 255)
    
    # Calculate the number of white pixels within the ellipse
    covered_pixels = np.sum((binary_image == 255) & (mask == 255))
    
    # Calculate the percentage of covered white pixels within the ellipse
    if ellipse_area == 0:
        print("area wasq 0")
        return ellipse_goodness  # Avoid division by zero if the ellipse area is somehow zero
    
    #percentage of covered pixels to number of pixels under area
    ellipse_goodness[0] = covered_pixels / ellipse_area
    
    #skew of the ellipse (less skewed is better?) - may not need this
    axes_lengths = ellipse[1]  # This is a tuple (minor_axis_length, major_axis_length)
    major_axis_length = axes_lengths[1]
    minor_axis_length = axes_lengths[0]
    ellipse_goodness[2] = min(ellipse[1][1]/ellipse[1][0], ellipse[1][0]/ellipse[1][1])
    
    return ellipse_goodness

"""
# Process frames for pupil detection
def process_frames(thresholded_image_strict, thresholded_image_medium, thresholded_image_relaxed, frame, gray_frame, darkest_point, debug_mode_on, render_cv_window):
    global ray_lines
    global max_rays
    global prev_model_center_avg
    global max_observed_distance

    kernel_size = 5
    kernel = np.ones((kernel_size, kernel_size), np.uint8)

    dilated_image = cv2.dilate(thresholded_image_medium, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    reduced_contours = filter_contours_by_area_and_return_largest(contours, 1000, 3)

    final_rotated_rect = ((0,0),(0,0),0)

    image_array = [thresholded_image_relaxed, thresholded_image_medium, thresholded_image_strict] #holds images
    name_array = ["relaxed", "medium", "strict"] #for naming windows
    final_image = image_array[0] #holds return array
    final_contours = [] #holds final contours
    ellipse_reduced_contours = [] #holds an array of the best contour points from the fitting process
    goodness = 0 #goodness value for best ellipse
    best_array = 0 
    kernel_size = 5  # Size of the kernel (5x5)
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    gray_copy1 = gray_frame.copy()
    gray_copy2 = gray_frame.copy()
    gray_copy3 = gray_frame.copy()
    gray_copies = [gray_copy1, gray_copy2, gray_copy3]
    final_goodness = 0
    
    #iterate through binary images and see which fits the ellipse best
    for i in range(1,4):
        # Dilate the binary image
        dilated_image = cv2.dilate(image_array[i-1], kernel, iterations=2)#medium
        
        # Find contours
        contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create an empty image to draw contours
        contour_img2 = np.zeros_like(dilated_image)
        reduced_contours = filter_contours_by_area_and_return_largest(contours, 1000, 3)

        #initialize variables
        center_x, center_y = None, None

        if len(reduced_contours) > 0 and len(reduced_contours[0]) > 5:
            current_goodness = check_ellipse_goodness(dilated_image, reduced_contours[0], debug_mode_on)
            ellipse = cv2.fitEllipse(reduced_contours[0])
            center_x, center_y = map(int, ellipse[0]) 
            if debug_mode_on: #show contours 
                cv2.imshow(name_array[i-1] + " threshold", gray_copies[i-1])
                
            #in total pixels, first element is pixel total, next is ratio
            total_pixels = check_contour_pixels(reduced_contours[0], dilated_image.shape, debug_mode_on)                 
            
            cv2.ellipse(gray_copies[i-1], ellipse, (255, 0, 0), 2)  # Draw with specified color and thickness of 2
            font = cv2.FONT_HERSHEY_SIMPLEX  # Font type
            
            final_goodness = current_goodness[0]*total_pixels[0]*total_pixels[0]*total_pixels[1]

        if final_goodness > 0 and final_goodness > goodness: 
            goodness = final_goodness
            ellipse_reduced_contours = total_pixels[2]
            best_image = image_array[i-1]
            final_contours = reduced_contours
            final_image = dilated_image

    test_frame = frame.copy()
    
    final_contours = [optimize_contours_by_angle(final_contours, gray_frame)]
    
    final_rotated_rect = None

    if final_contours and not isinstance(final_contours[0], list) and len(final_contours[0]) > 5:
        ellipse = cv2.fitEllipse(final_contours[0])
        final_rotated_rect = ellipse

        # Store the new ray in the list
        ray_lines.append(final_rotated_rect)
        # **Prune rays if list exceeds max_rays**
        if len(ray_lines) > max_rays:
            num_to_remove = len(ray_lines) - max_rays
            ray_lines = ray_lines[num_to_remove:]  # Keep only the last `max_rays` elements


    global sphere_center_locked_2d, locked_model_center_avg, prev_model_center_avg
    
    model_center_average = (320,240)
    model_center = compute_average_intersection(frame, ray_lines, 5, 200, 5)

    if not sphere_center_locked_2d:
        # Normal behavior: keep updating running average while unlocked
        if model_center is not None:
            model_center_average = update_and_average_point(model_centers, model_center, 200)
        else:
            model_center_average = prev_model_center_avg

        # If we got something sensible, remember it as the last good value
        if model_center_average[0] != 0:
            prev_model_center_avg = model_center_average
            locked_model_center_avg = model_center_average
    else:
        # Once locked, always use the frozen center
        model_center_average = locked_model_center_avg


    # Example safety check
    if center_x is None or center_y is None or model_center_average[0] is None or model_center_average[1] is None:
        return  # or skip this frame

    # Calculate the distance only if model_centers has at least 100 values
    if len(model_centers) >= 100 and center_x is not None:
        distance = math.sqrt((center_x - model_center_average[0]) ** 2 + (center_y - model_center_average[1]) ** 2)
        if distance > max_observed_distance:
            max_observed_distance = distance
            
    max_observed_distance = 202

    # Draw reference lines/ellipses
    cv2.circle(frame, model_center_average, int(max_observed_distance), (255, 50, 50), 2)  # Draw eye sphere (circle)
    cv2.circle(frame, model_center_average, 8, (255, 255, 0), -1)  # Draw eye center


    if final_rotated_rect is not None and center_x is not None and center_y is not None:
        cv2.line(frame, model_center_average, (center_x, center_y), (255, 150, 50), 2)  # # Draw line from eye center to ellipse center
        
    cv2.ellipse(frame, final_rotated_rect, (20, 255, 255), 2) #draw final ellipse on image

    # Calculate the extended endpoint of gaze line
    if final_rotated_rect is not None and center_x is not None and center_y is not None:
        # Compute the vector from model_center_average to center_x, center_y
        dx = center_x - model_center_average[0]
        dy = center_y - model_center_average[1]

        # Scale the vector by 1.2x
        extended_x = int(model_center_average[0] + 2 * dx)
        extended_y = int(model_center_average[1] + 2 * dy)

        # Draw the extended gaze line
        cv2.line(frame, (center_x, center_y), (extended_x, extended_y), (200, 255, 0), 3) 

    if render_cv_window:
        cv2.imshow("Best Thresholded Image Contours on Frame", frame)

    center, direction = compute_gaze_vector(center_x, center_y, model_center_average[0], model_center_average[1])

    if center is not None and direction is not None:
        origin_text = f"Origin: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})"
        dir_text    = f"Direction: ({direction[0]:.2f}, {direction[1]:.2f}, {direction[2]:.2f})"

        # Set bottom-left corner for drawing text
        text_origin = (12, frame.shape[0] - 38)  # 40 pixels from bottom
        text_dir    = (12, frame.shape[0] - 13)  # 15 pixels from bottom
        text_origin2 = (10, frame.shape[0] - 40)  # 40 pixels from bottom
        text_dir2    = (10, frame.shape[0] - 15)  # 15 pixels from bottom

        # Draw shadow text on the frame
        cv2.putText(frame, origin_text, text_origin, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
        cv2.putText(frame, dir_text, text_dir, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
        # Draw text on the frame
        cv2.putText(frame, origin_text, text_origin2, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(frame, dir_text, text_dir2, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        #print(f"Sphere Center:   ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
        #print(f"Gaze Direction:  ({direction[0]:.3f}, {direction[1]:.3f}, {direction[2]:.3f})")
        
    else:
        print("No valid intersection found.")

    cv2.imshow("Frame with Ellipse and Rays", frame)

    return final_rotated_rect
"""
def update_and_average_point(point_list, new_point, N):
    #Adds a new point to the list, keeps only the last N points, 
    #and returns the average of those points.
    
    #Parameters:
    #- point_list: Global list storing past points [(x1, y1), (x2, y2), ...]
    #- new_point: Tuple (x, y) representing the new point to add.
    #- N: Maximum number of points to keep in the list.
    
    #Returns:
    #- (avg_x, avg_y): The average point as a tuple of integers.
    #- None if the list is empty.
    point_list.append(new_point)  # Add new point

    if len(point_list) > N:
        point_list.pop(0)  # Remove the oldest point to maintain size N

    if not point_list:
        return None  # No points available

    avg_x = int(np.mean([p[0] for p in point_list]))
    avg_y = int(np.mean([p[1] for p in point_list]))

    return (avg_x, avg_y)

def draw_orthogonal_ray(image, ellipse, length=100, color=(0, 255, 0), thickness=1):
    #Draws a ray passing through the center of an ellipse orthogonally to its major axis.
    
    #Parameters:
    #- image: The OpenCV image to draw on.
    #- ellipse: A tuple ((cx, cy), (major_axis, minor_axis), angle) representing the fitted ellipse.
    #- length: Length of the ray to draw on each side of the ellipse center.
    #- color: Color of the line in BGR format (default: green).
    #- thickness: Thickness of the line (default: 2).

    (cx, cy), (major_axis, minor_axis), angle = ellipse
    
    # Convert angle to radians
    angle_rad = np.deg2rad(angle)
    
    # Compute the normal vector at the ellipse center (perpendicular to surface)
    normal_dx = (minor_axis / 2) * np.cos(angle_rad)  # Minor axis component
    normal_dy = (minor_axis / 2) * np.sin(angle_rad)

    # Compute start and end points of the orthogonal ray
    pt1 = (int(cx - length * normal_dx / (minor_axis / 2)), int(cy - length * normal_dy / (minor_axis / 2)))
    pt2 = (int(cx + length * normal_dx / (minor_axis / 2)), int(cy + length * normal_dy / (minor_axis / 2)))

    # Draw the ray
    cv2.line(image, pt1, pt2, color, thickness)

    return image 

stored_intersections = []  # Stores all past intersections

def compute_average_intersection(frame, ray_lines, N, M, spacing):
    #Selects N random lines from the list, highlights them in red on the frame,
    #computes their intersections, stores them, and prunes stored intersections when exceeding M.

    #Parameters:
    #- frame: The OpenCV frame to draw on.
    #- ray_lines: List of ellipse tuples ((cx, cy), (major_axis, minor_axis), angle).
    #- N: Number of random lines to select for intersection calculation.
    #- M: Maximum number of stored intersections before pruning.

    #Returns:
    #- (avg_x, avg_y): Average intersection point of selected lines.
    global stored_intersections

    if len(ray_lines) < 2 or N < 2:
        return (0, 0)  # Need at least 2 lines to find intersections

    # Get frame dimensions dynamically
    height, width = frame.shape[:2]

    # Select N unique random lines
    selected_lines = random.sample(ray_lines, min(N, len(ray_lines)))

    intersections = []

    # Highlight selected rays in red
    #for ray in selected_lines:
    #    draw_orthogonal_ray(frame, ray, color=(0, 0, 255), thickness=2)  # Red lines

    # Compute intersections for each pair of selected lines
    for i in range(len(selected_lines) - 1):
        line1 = selected_lines[i]
        line2 = selected_lines[i + 1]

        angle1 = line1[2]  # Extract angle from ellipse tuple
        angle2 = line2[2]  # Extract angle from ellipse tuple

        if abs(angle1 - angle2) >= 2:  # Ensure lines differ by at least 2 degrees
            intersection = find_line_intersection(line1, line2)
            
            # Ensure the intersection is within the frame bounds before adding
            if intersection and (0 <= intersection[0] < width) and (0 <= intersection[1] < height):
                intersections.append(intersection)
                stored_intersections.append(intersection)  # Store valid intersections
        #else:
        #    print(f"Skipped intersection: Angle difference too small ({abs(angle1 - angle2):.2f}°)")

    # Prune intersections if stored list exceeds M
    if len(stored_intersections) > M:
        stored_intersections = prune_intersections(stored_intersections, M)

    # Draw all stored intersections on the frame
    #for pt in stored_intersections:
    #    cv2.circle(frame, pt, 3, (255, 255, 255), -1)  # White dot for every past intersection

    if not intersections:
        return None  # No valid intersections found

    # Compute the average intersection point
    avg_x = np.mean([pt[0] for pt in stored_intersections])
    avg_y = np.mean([pt[1] for pt in stored_intersections])


    return (int(avg_x), int(avg_y))

#Removes the oldest intersections to ensure only the last M intersections remain.
def prune_intersections(intersections, maximum_intersections):

    if len(intersections) <= maximum_intersections:
        return intersections  # No need to prune if within the limit

    # Keep only the last M intersections
    pruned_intersections = intersections[-maximum_intersections:]

    return pruned_intersections

def rotation_from_a_to_b(a, b):
    # Normalisation
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)

    v = np.cross(a, b)
    c = np.dot(a, b)

    # Si les vecteurs sont déjà alignés
    if c > 0.999999:
        return np.eye(3, dtype=np.float32)
    
    # Si les vecteurs sont opposés (180°)
    if c < -0.999999:
        # On fait une rotation de 180° sur un axe arbitraire
        return -np.eye(3, dtype=np.float32)

    # Matrice antisymétrique du produit vectoriel (non normalisé)
    vx, vy, vz = v
    K = np.array([
        [0,   -vz,  vy],
        [vz,   0,  -vx],
        [-vy,  vx,   0]
    ], dtype=np.float32)

    # Formule de Rodrigues optimisée
    R = np.eye(3, dtype=np.float32) + K + (K @ K) * (1 / (1 + c))
    return R


def find_line_intersection(ellipse1, ellipse2):
    #Computes the intersection of two lines that are orthogonal to the surface of given ellipses.
    
    #Parameters:
    #- ellipse1, ellipse2: Ellipse tuples ((cx, cy), (major_axis, minor_axis), angle).
    
    #Returns:
    #- (x, y): Intersection point of the two lines, or None if parallel.

    (cx1, cy1), (_, minor_axis1), angle1 = ellipse1
    (cx2, cy2), (_, minor_axis2), angle2 = ellipse2

    # Convert angles to radians
    angle1_rad = np.deg2rad(angle1)
    angle2_rad = np.deg2rad(angle2)

    # Compute direction vectors for the two lines
    dx1, dy1 = (minor_axis1 / 2) * np.cos(angle1_rad), (minor_axis1 / 2) * np.sin(angle1_rad)
    dx2, dy2 = (minor_axis2 / 2) * np.cos(angle2_rad), (minor_axis2 / 2) * np.sin(angle2_rad)

    # Line equations in parametric form:
    # (x1, y1) + t1 * (dx1, dy1) = (x2, y2) + t2 * (dx2, dy2)
    A = np.array([[dx1, -dx2], [dy1, -dy2]])
    B = np.array([cx2 - cx1, cy2 - cy1])

    # Solve for t1, t2 using linear algebra (if the determinant is nonzero)
    if np.linalg.det(A) == 0:
        return None  # Lines are parallel and do not intersect

    t1, t2 = np.linalg.solve(A, B)

    # Compute intersection point
    intersection_x = cx1 + t1 * dx1
    intersection_y = cy1 + t1 * dy1

    return (int(intersection_x), int(intersection_y))

def compute_gaze_vector(x, y, center_x, center_y, screen_width=1920, screen_height=1080):
    #Compute 3D gaze direction from pupil and sphere center screen coordinates.
    #Returns:
    #    sphere_center (np.ndarray): 3D position of the sphere center in world space
    #    gaze_direction (np.ndarray): Normalized 3D direction vector from sphere center

    # Get viewport dimensions
    viewport_width = screen_width
    viewport_height = screen_height

    # Define camera and projection settings
    fov_y_deg = 45.0
    aspect_ratio = viewport_width / viewport_height
    far_clip = 100.0

    # Camera position is fixed at z = 3
    camera_position = np.array([0.0, 0.0, 3.0])

    # Compute size of far plane in world units
    fov_y_rad = np.radians(fov_y_deg)
    half_height_far = np.tan(fov_y_rad / 2) * far_clip
    half_width_far = half_height_far * aspect_ratio

    # Convert screen (x, y) to normalized device coordinates [-1, 1]
    ndc_x = (2.0 * x) / viewport_width - 1.0
    ndc_y = 1.0 - (2.0 * y) / viewport_height

    # Project pupil center to far plane coordinates in world space
    far_x = ndc_x * half_width_far
    far_y = ndc_y * half_height_far
    far_z = camera_position[2] - far_clip
    far_point = np.array([far_x, far_y, far_z])

    # Compute ray direction from camera to far plane point
    ray_origin = camera_position
    ray_direction = far_point - camera_position
    ray_direction /= np.linalg.norm(ray_direction)

    # Sphere radius and center offset
    inner_radius = 1.0 / 1.05
    sphere_offset_x = (center_x / screen_width) * 2.0 - 1.0
    sphere_offset_y = 1.0 - (center_y / screen_height) * 2.0
    sphere_center = np.array([sphere_offset_x * 1.5, sphere_offset_y * 1.5, 0.0])

    # Compute intersection with sphere
    origin = ray_origin
    direction = ray_direction
    L = origin - sphere_center

    a = np.dot(direction, direction)
    b = 2 * np.dot(direction, L)
    c = np.dot(L, L) - inner_radius**2

    discriminant = b**2 - 4 * a * c
    if discriminant < 0:
        # Compute the closest point to the sphere (tangent point approximation)
        t = -np.dot(direction, L) / np.dot(direction, direction)
        intersection_point = origin + t * direction
        intersection_local = intersection_point - sphere_center
        target_direction = intersection_local / np.linalg.norm(intersection_local)
    else:
        sqrt_disc = np.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2 * a)
        t2 = (-b + sqrt_disc) / (2 * a)

        t = None
        if t1 > 0 and t2 > 0:
            t = min(t1, t2)
        elif t1 > 0:
            t = t1
        elif t2 > 0:
            t = t2
        if t is None:
            return None, None

    # Final intersection point
    intersection_point = origin + t * direction
    intersection_local = intersection_point - sphere_center
    target_direction = intersection_local / np.linalg.norm(intersection_local)

    sqrt_disc = np.sqrt(discriminant)
    t1 = (-b - sqrt_disc) / (2 * a)
    t2 = (-b + sqrt_disc) / (2 * a)

    t = None
    if t1 > 0 and t2 > 0:
        t = min(t1, t2)
    elif t1 > 0:
        t = t1
    elif t2 > 0:
        t = t2
    if t is None:
        return None, None

    # Final intersection point
    intersection_point = origin + t * direction

    # Convert to local space relative to sphere center
    intersection_local = intersection_point - sphere_center
    target_direction = intersection_local / np.linalg.norm(intersection_local)

    # Local green ring direction
    circle_local_center = np.array([0.0, 0.0, inner_radius])
    circle_local_center /= np.linalg.norm(circle_local_center)

    # Compute rotation to align local +Z to target
    rotation_axis = np.cross(circle_local_center, target_direction)
    rotation_axis_norm = np.linalg.norm(rotation_axis)
    if rotation_axis_norm < 1e-6:
        return sphere_center, circle_local_center

    rotation_axis /= rotation_axis_norm
    dot = np.dot(circle_local_center, target_direction)
    dot = np.clip(dot, -1.0, 1.0)
    angle_rad = np.arccos(dot)

    # Rotation matrix from axis-angle
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)
    t_ = 1 - c
    x_, y_, z_ = rotation_axis

    rotation_matrix = np.array([
        [t_*x_*x_ + c, t_*x_*y_ - s*z_, t_*x_*z_ + s*y_],
        [t_*x_*y_ + s*z_, t_*y_*y_ + c, t_*y_*z_ - s*x_],
        [t_*x_*z_ - s*y_, t_*y_*z_ + s*x_, t_*z_*z_ + c]
    ])

     # Rotate +Z vector to get gaze direction
    gaze_local = np.array([0.0, 0.0, inner_radius])
    gaze_rotated = rotation_matrix @ gaze_local
    gaze_rotated /= np.linalg.norm(gaze_rotated)

    # --- Choose which sphere center to output: fixed (after calibration) or current ---
    global last_sphere_center, last_gaze_dir, calibrated_sphere_center
    last_sphere_center = sphere_center.copy()
    last_gaze_dir = gaze_rotated.copy()

    if calibrated_sphere_center is not None:
        sphere_center_out = calibrated_sphere_center
    else:
        sphere_center_out = sphere_center

    # --- Write to file (overwrite every frame) ---
    file_path = "gaze_vector.txt"

    def is_file_available(path):
        try:
            with open(path, "a"):
                return True
        except IOError:
            return False

    if is_file_available(file_path):
        try:
            with open(file_path, "w") as f:
                # Use sphere_center_out (fixed after calibration) for logging
                all_values = np.concatenate((sphere_center_out, gaze_rotated))
                csv_line = ",".join(f"{v:.6f}" for v in all_values)
                f.write(csv_line + "\n")
        except Exception as e:
            print("Write error:", e)
    else:
        print("File is currently in use. Skipping write.")

    return sphere_center_out, gaze_rotated

def on_mouse_frame_with_rays(event, x, y, flags, param):
    #Left-click on 'Frame with Ellipse and Rays' to manually set the eye sphere center.
    #This behaves like pressing 'c': it locks the 2D center and fixes the 3D origin
    #using the latest computed sphere center.
    global sphere_center_locked_2d, locked_model_center_avg, prev_model_center_avg
    global calibrated_sphere_center, calibrated, last_sphere_center

    if event == cv2.EVENT_LBUTTONDOWN:
        # Lock the 2D center to the clicked point
        locked_model_center_avg = (x, y)
        prev_model_center_avg = locked_model_center_avg
        sphere_center_locked_2d = True

        # If we have a valid latest 3D sphere center, fix that too
        if last_sphere_center is not None:
            calibrated_sphere_center = last_sphere_center.copy()
            calibrated = True
            print("Manual sphere center set at 2D:", locked_model_center_avg)
            print("Fixed eye origin (sphere center 3D):", calibrated_sphere_center)
        else:
            print("Manual 2D center set at:", locked_model_center_avg,
                  "but no 3D sphere center available yet.")


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
        
"""   
def update_gaze_circle_from_current_gaze():
    
    # Use the latest gaze vector to update the circle position on the external camera.
    # Assumes we have calibrated R_gaze_to_cam that maps gaze_dir to external cam space.

    global circle_x, circle_y, last_gaze_dir, calibrated, smoothed_u, smoothed_v

    # Comme ça ça return pour pas update avant d'avoir fait les 4 cercles (bon sauf si spam C mais azy)
    if not calibrated or last_gaze_dir is None:
        return

    # Projection vecteur gaze à l'instant t
    gz = last_gaze_dir[2]
    if abs(gz) < 1e-6:
        return
    vec = np.array([[[last_gaze_dir[0]/gz, last_gaze_dir[1]/gz]]], dtype=np.float32)

    # Maintenant on utilise l'homographie pour récupérer le point en mappant le vecteur sur l'homographie
    target = cv2.perspectiveTransform(vec, M_homography)
    u, v = target[0][0][0], target[0][0][1]
    
    u = np.clip(u, -EXT_WIDTH*0.5, EXT_WIDTH*1.5)
    v = np.clip(v, -EXT_HEIGHT*0.5, EXT_HEIGHT*1.5)

    #g_raw = last_gaze_dir.copy()
    #norm = np.linalg.norm(g_raw)
    #if norm < 1e-6: return
    #g_raw /= norm
    
    # Rotate gaze into external camera coordinate system
    #g = R_gaze_to_cam @ last_gaze_dir

    # Avoid weird cases where gaze points behind the camera
    #if g[2] <= 1e-3:
    #    return

    # Sensitivité/gain sur les x et y
    #sens_x = 7000
    #sens_y = 4000

    # Simple pinhole projection onto 2D
    #u = EXT_CX - sens_x * (g[0] / g[2])
    #v = EXT_CY - sens_y * (g[1] / g[2])

    #circle_x = int(np.clip(u, 0, EXT_WIDTH - 1))
    #circle_y = int(np.clip(v, 0, EXT_HEIGHT - 1))
    
    if smoothed_u is None or np.isnan(smoothed_u):
        smoothed_u, smoothed_v = u, v
    
    alpha = 0.2 # Si alpha petit, plus lent, mais du coup il fait moins de "jitter" quoi
    
    smoothed_u = alpha*u + (1-alpha)*smoothed_u
    smoothed_v = alpha*v + (1-alpha)*smoothed_v
    
    circle_x = int(np.clip(smoothed_u, 0, EXT_WIDTH - 1))
    circle_y = int(np.clip(smoothed_v, 0, EXT_HEIGHT - 1))
"""

# Bon du coup avec l'homographie celle ça ne sert plus à rien à priori
# Mais il faut espérer que l'homograhie fonctionne mieux
"""
def calibrate_gaze_to_external():
    global calibrated, R_gaze_to_cam, calibrated_sphere_center
    global sphere_center_locked_2d, locked_model_center_avg, prev_model_center_avg
    global circle_x, circle_y

    if last_gaze_dir is None or last_sphere_center is None:
        print("Calibration failed: no gaze vector / origin available yet.")
        return

    # Direction actuelle normalisée
    current_gaze = last_gaze_dir.copy()
    current_gaze /= np.linalg.norm(current_gaze)

    # On veut que ce regard corresponde au centre de l'écran [0, 0, 1]
    forward = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    
    # Matrice de rotation
    R_gaze_to_cam = rotation_from_a_to_b(current_gaze, forward)

    # Fixer centre de l'oeil etc et fixer cercle rouge là où on regarde pour qu'il arrête de se téléporter
    calibrated_sphere_center = last_sphere_center.copy()
    sphere_center_locked_2d = True
    locked_model_center_avg = prev_model_center_avg
    circle_x, circle_y = EXT_CX, EXT_CY
    
    calibrated = True
"""

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
    
    # apply thresholding operations at different levels
    # at least one should give us a good ellipse segment
    # thresholded_image_strict = apply_binary_threshold(gray_frame, darkest_pixel_value, 5)#lite
    # thresholded_image_strict = mask_outside_square(thresholded_image_strict, darkest_point, 250)

    # thresholded_image_medium = apply_binary_threshold(gray_frame, darkest_pixel_value, 15)#medium
    # thresholded_image_medium = mask_outside_square(thresholded_image_medium, darkest_point, 250)
    
    # thresholded_image_relaxed = apply_binary_threshold(gray_frame, darkest_pixel_value, 25)#heavy
    # thresholded_image_relaxed = mask_outside_square(thresholded_image_relaxed, darkest_point, 250)
    
    # #take the three images thresholded at different levels and process them
    # final_rotated_rect = process_frames(thresholded_image_strict, thresholded_image_medium, thresholded_image_relaxed, frame, gray_frame, darkest_point, False, False)
    
    # return final_rotated_rect


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
    cv2.namedWindow("Frame with Ellipse and Rays")
    cv2.setMouseCallback("Frame with Ellipse and Rays", on_mouse_frame_with_rays)

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


# Process a selected video file
def process_video():
    video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi")])

    if not video_path:
        return  # User canceled selection

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video file.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        process_frame(frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            cv2.waitKey(0)

    cap.release()
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