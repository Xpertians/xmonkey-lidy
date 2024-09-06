import os
import json
import re
import requests
from collections import Counter, defaultdict

SPDX_LICENSES_INDEX_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
PATTERN_FILE = 'spdx_license_patterns.json'
EXCLUSION_FILE = 'spdx_exclusions.json'

def download_spdx_licenses(output_file='spdx_licenses.json'):
    """ Download all SPDX licenses and store them locally in a single JSON file """
    print("Downloading SPDX license data...")
    licenses = []

    response = requests.get(SPDX_LICENSES_INDEX_URL)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the SPDX index. Status code: {response.status_code}")

    index_data = response.json()
    license_list = index_data['licenses']

    for license_info in license_list:
        license_id = license_info['licenseId']
        license_name = license_info['name']
        details_url = license_info['detailsUrl']

        license_response = requests.get(details_url)
        if license_response.status_code != 200:
            print(f"Failed to fetch license data for {license_id}. Skipping...")
            continue

        license_data = license_response.json()
        license_text = license_data.get('licenseText')

        if license_text:
            licenses.append({
                'licenseId': license_id,
                'licenseName': license_name,
                'licenseText': license_text
            })

    with open(output_file, 'w') as f:
        json.dump(licenses, f, indent=4)

    print(f"SPDX licenses downloaded and saved to {output_file}")

def load_spdx_licenses(local_file='spdx_licenses.json'):
    """ Load SPDX licenses from the local file """
    if not os.path.exists(local_file):
        raise FileNotFoundError(f"SPDX licenses file '{local_file}' not found.")
    
    with open(local_file, 'r') as f:
        return json.load(f)

def generate_license_patterns_and_exclusions(spdx_licenses, pattern_file=PATTERN_FILE, exclusion_file=EXCLUSION_FILE):
    """ Generate patterns and exclusions dynamically from the SPDX license data and store them in files """
    license_patterns = {}
    pattern_to_license = defaultdict(list)

    for license_data in spdx_licenses:
        license_id = license_data['licenseId']
        license_name = license_data['licenseName']
        license_text = license_data.get('licenseText')

        if not license_text:
            continue

        # Extract common phrases (like foundation names, URLs)
        foundation_names = re.findall(r'\b[A-Za-z]+\sFoundation\b', license_text, re.IGNORECASE)
        urls = re.findall(r'http[s]?://[^\s]+', license_text)

        # Ensure license name and SPDX ID are part of the pattern and deduplicate patterns
        patterns = list(set(foundation_names + urls + [license_name, license_id]))
        
        # Make all patterns case-insensitive by storing them in lowercase
        patterns = [pattern.lower() for pattern in patterns]
        
        # Store the patterns for the current license and track the license associated with each pattern
        license_patterns[license_id] = patterns
        for pattern in patterns:
            pattern_to_license[pattern].append(license_id)

    # Generate exclusions for licenses based on shared patterns
    exclusions = {}
    for license_id, patterns in license_patterns.items():
        exclusion_patterns = set()
        for pattern in patterns:
            if len(pattern_to_license[pattern]) > 1:
                # If this pattern is shared by multiple licenses, add unique patterns of other licenses to the exclusion list
                for other_license in pattern_to_license[pattern]:
                    if other_license != license_id:
                        exclusion_patterns.update(license_patterns[other_license])
        exclusions[license_id] = list(exclusion_patterns)

    # Save patterns and exclusions to JSON files
    with open(pattern_file, 'w') as f:
        json.dump(license_patterns, f, indent=4)
    with open(exclusion_file, 'w') as f:
        json.dump(exclusions, f, indent=4)

    print(f"License patterns and exclusions saved to {pattern_file} and {exclusion_file}")
    return license_patterns, exclusions

def load_license_patterns_and_exclusions(pattern_file=PATTERN_FILE, exclusion_file=EXCLUSION_FILE):
    """ Load license patterns and exclusions from the stored JSON files """
    if not os.path.exists(pattern_file):
        raise FileNotFoundError(f"Pattern file '{pattern_file}' not found.")
    
    if not os.path.exists(exclusion_file):
        raise FileNotFoundError(f"Exclusion file '{exclusion_file}' not found.")

    with open(pattern_file, 'r') as f:
        license_patterns = json.load(f)
    
    with open(exclusion_file, 'r') as f:
        exclusions = json.load(f)
    
    return license_patterns, exclusions

def match_license_with_patterns_and_exclusions(text, license_patterns, exclusions, spdx_license=None):
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

def match_license(text, spdx_licenses, threshold=0.5, spdx_license=None):
    """ Match a text to the closest SPDX license or a user-specified SPDX license """
    preprocessed_text = preprocess(text)
    best_match = None
    highest_score = 0.0

    if spdx_license:
        # Load patterns and exclusions, then match against the specified license
        license_patterns, exclusions = load_license_patterns_and_exclusions()
        return match_license_with_patterns_and_exclusions(text, license_patterns, exclusions, spdx_license=spdx_license)

    for license_data in spdx_licenses:
        license_id = license_data['licenseId']
        license_text = license_data.get('licenseText')

        preprocessed_license = preprocess(license_text)
        score = sorensen_dice_coefficient(preprocessed_text, preprocessed_license)

        if score > highest_score:
            highest_score = score
            best_match = license_id

    if highest_score > threshold:
        return {
            "SPDX": best_match,
            "method": "soredice_proximity_score",
            "score": highest_score,
            "debug": {
                "matched_patterns": [],
                "excluded_patterns": []
            }
        }

    # If no match above threshold, fall back to pattern-based matching with exclusions
    print("No high similarity match found. Falling back to pattern-based search with exclusions.")
    license_patterns, exclusions = load_license_patterns_and_exclusions()
    matches, debug = match_license_with_patterns_and_exclusions(text, license_patterns, exclusions)

    if matches:
        max_matches = max(matches.values())
        top_match = max(matches, key=matches.get)
        return {
            "SPDX": top_match,
            "method": "string_patterns",
            "score": max_matches,
            "debug": debug[top_match]
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

def preprocess(text):
    """ Preprocess the text by normalizing and tokenizing """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]+', '', text)  # Remove non-alphanumeric characters
    tokens = text.split()  # Split by whitespace
    return tokens

def sorensen_dice_coefficient(a, b):
    """ Compute Sørensen-Dice coefficient between two token sets """
    if not a or not b:
        return 0.0
    a_bigrams = Counter(zip(a, a[1:]))
    b_bigrams = Counter(zip(b, b[1:]))
    overlap = sum((a_bigrams & b_bigrams).values())
    total = sum(a_bigrams.values()) + sum(b_bigrams.values())
    return 2 * overlap / total

# If running for the first time, download the SPDX license data
if not os.path.exists('spdx_licenses.json'):
    download_spdx_licenses()

# Load the local SPDX license data
spdx_licenses = load_spdx_licenses()

# Generate and store license patterns and exclusions if the files do not exist
if not os.path.exists(PATTERN_FILE) or not os.path.exists(EXCLUSION_FILE):
    generate_license_patterns_and_exclusions(spdx_licenses)

# Use the NOTICE-TEST file
with open('NOTICE-TEST', 'r') as f:
    notice_text = f.read()

# Specify the SPDX ID to match against, e.g., Apache-2.0 (or set to None to match against all)
user_specified_spdx = None  # Change this value to test against a specific license

# Test matching
result = match_license(notice_text, spdx_licenses, spdx_license=user_specified_spdx)

# Print the result as a JSON output
print(json.dumps(result, indent=4))
