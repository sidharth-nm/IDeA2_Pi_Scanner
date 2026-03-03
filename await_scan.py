'''
Routinely polls the n8n server for a status code. Upon receiving code 0, starts the scanning process.

Status codes reference:
-1 = Idle
0 = In progress
1 = Finished
'''

import time
import requests

POLL_URL = "https://narwhjorl.app.n8n.cloud/webhook/scan-status"
RESULT_URL = "https://narwhjorl.app.n8n.cloud/webhook/process-scan"
POLL_INTERVAL = 5  # seconds

while True:
    response = requests.get(POLL_URL)
    data = response.json()

    if data.get("start_scan"):
        print("Scan triggered, starting...")
        
        # TODO: RUN THE OTHER SCRIPTS HERE, ENDING WITH upload_to_cad_instructions.py
        # TODO: Seriously, replace this. I only left it empty since I don't have the actual scanning script on the Pi.

        print("Scan uploaded.")

    time.sleep(POLL_INTERVAL)