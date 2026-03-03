'''
Continues off generate_3d_obj.py. Hence, assumes an "output.zip" already exists in the given directory.
Unzips the file from the previous script, extracts the .OBJ file and uploads to the n8n webhook to start generating instructions for recreation in Autodesk Fusion.
'''

import os
import zipfile
import requests

script_dir = os.path.dirname(os.path.abspath(__file__))
zip_path = os.path.join(script_dir, "output.zip")
extract_path = os.path.join(script_dir, "output")

with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(extract_path)

obj_file = next(
    (os.path.join(root, f)
     for root, _, files in os.walk(extract_path)
     for f in files if f.endswith(".obj")),
    None
)

if not obj_file:
    raise FileNotFoundError("No .OBJ file found in output folder")

print(f"Found OBJ: {obj_file}")

with open(obj_file, "rb") as f:
    requests.post(
        "https://narwhjorl.app.n8n.cloud/webhook/process-scan",
        files={"file": f}
    )