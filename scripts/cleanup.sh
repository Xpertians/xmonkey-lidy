#!/bin/bash

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

for str in "${strings_to_remove[@]}"; do
  sed -i '' "/\"${str}\",/d" ./xmonkey_lidy/data/spdx_exclusions.json
done
