#!/bin/bash

set -e

if [ ! -f config.json ]; then
    echo "Error: config.json file not found, please provide one"
    exit 1
fi

# Ensure the worker-data directory exists
mkdir -p ./source-$1-data
mkdir -p ./worker-$1-data

nodeName=$(jq -r '.wallet.addressKeyName' config.json)
if [ -z "$nodeName" ]; then
    echo "No wallet name provided for the node, please provide your preferred wallet name. config.json >> wallet.addressKeyName"
    exit 1
fi

json_content=$(cat ./config.json)
stringified_json=$(echo "$json_content" | jq -c .)

mnemonic=$(jq -r '.wallet.addressRestoreMnemonic' config.json)
if [ -n "$mnemonic" ]; then
    echo "ALLORA_OFFCHAIN_NODE_CONFIG_JSON='$stringified_json'" > ./worker-$1-data/env_file
    echo "NAME=$nodeName" >> ./worker-$1-data/env_file
    echo "ENV_LOADED=true" >> ./worker-$1-data/env_file
    
    echo "wallet mnemonic already provided by you, loading config.json . Please proceed to run docker compose"
    exit 1
fi

if [ ! -f ./worker-$1-data/env_file ]; then
    echo "ENV_LOADED=false" > ./worker-$1-data/env_file
fi

ENV_LOADED=$(grep '^ENV_LOADED=' ./worker-$1-data/env_file | cut -d '=' -f 2)
if [ "$ENV_LOADED" = "false" ]; then
    json_content=$(cat ./config.json)
    stringified_json=$(echo "$json_content" | jq -c .)
    
    docker run -it --entrypoint=bash -v $(pwd)/worker-$1-data:/data -v $(pwd)/scripts:/scripts -e NAME="${nodeName}" -e ALLORA_OFFCHAIN_NODE_CONFIG_JSON="${stringified_json}" alloranetwork/allora-chain:latest -c "bash /scripts/init.sh"
    echo "config.json saved to ./worker-$1-data/env_file"
else
    echo "config.json is already loaded, skipping the operation. You can set ENV_LOADED variable to false in ./worker-$1-data/env_file to reload the config.json"
fi