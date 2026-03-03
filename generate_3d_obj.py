'''
Extracts images from an "images" folder in the same directory, uploads to KIRI Engine for cloud photogrammetry and saves the output ZIP file.
Assumes a populated "images" folder already exists.
'''

import os
import time
import glob
import requests
from dotenv import load_dotenv

# Configuring API key, request URLs
load_dotenv()
KIRI_API_KEY = os.getenv("KIRI_API_KEY")
IMAGE_FOLDER = "images"  # Same level as this file, needs to be populated 
CREATE_URL = "https://api.kiriengine.app/api/v1/open/photo/image"
STATUS_URL = "https://api.kiriengine.app/api/v1/open/model/getStatus?serialize="
DOWNLOAD_SOURCE_URL = 'https://api.kiriengine.app/api/v1/open/model/getModelZip?serialize='

def main():
    # Grab image files (PNG/JPG) from 'images' folder
    image_paths = glob.glob(os.path.join(IMAGE_FOLDER, "*.jpg")) + \
                  glob.glob(os.path.join(IMAGE_FOLDER, "*.png"))
  
    if not image_paths:
        print(f"No images found in the '{IMAGE_FOLDER}' directory")
        return

    print(f"Found {len(image_paths)} images. Preparing upload")
    
    # Header fields for POST request
    headers = {
        "Authorization": f"Bearer {KIRI_API_KEY}"
    }

    # Body fields for POST request
    data = {
        "modelQuality": 0,
        "textureQuality": 0,
        "textureSmoothing": 1,
        "fileFormat": "OBJ",
        "isMask": 1
    }
    
    # Preparing array of images to upload to KIRI Engine
    files = []
    file_handles = [] # To keep a tab of files to be closed later

    for path in image_paths:
        f = open(path, 'rb')
        file_handles.append(f)
        # Format: ('field_name', ('filename', file_object, 'mime_type'))
        files.append(('imagesFiles', (os.path.basename(path), f, 'image/jpeg')))

    print("☁️ Uploading to KIRI Engine API...")
    try:
        # Send the POST request with the large array of imgs
        response = requests.post(CREATE_URL, headers=headers, data=data, files=files)
        response.raise_for_status()
        
        response_data = response.json()
        serialize = response_data["data"]["serialize"]
        print(f"Upload successful, Serialize ID: {serialize}")
        
    except requests.exceptions.RequestException as e:
        print(f"Upload failed. Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Server response: {e.response.text}")
        return
    finally:
        # Close opened img files from earlier
        for f in file_handles:
            f.close()

    if not serialize:
        print("No Serialize ID returned. Exiting")
        return
    
    # Poll KIRI's servers for status until code 2 received
    # Code 2 = model is ready for download
    print("\nPolling status until completion (waiting for status code 2)...")
    download_link = None
    
    while True:
        try:
            # Send a GET request to poll the current status
            # Format of URL i sis {Base URL}{serialize}
            status_response = requests.get(f"{STATUS_URL}{serialize}", headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()
            
            # Extract the status code since KIRI hates using status codes like a sane API.
            current_status = status_data["data"]["status"]
            
            if current_status == 2:
                # Extracts download link known download link if model is ready
                download_response = requests.get(f"{DOWNLOAD_SOURCE_URL}{serialize}", headers=headers)
                download_response.raise_for_status()
                download_resp_data = download_response.json()
                
                download_link = download_resp_data["data"]["modelUrl"]
                print("\n💎 Processing complete!")
                break
            
            # See https://docs.kiriengine.app/model/retrieve-3d-model-status for specific codes
            # TLDR is 1 = Failed, 4 = Expired 
            elif current_status in [1, 4]:
                print("\n❌ Processing failed according to API.")
                return
            else:
                # Still processing (e.g., -1 = Uploading or 3 = Queueing)
                print(".", end="", flush=True)
                time.sleep(15) # Wait 15 seconds before pinging for status
                
        # If error, then print a corresponding message and wait for a bit)
        except requests.exceptions.RequestException as e:
            print(f"\nError checking status: {e}")
            time.sleep(15)

    # If download link has been obtained, then proceeds to download to output.zip
    if download_link:
        print(f"\n Model is ready")
        print(f"Download Link: {download_link}") # In case code breaks for whatever reason, download link can be extracted from terminal output
        print("\n Writing file to output.zip ...")

        response = requests.get(download_link) # Makes a GET request to the given download link
        response.raise_for_status()

        # Writes output file to output.zip in local directory
        with open("output.zip", "wb") as f:
            f.write(response.content)
    else:
        print("\n Processing finished, but no download link was found in the response")

if __name__ == "__main__":
    main()
