# ALLORA WORKER INSTALLATION GUIDE

## 1. Clone the code from this repository

```bash
git clone https://github.com/hiephtdev/allora-worker
cd allora-worker
```

## 2. Install Docker and necessary libraries

```bash
chmod +x init.sh
./init.sh
```

## 3. Perform faucet

Go to the link and paste your Allora wallet address in the format `allo1jzvjewf0...`  [https://faucet.testnet-1.testnet.allora.network/](https://faucet.testnet-1.testnet.allora.network/)

## 4. Run the worker

- Run the worker => wait until it reports success to complete the process

```bash
cd node
```

### If this is the first time, enter the following command with the `node_name`, `mnemonic` - wallet seed phrase, and `cgc_api_key` - API key obtained from CoinGecko

```bash
./init.config.sh <node_name> <mnemonic> <cgc_api_key>
# example: ./init.config.sh "MysticWho" "gospel guess idle vessel motor step xxx xxx xxx xxx xxx xxx" "GC-xxxxxx"
```

- If no changes are needed and you just want to recreate the config, enter the following command

```bash
./init.config.sh --i
```

- If you need additional help with this file, enter

```bash
./init.config.sh --help
```

### Run the worker

```bash
docker compose up -d
```

### Check if each worker is running

```bash
docker logs source-01 -f
```

```bash
docker logs updater -f
```

```bash
docker logs node -f
```

## 5. Complete the process and wait for the points explosion at

[https://app.allora.network/points/leaderboard](https://app.allora.network/points/leaderboard)

