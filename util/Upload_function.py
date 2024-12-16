import httpx
from decouple import config

# Specify the file to be uploaded
file_path = "./util/Picture/output.ply"
url= config("URL")
# Disable SSL verification for testing (use cautiously in production)
verify_ssl = False

# Use httpx for HTTP/2 communication
with httpx.Client(http2=True, verify=verify_ssl) as client:
    with open(file_path, "rb") as file:
        # Prepare the file for upload
        files = {"file": (file_path, file, "application/octet-stream")}
        
        # Measure time for the request

        response = client.post(url, files=files)
        