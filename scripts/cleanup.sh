#!/bin/bash

# Define the list of strings to be removed (without trailing commas in the array)
strings_to_remove=(
  "use"
  "ipa"
  "cube"
  "copyright"
  "modification"
  "derivative"
  "software"
  "license"
  "warranty"
  "permission"
)

# Loop through each string and apply the sed command
for str in "${strings_to_remove[@]}"; do
  # Escape the string properly for sed (double quotes and comma after each string)
  sed -i '' "/\"${str}\",/d" ./xmonkey_lidy/data/spdx_exclusions.json
done
