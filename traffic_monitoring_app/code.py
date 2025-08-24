import googlemaps
import cv2
import os
import time
from datetime import datetime
from skimage.metrics import structural_similarity as compare_ssim

# Initialize Google Maps API with your API key
gmaps = googlemaps.Client(key='YOUR_API_KEY')  # Replace with your actual API key

# Step 1: Function to get directions using Google Maps API
def get_directions(start_location, end_location, avoid_roads=[]):
    directions_result = gmaps.directions(
        start_location,
        end_location,
        mode="driving",
        departure_time=datetime.now(),
        avoid=avoid_roads
    )
    if directions_result:
        route = directions_result[0]['overview_polyline']['points']
        return route, directions_result
    return None, None

# Step 2: Compare two traffic images to detect stationary vehicles (congestion)
def compare_images(image1, image2):
    # Convert to grayscale and resize for faster processing
    gray1 = cv2.cvtColor(cv2.resize(image1, (64, 64)), cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(cv2.resize(image2, (64, 64)), cv2.COLOR_BGR2GRAY)
    
    # Compute Structural Similarity Index (SSIM)
    score, _ = compare_ssim(gray1, gray2, full=True)
    
    # Define a threshold for congestion (high similarity means no movement)
    return score > 0.9

# Step 3: Monitor traffic by capturing images from IP camera and comparing
def monitor_traffic_with_route_recalculation(start_location, end_location, ip_camera_url, interval=5):
    cap = cv2.VideoCapture(ip_camera_url)
    image_paths = []

    try:
        while True:
            print("Starting 3-minute traffic analysis cycle...")
            congested = False

            # Capture images at specified intervals
            for _ in range(36):  # Capture 36 images over 3 minutes
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture image from IP camera")
                    break
                
                # Save the captured image temporarily
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_image_path = f"temp_image_{timestamp}.jpg"
                cv2.imwrite(temp_image_path, frame)
                image_paths.append(temp_image_path)

                # Wait for the specified interval
                time.sleep(interval)

            # Compare consecutive images to detect traffic
            for i in range(len(image_paths) - 1):
                image1 = cv2.imread(image_paths[i])
                image2 = cv2.imread(image_paths[i + 1])

                # Detect congestion
                if compare_images(image1, image2):
                    print("Traffic detected!")
                    congested = True
                    break  # Stop further checks once congestion is detected

            # Output traffic status at the end of the cycle
            if congested:
                print("Congestion detected. Would you like to reroute? (yes/no)")
                user_response = input().strip().lower()
                if user_response == "yes":
                    new_route, _ = get_directions(start_location, end_location, avoid_roads=["congested_road"])
                    if new_route:
                        print(f"New route: {new_route}")
                else:
                    print("Continuing on the current route.")

            else:
                print("No traffic detected.")

            # Clear images after each cycle to conserve memory
            for image_path in image_paths:
                os.remove(image_path)
            image_paths.clear()  # Clear the list for the next cycle
            
            print("Completed 3-minute cycle. Starting again...\n")
            time.sleep(180)  # Wait for the next 3-minute cycle

    except KeyboardInterrupt:
        print("Traffic monitoring stopped.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

# Example usage
start_location = "1600 Amphitheatre Parkway, Mountain View, CA"
end_location = "1 Infinite Loop, Cupertino, CA"

# IP camera URL (Replace with your actual IP camera URL)
ip_camera_url = "rtsp://username:password@camera_ip_address:port/stream_path"

monitor_traffic_with_route_recalculation(start_location, end_location, ip_camera_url)
