#!/bin/bash

set -e

show_help() {
    echo "Usage: $0 [--i] <node_name> <mnemonic> <cgc_api_key>"
    echo
    echo "Options:"
    echo "  --i          Skip the argument check and use default or no values"
    echo "  --help       Show this help message and exit"
    echo
    echo "Arguments:"
    echo "  <node_name>      The node name to set in the config.json file"
    echo "  <mnemonic>       The mnemonic to set in the config.json file"
    echo "  <cgc_api_key>    The CGC API key to set in the docker-compose.yaml file"
}

# Check if --help is requested
if [[ "$1" == "--help" ]]; then
    show_help
    exit 0
fi

if [ ! -f config.json ]; then
    echo "Error: config.json file not found, please provide one"
    exit 1
fi

# Ensure the worker-data directory exists
mkdir -p ./source-data
mkdir -p ./worker-data

# tìm xxx_your_mnemonic_here_xxx và your_cgc_api_key trong file config.json và thay thế chúng bằng $1 và $2
# check nếu người dùng không nhập $1 và $2 thì bỏ qua
if [[ "$1" == "--i" ]]; then
    shift
else
    if [ $# -ne 3 ]; then
        show_help
        exit 1
    fi

    # Replace placeholders with the provided arguments
    sed -i "s/\"addressKeyName\": \".*\"/\"addressKeyName\": \"$1\"/" config.json
    sed -i "s/\"addressRestoreMnemonic\": \".*\"/\"addressRestoreMnemonic\": \"$2\"/" config.json
    sed -i "s/CGC_API_KEY=.*/CGC_API_KEY=$3/" docker-compose.yaml
fi
nodeName=$(jq -r '.wallet.addressKeyName' config.json)
if [ -z "$nodeName" ]; then
    echo "No wallet name provided for the node, please provide your preferred wallet name. config.json >> wallet.addressKeyName"
    exit 1
fi

json_content=$(cat ./config.json)
stringified_json=$(echo "$json_content" | jq -c .)

mnemonic=$(jq -r '.wallet.addressRestoreMnemonic' config.json)
if [ -n "$mnemonic" ]; then
    echo "ALLORA_OFFCHAIN_NODE_CONFIG_JSON='$stringified_json'" > ./worker-data/env_file
    echo "NAME=$nodeName" >> ./worker-data/env_file
    echo "ENV_LOADED=true" >> ./worker-data/env_file
    
    echo "wallet mnemonic already provided by you, loading config.json . Please proceed to run docker compose"
    exit 1
fi

if [ ! -f ./worker-data/env_file ]; then
    echo "ENV_LOADED=false" > ./worker-data/env_file
fi

ENV_LOADED=$(grep '^ENV_LOADED=' ./worker-data/env_file | cut -d '=' -f 2)
if [ "$ENV_LOADED" = "false" ]; then
    json_content=$(cat ./config.json)
    stringified_json=$(echo "$json_content" | jq -c .)
    
    docker run -it --entrypoint=bash -v $(pwd)/worker-data:/data -v $(pwd)/scripts:/scripts -e NAME="${nodeName}" -e ALLORA_OFFCHAIN_NODE_CONFIG_JSON="${stringified_json}" alloranetwork/allora-chain:latest -c "bash /scripts/init.sh"
    echo "config.json saved to ./worker-data/env_file"
else
    echo "config.json is already loaded, skipping the operation. You can set ENV_LOADED variable to false in ./worker-data/env_file to reload the config.json"
fi