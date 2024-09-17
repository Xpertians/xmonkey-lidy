#!/bin/bash

# Define the list of strings to be removed
strings_to_remove=(
  "icu",
  "use",
  "ipa",
  "cube",
  "copyright",
  "modification",
  "derivative",
  "software",
  "license",
)

# Loop through each string and apply the sed command
for str in "${strings_to_remove[@]}"; do
  sed -i '' "/$str/d" ./xmonkey_lidy/data/spdx_exclusions.json
done
