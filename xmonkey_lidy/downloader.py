import os
import requests
import json
from tqdm import tqdm
from datetime import datetime
import re


class LicenseDownloader:
    SPDX_LICENSES_INDEX_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"

    def __init__(self, publisher="Official SPDX Publisher", data_dir="data"):
        self.DATA_DIR = os.path.abspath(data_dir)
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)
        self.licenses_file = os.path.join(
            self.DATA_DIR, "spdx_licenses.json"
        )
        self.patterns_file = os.path.join(
            self.DATA_DIR, "spdx_license_patterns.json"
        )
        self.exclusions_file = os.path.join(
            self.DATA_DIR, "spdx_exclusions.json"
        )
        self.metadata_file = os.path.join(
            self.DATA_DIR, "metadata.json"
        )
        self.publisher = publisher
        self.generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def download_and_update_licenses(self):
        """Download and replace SPDX licenses and generate new JSON files."""
        print(f"Downloading SPDX license data into {self.DATA_DIR}...")
        response = requests.get(self.SPDX_LICENSES_INDEX_URL)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch SPDX index. "
                f"Status code: {response.status_code}"
            )
        index_data = response.json()
        license_list = index_data['licenses']
        licenses = []
        pattern_to_license = {}
        license_patterns = {}
        total_patterns_added = 0
        total_exclusions_added = 0
        # Using tqdm to show progress while downloading each license
        for license_info in tqdm(
            license_list, desc="Downloading SPDX Licenses", unit="license"
        ):
            details_url = license_info['detailsUrl']
            license_response = requests.get(details_url)
            if license_response.status_code == 200:
                license_data = license_response.json()
                license_text = license_data.get('licenseText')
                licenses.append({
                    'licenseId': license_info['licenseId'],
                    'licenseName': license_info['name'],
                    'licenseText': license_text
                })
                patterns = self._generate_patterns(
                    license_text, license_info['licenseId'],
                    license_info['name']
                )
                license_patterns[license_info['licenseId']] = patterns
                total_patterns_added += len(patterns)

                # Track patterns for exclusion generation
                for pattern in patterns:
                    if pattern not in pattern_to_license:
                        pattern_to_license[pattern] = []
                    pattern_to_license[pattern].append(
                        license_info['licenseId']
                    )

        # Generate exclusions based on shared patterns
        exclusions = self._generate_exclusions(
            license_patterns, pattern_to_license
        )
        total_exclusions_added = sum(len(excl) for excl in exclusions.values())

        # Save licenses, patterns, and exclusions with metadata
        self._save_to_file(self.licenses_file, {
            "metadata": {
                "generated_on": self.generated_on,
                "publisher": self.publisher,
                "total_licenses_downloaded": len(licenses)
            },
            "data": licenses
        })

        self._save_to_file(self.patterns_file, {
            "metadata": {
                "generated_on": self.generated_on,
                "publisher": self.publisher,
                "total_patterns_added": total_patterns_added
            },
            "data": license_patterns
        })

        self._save_to_file(self.exclusions_file, {
            "metadata": {
                "generated_on": self.generated_on,
                "publisher": self.publisher,
                "total_exclusions_added": total_exclusions_added
            },
            "data": exclusions
        })

        print(f"\nNew SPDX license JSON files have been generated at:\n"
              f"- {self.licenses_file}\n"
              f"- {self.patterns_file}\n"
              f"- {self.exclusions_file}")
        print(f"\nSummary:\n"
              f"- Total licenses downloaded: {len(licenses)}\n"
              f"- Total patterns added: {total_patterns_added}\n"
              f"- Total exclusions added: {total_exclusions_added}\n"
              f"- Generated on: {self.generated_on}\n"
              f"- Publisher: {self.publisher}\n")

    def _generate_patterns(self, license_text, license_id, license_name):
        patterns = []

        # Common legal keywords to search for in license text
        keywords = [
            'copyright', 'license', 'permission', 'warranty', 'use',
            'redistribution', 'modification', 'distribution', 'software',
            'disclaimer', 'liability', 'derivative', 'source code', 'patent'
        ]

        # Search for keywords in the license text
        for keyword in keywords:
            if re.search(fr'\b{keyword}\b', license_text, re.IGNORECASE):
                patterns.append(keyword)

        # Extract URLs and organization names from the license text
        urls = re.findall(r'http[s]?://[^\s]+', license_text)
        org_names = re.findall(
            r'\b[A-Za-z]+\sFoundation\b', license_text, re.IGNORECASE
        )

        # Include the license name and SPDX ID as part of the patterns
        patterns += urls + org_names + [license_name, license_id]

        # Lowercase and deduplicate patterns
        return list(set([pattern.lower() for pattern in patterns]))

    def _generate_exclusions(self, license_patterns, pattern_to_license):
        exclusions = {}
        for license_id, patterns in license_patterns.items():
            exclusions[license_id] = set()
            for pattern in patterns:
                if len(pattern_to_license[pattern]) > 1:
                    for other_license in pattern_to_license[pattern]:
                        if other_license != license_id:
                            exclusions[license_id].update(
                                license_patterns[other_license]
                            )
            exclusions[license_id] = list(exclusions[license_id])

        return exclusions

    def _save_to_file(self, filepath, data):
        """Helper function to save data as JSON with proper formatting."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
