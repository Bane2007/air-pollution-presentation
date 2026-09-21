#!/bin/bash
# run-lane.sh <lane> <prompt-file>: one headless edge-lane session in its own 3G scope, stream-json log next to it
SP=/tmp/claude-1000/-home-karth-obsidian-brain/046b07c0-072c-4d74-b8ec-c3b16ce8017b/scratchpad/lanes
lane="$1"; prompt="$(cat "$2")"
cd /home/karth/obsidian/brain || exit 1
exec systemd-run --user --scope -p MemoryMax=3G -p MemorySwapMax=256M --quiet \
  env FleetRole=lane FleetDomain="$lane" \
  claude -p < /dev/null --agent edge-lane --model opus --effort medium \
    --mcp-config "$SP/mcp-research.json" --strict-mcp-config \
    --output-format stream-json --verbose \
    "$prompt" > "$SP/$lane.jsonl" 2> "$SP/$lane.err"
