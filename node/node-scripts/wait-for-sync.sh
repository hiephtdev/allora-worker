#!/bin/bash
set -e

while true; do
  status=$(curl -s http://rpc-node:26657/status | jq -r .result.sync_info.catching_up)
  if [ "$status" == "false" ]; then
    break
  fi
  echo "Waiting for rpc-node to finish syncing..."
  sleep 5
done

exec "$@"
