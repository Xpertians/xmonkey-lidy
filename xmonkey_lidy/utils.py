import json
import re


class LicenseUtils:
    def match_license(self, text, licenses_file):
        """Identify the license by matching with licenses."""
        with open(licenses_file, 'r') as f:
            licenses = json.load(f)
        # Implement the matching logic (Sørensen-Dice and patterns)
        return {"SPDX": "example-license", "method": "example", "score": 0.75}

    def validate_patterns(self, spdx, patterns_file, exclusions_file):
        """Validate the patterns for a specific SPDX or all SPDX."""
        with open(patterns_file, 'r') as f:
            patterns = json.load(f)
        with open(exclusions_file, 'r') as f:
            exclusions = json.load(f)
        # Implement validation logic
        return {"validation": "debug info"}
