import json
import os
import re

class LicenseMatcher:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    
    def __init__(self):
        self.licenses_file = os.path.join(self.DATA_DIR, "spdx_licenses.json")
        self.patterns_file = os.path.join(self.DATA_DIR, "spdx_license_patterns.json")
        self.exclusions_file = os.path.join(self.DATA_DIR, "spdx_exclusions.json")
        self.license_metadata = self._load_metadata(self.licenses_file)
        self.pattern_metadata = self._load_metadata(self.patterns_file)
        self.exclusion_metadata = self._load_metadata(self.exclusions_file)

    def identify_license(self, file_path):
        """Identify the license of a file based on patterns and Sørensen-Dice."""
        with open(file_path, 'r') as f:
            text = f.read()

        # Load patterns and exclusions
        license_patterns = self._load_json(self.patterns_file)["data"]
        exclusions = self._load_json(self.exclusions_file)["data"]

        # Attempt to match license using patterns and exclusions
        matches, debug_info = self.match_license_with_patterns_and_exclusions(text, license_patterns, exclusions)

        if matches:
            # Return the license with the most matches
            top_license = max(matches, key=matches.get)
            return {
                "SPDX": top_license,
                "method": "string_patterns",
                "score": matches[top_license],
                "publisher": self.pattern_metadata.get("publisher", "Unknown Publisher"),
                "generated_on": self.pattern_metadata.get("generated_on", "Unknown Date"),
                "debug": debug_info[top_license]
            }
        else:
            return {
                "SPDX": "UNKNOWN",
                "method": "string_patterns",
                "score": 0,
                "publisher": self.pattern_metadata.get("publisher", "Unknown Publisher"),
                "generated_on": self.pattern_metadata.get("generated_on", "Unknown Date"),
                "debug": {
                    "matched_patterns": [],
                    "excluded_patterns": []
                }
            }

    def validate_patterns(self, spdx=None):
        """Validate pattern matching for a specific SPDX or all SPDX licenses."""
        license_patterns = self._load_json(self.patterns_file)["data"]
        exclusions = self._load_json(self.exclusions_file)["data"]

        if spdx:
            patterns = license_patterns.get(spdx, [])
            return {
                "SPDX": spdx,
                "patterns": patterns,
                "exclusions": exclusions.get(spdx, []),
                "publisher": self.pattern_metadata.get("publisher", "Unknown Publisher"),
                "generated_on": self.pattern_metadata.get("generated_on", "Unknown Date")
            }
        else:
            return {
                "licenses": list(license_patterns.keys()),
                "total_patterns": sum(len(patterns) for patterns in license_patterns.values()),
                "total_exclusions": sum(len(excls) for excls in exclusions.values()),
                "publisher": self.pattern_metadata.get("publisher", "Unknown Publisher"),
                "generated_on": self.pattern_metadata.get("generated_on", "Unknown Date")
            }

    def produce_license(self, spdx):
        """Produce a copy of the specified SPDX license."""
        with open(self.licenses_file, 'r') as f:
            licenses = json.load(f)["data"]

        for license_data in licenses:
            if license_data['licenseId'] == spdx:
                return license_data['licenseText']
        return f"License {spdx} not found."

    def match_license_with_patterns_and_exclusions(self, text, license_patterns, exclusions, spdx_license=None):
        """ Match a text using license-specific patterns and apply exclusions """
        matches = {}
        debug = {}
        text = text.lower()  # Make the search case-insensitive

        # If a specific SPDX license is provided, only match against that license
        if spdx_license:
            patterns = license_patterns.get(spdx_license, [])
            matched_patterns = []
            match_count = 0

            for pattern in patterns:
                if re.search(re.escape(pattern), text, re.IGNORECASE):
                    match_count += 1
                    matched_patterns.append(pattern)

            if match_count > 0:
                excluded_patterns = []
                for exclusion_pattern in exclusions.get(spdx_license, []):
                    if re.search(re.escape(exclusion_pattern), text, re.IGNORECASE):
                        excluded_patterns.append(exclusion_pattern)
                return {
                    "SPDX": spdx_license,
                    "method": "string_patterns",
                    "score": match_count,
                    "debug": {
                        "matched_patterns": matched_patterns,
                        "excluded_patterns": excluded_patterns
                    }
                }
            else:
                return {
                    "SPDX": spdx_license,
                    "method": "string_patterns",
                    "score": 0,
                    "debug": {
                        "matched_patterns": [],
                        "excluded_patterns": []
                    }
                }

        # Otherwise, match against all licenses
        for license_id, patterns in license_patterns.items():
            match_count = 0
            matched_patterns = []
            # Apply pattern matching
            for pattern in patterns:
                if re.search(re.escape(pattern), text, re.IGNORECASE):
                    match_count += 1
                    matched_patterns.append(pattern)
            
            # If matches are found, check exclusions
            if match_count > 0:
                excluded = False
                excluded_patterns = []
                for exclusion_pattern in exclusions.get(license_id, []):
                    if re.search(re.escape(exclusion_pattern), text, re.IGNORECASE):
                        excluded = True
                        excluded_patterns.append(exclusion_pattern)
                if not excluded:
                    matches[license_id] = match_count
                    debug[license_id] = {
                        "matched_patterns": matched_patterns,
                        "excluded_patterns": excluded_patterns
                    }

        return matches, debug

    def _load_json(self, filepath):
        """Helper function to load JSON data from a file."""
        with open(filepath, 'r') as f:
            return json.load(f)

    def _load_metadata(self, filepath):
        """Helper function to load metadata from JSON files."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data.get("metadata", {})
        except FileNotFoundError:
            return {}
