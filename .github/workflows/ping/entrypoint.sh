#!/bin/sh

set -o nounset

ping \
    -c "$INPUT_COUNT" \
    -t "$INPUT_TIMEOUT" \
    $INPUT_ARGS "$INPUT_HOST" > "$INPUT_PATH"

PCT_LOSS="$(cat "$INPUT_PATH" | tail -n 2 | grep 'packet loss' | perl -pe 's/^.* ([0-9\.]+). packet loss.*$/$1/')"
echo "::set-output name=ping_pct_loss::$PCT_LOSS"

AVG_RTT="$(cat "$INPUT_PATH" | tail -n 2 | grep 'round-trip' | awk -F'/' '{print $4}')"
echo "::set-output name=ping_avg_rtt::$AVG_RTT"

