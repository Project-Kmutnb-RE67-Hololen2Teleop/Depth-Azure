import httpx
import time

# Define the server URL
url = "https://127.0.0.1:12345/PointCloud/upload"

# Specify the file to be uploaded
file_path = "./Upload/Sphere_500point.ply"

# Disable SSL verification for testing (use cautiously in production)
verify_ssl = False

# Use httpx for HTTP/2 communication
with httpx.Client(http2=True, verify=verify_ssl) as client:
    with open(file_path, "rb") as file:
        # Prepare the file for upload
        files = {"file": (file_path, file, "application/octet-stream")}
        
        # Measure time for the request
        start_time = time.time()
        response = client.post(url, files=files)
        elapsed_time = time.time() - start_time
        
        # Check if HTTP/2 is being used
        is_http2 = response.http_version == "HTTP/2"
        
        # Print results
        print("Single File Upload:")
        print(f"  Using HTTP/2: {is_http2}")
        print(f"  Response Code: {response.status_code}")
        print(f"  Response Body: {response.text}")
        print(f"  Time Taken: {elapsed_time:.2f} seconds")