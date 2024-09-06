import json
import os
from .utils import LicenseUtils

class LicenseMatcher:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    
    def __init__(self):
        self.licenses_file = os.path.join(self.DATA_DIR, "spdx_licenses.json")
        self.patterns_file = os.path.join(self.DATA_DIR, "spdx_license_patterns.json")
        self.exclusions_file = os.path.join(self.DATA_DIR, "spdx_exclusions.json")
        self.utils = LicenseUtils()

    def identify_license(self, file_path):
        """Identify the license of a file."""
        with open(file_path, 'r') as f:
            text = f.read()

        return self.utils.match_license(text, self.licenses_file)

    def validate_patterns(self, spdx=None):
        """Validate pattern matching for a specific SPDX or all SPDX."""
        return self.utils.validate_patterns(spdx, self.patterns_file, self.exclusions_file)

    def produce_license(self, spdx):
        """Produce a copy of the specified SPDX license."""
        with open(self.licenses_file, 'r') as f:
            licenses = json.load(f)

        for license_data in licenses:
            if license_data['licenseId'] == spdx:
                return license_data['licenseText']
        return f"License {spdx} not found."
