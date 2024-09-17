import json
import os
import re
from collections import Counter


class LicenseMatcher:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

    def __init__(self):
        self.licenses_file = os.path.join(
            self.DATA_DIR, "spdx_licenses.json"
        )
        self.patterns_file = os.path.join(
            self.DATA_DIR, "spdx_license_patterns.json"
        )
        self.exclusions_file = os.path.join(
            self.DATA_DIR, "spdx_exclusions.json"
        )
        self.license_metadata = self._load_metadata(self.licenses_file)
        self.pattern_metadata = self._load_metadata(self.patterns_file)
        self.exclusion_metadata = self._load_metadata(self.exclusions_file)

    def identify_license(self, content, is_file=True, use_soredice_only=False, debug=False, threshold=0.5):
        """Identify the license of a file using Sørensen-Dice or fallback to pattern matching."""
        if is_file:
            with open(content, 'r') as f:
                text = f.read()
        else:
            text = content
        # Load patterns and exclusions
        spdx_licenses = self._load_json(self.licenses_file)["data"]
        license_patterns = self._load_json(self.patterns_file)["data"]
        exclusions = self._load_json(self.exclusions_file)["data"]
        # If using Sørensen-Dice only, skip pattern matching
        if use_soredice_only:
            best_match, score, debug_info = self.match_license_using_sorensen_dice(text, spdx_licenses, threshold, debug)
            return {
                "SPDX": best_match or "UNKNOWN",
                "method": "soredice_proximity_score",
                "score": score,
                "publisher": self.license_metadata.get("publisher", "Unknown Publisher"),
                "generated_on": self.license_metadata.get("generated_on", "Unknown Date"),
                "debug": debug_info if debug else {}
            }
        # First try to match using Sørensen-Dice
        best_match, score, debug_info = self.match_license_using_sorensen_dice(text, spdx_licenses, threshold, debug)
        if best_match:
            # If a match is found using Sørensen-Dice, return it
            return {
                "SPDX": best_match,
                "method": "soredice_proximity_score",
                "score": score,
                "publisher": self.license_metadata.get("publisher", "Unknown Publisher"),
                "generated_on": self.license_metadata.get("generated_on", "Unknown Date"),
                "debug": debug_info if debug else {}
            }
        # If no match exceeds the threshold, fall back to pattern matching
        print("No high similarity match found. Falling back to pattern-based search.")
        matches, pattern_debug_info = self.match_license_with_patterns_and_exclusions(text, license_patterns, exclusions)
        # Filter out licenses with 0 matches
        matches = {license_id: count for license_id, count in matches.items() if count > 0}
        if matches:
            top_license = max(matches, key=matches.get)
            return {
                "SPDX": top_license,
                "method": "string_patterns",
                "score": matches[top_license],
                "publisher": self.pattern_metadata.get("publisher", "Unknown Publisher"),
                "generated_on": self.pattern_metadata.get("generated_on", "Unknown Date"),
                "debug": pattern_debug_info[top_license] if debug else {}
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

    def extract_copyright_info(self, content, is_file=True):
        return self.extract_copyright_info_from_file(content, is_file)

    def extract_copyright_info_from_file(self, content, is_file=True):
        """Extract copyright information from any text file."""
        if is_file:
            with open(content, 'r') as f:
                text = f.read()
        else:
            text = content
        # Improved regex to avoid legal instructions, placeholders, and false positives
        copyright_pattern = re.compile(
            r'(?i)^\s*(copyright|\(c\)|©)\s*(?:\(?c\)?\s*)?(\d{4}(?:-\d{4})?)?\s*(?!.*(?:notice|retain|included|works|license|source|form|derivative|reproduce))(.*?)\s*(?:\.|$)', re.MULTILINE)
        # Find all matches in the text
        copyrights = re.findall(copyright_pattern, text)
        # Validate and filter out placeholder strings like [yyyy] or [name of copyright owner]
        valid_copyrights = []
        for match in copyrights:
            year = match[1].strip() if match[1] else "Unknown"
            holder = match[2].strip() if match[2] else "Unknown"
            # Check if the year or holder contains placeholders like YYYY or [name of copyright owner]
            if re.search(r'\b(?:YYYY|yyyy|[Bb]rackets|name of copyright owner)\b|\[.*?\]', holder) or 'yyyy' in year:
                continue  # Skip placeholders
            valid_copyrights.append({
                "copyright": match[0].strip(),
                "year": year,
                "holder": holder
            })
        if valid_copyrights:
            return valid_copyrights
        else:
            return "[]"

    def validate_patterns(self, content, is_file=True, spdx=None):
        """Validate the license file against specific or all SPDX patterns."""
        if is_file:
            with open(content, 'r') as f:
                text = f.read()
        else:
            text = content
        # Load patterns and exclusions
        license_patterns = self._load_json(self.patterns_file)["data"]
        exclusions = self._load_json(self.exclusions_file)["data"]
        if spdx:
            # Validate against a specific license
            match_data = self.match_license_with_patterns_and_exclusions(text, license_patterns, exclusions, spdx_license=spdx)
            result = match_data.get(spdx, 0)
            debug_info = match_data.get("debug", {})
            return {
                "SPDX": spdx,
                "result": result,
                "debug": debug_info,
                "publisher": self.pattern_metadata.get("publisher", "Unknown Publisher"),
                "generated_on": self.pattern_metadata.get("generated_on", "Unknown Date")
            }
        # Validate against all licenses
        matches, debug_info = self.match_license_with_patterns_and_exclusions(text, license_patterns, exclusions)
        return {
            "matches": matches,
            "debug": debug_info,
            "publisher": self.pattern_metadata.get("publisher", "Unknown Publisher"),
            "generated_on": self.pattern_metadata.get("generated_on", "Unknown Date")
        }

    def produce_license(self, spdx_license):
        """Return the full text of a specific SPDX license."""
        # Load the SPDX license data
        spdx_licenses = self._load_json(self.licenses_file)["data"]
        # Search for the requested license
        for license_data in spdx_licenses:
            if license_data['licenseId'].lower() == spdx_license.lower():
                return license_data.get('licenseText', f"No license text found for {spdx_license}")
        return f"SPDX license {spdx_license} not found."

    def match_license_using_sorensen_dice(self, text, spdx_licenses, threshold=0.5, debug=False):
        """Match a text to the closest SPDX license using Sørensen-Dice."""
        preprocessed_text = self._preprocess(text)
        best_match = None
        highest_score = 0.0
        debug_info = {}
        for license_data in spdx_licenses:
            license_id = license_data['licenseId']
            license_text = license_data.get('licenseText')
            preprocessed_license = self._preprocess(license_text)
            score = self.sorensen_dice_coefficient(preprocessed_text, preprocessed_license)
            if debug:
                debug_info[license_id] = {"score": score}
            if score > highest_score:
                highest_score = score
                best_match = license_id
        if highest_score > threshold:
            return best_match, highest_score, debug_info
        else:
            return None, 0.0, debug_info

    def sorensen_dice_coefficient(self, a, b):
        """Compute Sørensen-Dice coefficient between two token sets."""
        if not a or not b:
            return 0.0
        a_bigrams = Counter(zip(a, a[1:]))
        b_bigrams = Counter(zip(b, b[1:]))
        overlap = sum((a_bigrams & b_bigrams).values())
        total = sum(a_bigrams.values()) + sum(b_bigrams.values())
        return 2 * overlap / total

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
                    spdx_license: match_count,
                    "debug": {
                        "matched_patterns": matched_patterns,
                        "excluded_patterns": excluded_patterns
                    }
                }
            return {spdx_license: 0}

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

    def _preprocess(self, text):
        """Preprocess the text by normalizing and tokenizing."""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]+', '', text)  # Remove non-alphanumeric characters
        tokens = text.split()  # Split by whitespace
        return tokens

    def _load_json(self, filepath):
        """Helper function to load JSON data from a file."""
        with open(filepath, 'r') as f:
            return json.load(f)

    def _load_metadata(self, filepath):
        """Helper function to load metadata from JSON files."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Check if the JSON file has metadata. If it's a list, return an empty dict.
                if isinstance(data, dict) and "metadata" in data:
                    return data.get("metadata", {})
                return {}
        except FileNotFoundError:
            return {}
