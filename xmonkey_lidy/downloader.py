import os
import requests
import json
from tqdm import tqdm
from datetime import datetime
from itertools import combinations
import re


class LicenseDownloader:
    SPDX_LICENSES_INDEX_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"

    def __init__(self, publisher="Official SPDX Publisher", data_dir="data"):
        self.DATA_DIR = os.path.abspath(data_dir)
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)
        self.licenses_file = os.path.join(self.DATA_DIR, "spdx_licenses.json")
        self.patterns_file = os.path.join(self.DATA_DIR, "spdx_license_patterns.json")
        self.exclusions_file = os.path.join(self.DATA_DIR, "spdx_exclusions.json")
        self.metadata_file = os.path.join(self.DATA_DIR, "metadata.json")
        self.publisher = publisher
        self.generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total_patterns_added = 0
        self.total_exclusions_added = 0
        self.stop_words = {
            'words', 'unique', 'for', 'software', 'common', 'group', 'like',
            'across', 'all', 'damage', 'particular', 'right', 'may', 'including',
            'documentation', 'source', 'following', 'whether', 'otherwise',
            'fitness', 'distribute', 'name', 'andor', 'c', 'shall', 'liability',
            'event', 'consequential', 'file', 'make', 'written',
            'term', 'version', 'data', 'work', 'however', 'loss',
            'product', 'even', 'indirect', 'incidental', 'possibility', 'kind', 'free',
            'without', 'license'
        }
        self.keywords = [
            'software', 'copyright', 'notice', 'provided', 'without', 'warranty',
            'implied', 'code', 'right', 'may', 'including',
            'source', 'must', 'whether', 'modification', 'liable', 'express',
            'granted', 'condition', 'permission', 'form', 'distribution', 'copy',
            'merchantability', 'fitness', 'used', 'distribute', 'shall', 'liability',
            'event', 'consequential', 'modify', 'file', 'disclaimer', 'term',
            'version', 'data', 'product', 'even', 'indirect', 'incidental',
            'possibility', 'legal', 'author', 'third-party', 'compliance', 'binding',
            'transfer', 'infringement', 'fees', 'organization', 'affiliated',
            'guarantee', 'damages', 'obligation', 'disclosure', 'jurisdiction',
            'affiliate', 'settlement', 'procurement', 'penalty', 'nonexclusive',
            'validity', 'govern', 'royalty', 'terms', 'obligations', 'waiver',
            'provision', 'comply', 'enforceable', 'clause', 'grant', 'affero',
            'enforce', 'redistribute', 'derivative', 'patent', 'substitute',
            'third', 'agreement', 'remedy', 'representation', 'damages', 'transfer',
            'penalty', 'claim', 'affiliate', 'fees', 'binding', 'disclosure',
            'material', 'authorized', 'publication', 'owner', 'liens', 'guarantee',
            'waiver', 'compliance', 'third-party', 'provided', 'must', 'used',
            'modify', 'disclaimer', 'permitted'
        ]

    def download_and_update_licenses(self):
        """Download and replace SPDX licenses and generate new JSON files."""
        print(f"Downloading SPDX license data into {self.DATA_DIR}...")
        response = requests.get(self.SPDX_LICENSES_INDEX_URL)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch SPDX index. Status code: {response.status_code}")
        index_data = response.json()
        license_list = index_data['licenses']
        licenses = []
        license_patterns = {}
        pattern_to_license = {}

        # Download each license and extract patterns
        for license_info in tqdm(license_list, desc="Downloading SPDX Licenses", unit="license"):
            details_url = license_info['detailsUrl']
            license_response = requests.get(details_url)
            if license_response.status_code == 200:
                license_data = license_response.json()
                license_id = license_data['licenseId']
                license_text = license_data['licenseText']
                license_name = license_data['name']
                licenses.append({
                    'licenseId': license_info['licenseId'],
                    'licenseName': license_info['name'],
                    'licenseText': license_text
                })
                patterns = self._extract_patterns(license_text, license_name, license_id)

                # Associate patterns with the license ID
                license_patterns[license_id] = patterns
                for pattern in patterns:
                    if pattern not in pattern_to_license:
                        pattern_to_license[pattern] = set()
                    pattern_to_license[pattern].add(license_id)
                self.total_patterns_added += len(patterns)

        # Generate exclusions dynamically
        exclusions = self._generate_exclusions(license_patterns, pattern_to_license)

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
                "total_patterns_added": self.total_patterns_added
            },
            "data": license_patterns
        })

        self._save_to_file(self.exclusions_file, {
            "metadata": {
                "generated_on": self.generated_on,
                "publisher": self.publisher,
                "total_exclusions_added": self.total_exclusions_added
            },
            "data": exclusions
        })
        
        print(f"\nSPDX license patterns and exclusions have been generated.")
        print(f"Total Patterns Added: {self.total_patterns_added}")
        print(f"Total Exclusions Added: {self.total_exclusions_added}")

    def _extract_patterns(self, license_text, license_name, license_id):
        """Extracts minimal and unique patterns from the license text."""
        patterns = []

        # List of organization types
        org_types = ['Foundation', 'Corporation', 'Company', 'Institute', 'Association', 'Inc', 'Ltd']

        # Search for unique keywords in the license text
        for keyword in self.keywords:
            if re.search(fr'\b{keyword}\b', license_text, re.IGNORECASE):
                patterns.append(keyword)

        # Extract URLs and organization names from the license text
        urls = re.findall(r'http[s]?://[^\s]+', license_text)

        # Dynamically create the regex pattern using the org_types list
        org_pattern = r'\b[A-Za-z]+\s(?:' + '|'.join(org_types) + r')\b'

        # Find all occurrences in the license text
        org_names = re.findall(org_pattern, license_text, re.IGNORECASE)

        # License Name base combinations
        lic_combi = self.generate_hits(license_name)
        lic_combi += self.generate_hits(license_id)

        # Include the license name and SPDX ID as part of the patterns
        patterns += urls + org_names + lic_combi + [license_name, license_id]

        # Deduplicate patterns, remove stop words, and ignore short strings
        cleaned_patterns = [pattern.replace('"', '') for pattern in patterns]
        return list(set([pattern.lower() for pattern in cleaned_patterns if pattern.lower() not in self.stop_words and len(pattern) >= 3]))

    def _generate_exclusions(self, license_patterns, pattern_to_license):
        exclusions = {}
        for license_id, patterns in license_patterns.items():
            exclusions[license_id] = set()
            for pattern in patterns:
                if pattern.lower() not in self.keywords and len(pattern) >= 3:
                    # Add to exclusion if this pattern belongs to multiple licenses
                    if len(pattern_to_license[pattern]) > 1:
                        for other_license in pattern_to_license[pattern]:
                            if other_license != license_id:
                                exclusions[license_id].update(license_patterns[other_license])
                        self.total_exclusions_added += 1
            exclusions[license_id] = list(exclusions[license_id])
        return exclusions

    def generate_hits(self, license_str):
        parts = re.split(r'[-\s]', license_str)
        hits = set()
        hits.add(license_str.lower())
        current_str = ""
        for i, part in enumerate(parts):
            if current_str:
                current_str += "-" + part.lower()
            else:
                current_str = part.lower()
            hits.add(current_str)
        hits.update([part.lower() for part in parts])
        return sorted(hits)

    def _save_to_file(self, filepath, data):
        """Helper function to save data as JSON with proper formatting."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
