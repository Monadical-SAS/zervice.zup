#!/bin/sh

# set -o errexit
# set -o nounset
# set -o pipefail
set -o xtrace
pwd

curl --silent \
   --output "$INPUT_RESPONSE_PATH"  \
   --write-out "$INPUT_STATS" \
   $INPUT_ARGS "$INPUT_URL" > "$INPUT_STATS_PATH"

OUTPUT="$(cat "$INPUT_STATS_PATH")"

HTTP_CODE="$(cat "$INPUT_STATS_PATH" | grep http_code | awk '{print $2}')"
echo "::set-output name=http_code::$HTTP_CODE"

TOTAL_TIME="$(cat "$INPUT_STATS_PATH" | grep time_total | awk '{print $2*1000}')"
echo "::set-output name=total_time::$TOTAL_TIME"
