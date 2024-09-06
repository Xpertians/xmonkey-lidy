import os
import requests
import json

class LicenseDownloader:
    SPDX_LICENSES_INDEX_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    
    def __init__(self):
        self.licenses_file = os.path.join(self.DATA_DIR, "spdx_licenses.json")
        self.patterns_file = os.path.join(self.DATA_DIR, "spdx_license_patterns.json")
        self.exclusions_file = os.path.join(self.DATA_DIR, "spdx_exclusions.json")
    
    def download_and_update_licenses(self):
        """Download and replace SPDX licenses and generate new JSON files."""
        response = requests.get(self.SPDX_LICENSES_INDEX_URL)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch SPDX index. Status code: {response.status_code}")

        index_data = response.json()
        license_list = index_data['licenses']
        licenses = []

        for license_info in license_list:
            details_url = license_info['detailsUrl']
            license_response = requests.get(details_url)
            if license_response.status_code == 200:
                license_data = license_response.json()
                licenses.append({
                    'licenseId': license_info['licenseId'],
                    'licenseName': license_info['name'],
                    'licenseText': license_data.get('licenseText')
                })
        
        # Save licenses, patterns, and exclusions
        self._save_to_file(self.licenses_file, licenses)
        # Further processing for patterns and exclusions can be done here.
        print("License files updated.")

    def _save_to_file(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
