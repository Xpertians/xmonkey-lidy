#!/bin/bash

sed -i '' '/"icu",/d' ./xmonkey_lidy/data/spdx_exclusions.json
sed -i '' '/"use",/d' ./xmonkey_lidy/data/spdx_exclusions.json
sed -i '' '/"ipa",/d' ./xmonkey_lidy/data/spdx_exclusions.json
sed -i '' '/"cube",/d' ./xmonkey_lidy/data/spdx_exclusions.json