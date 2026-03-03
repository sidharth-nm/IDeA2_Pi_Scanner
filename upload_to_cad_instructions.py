'''
Continues off generate_3d_obj.py. Hence, assumes an "output.zip" already exists in the given directory.
Unzips the file from the previous script, extracts the .OBJ file and uploads to the n8n webhook to start generating instructions for recreation in Autodesk Fusion.
'''

import os
import zipfile
import requests
from dotenv import load_dotenv

# Configuration; directory/file paths and loading webhook URL from env
load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
script_dir = os.path.dirname(os.path.abspath(__file__))
zip_path = os.path.join(script_dir, "output.zip")
extract_path = os.path.join(script_dir, "output")

# Extracts the zip file to a folder within current directory
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(extract_path)

# Finds & stores the OBJ file to be uploaded to n8n
obj_file = next(
    (os.path.join(root, f)
     for root, _, files in os.walk(extract_path)
     for f in files if f.endswith(".obj")),
    None
)

# If no OBJ file found, throws an error
if not obj_file:
    raise FileNotFoundError("No .OBJ file found in output folder")

print(f"Found OBJ: {obj_file}")

# Makes POST request to the webhook with the OBJ file
with open(obj_file, "rb") as f:
    requests.post(
        WEBHOOK_URL,
        files={"file": f}
    )