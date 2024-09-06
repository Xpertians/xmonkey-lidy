import json
import os
import re

class LicenseMatcher:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    
    def __init__(self):
        self.licenses_file = os.path.join(self.DATA_DIR, "spdx_licenses.json")
        self.patterns_file = os.path.join(self.DATA_DIR, "spdx_license_patterns.json")
        self.exclusions_file = os.path.join(self.DATA_DIR, "spdx_exclusions.json")
    
    def identify_license(self, file_path):
        """Identify the license of a file based on patterns and Sørensen-Dice."""
        with open(file_path, 'r') as f:
            text = f.read()

        # Load patterns and exclusions
        license_patterns = self._load_json(self.patterns_file)
        exclusions = self._load_json(self.exclusions_file)

        # Attempt to match license using patterns and exclusions
        matches, debug_info = self.match_license_with_patterns_and_exclusions(text, license_patterns, exclusions)

        if matches:
            # Return the license with the most matches
            top_license = max(matches, key=matches.get)
            return {
                "SPDX": top_license,
                "method": "string_patterns",
                "score": matches[top_license],
                "debug": debug_info[top_license]
            }
        else:
            return {
                "SPDX": "UNKNOWN",
                "method": "string_patterns",
                "score": 0,
                "debug": {
                    "matched_patterns": [],
                    "excluded_patterns": []
                }
            }

    def validate_patterns(self, spdx=None):
        """Validate pattern matching for a specific SPDX or all SPDX licenses."""
        license_patterns = self._load_json(self.patterns_file)
        exclusions = self._load_json(self.exclusions_file)

        if spdx:
            patterns = license_patterns.get(spdx, [])
            return {
                "SPDX": spdx,
                "patterns": patterns,
                "exclusions": exclusions.get(spdx, [])
            }
        else:
            return {
                "licenses": list(license_patterns.keys()),
                "total_patterns": sum(len(patterns) for patterns in license_patterns.values()),
                "total_exclusions": sum(len(excls) for excls in exclusions.values())
            }

    def produce_license(self, spdx):
        """Produce a copy of the specified SPDX license."""
        with open(self.licenses_file, 'r') as f:
            licenses = json.load(f)

        for license_data in licenses:
            if license_data['licenseId'] == spdx:
                return license_data['licenseText']
        return f"License {spdx} not found."

    def match_license_with_patterns_and_exclusions(self, text, license_patterns, exclusions, spdx_license=None):
        """ Match a text using license-specific patterns and apply
