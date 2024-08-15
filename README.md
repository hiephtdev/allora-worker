# HƯỚNG DẪN CÀI ĐẶT ALLORA WORKER

## 1. Clone code tại repo này về

```bash
git clone https://github.com/hiephtdev/allora-worker
cd allora-worker
```

## 2. Cài đặt docker, các thư viện cần thiết

```bash
chmod +x init.sh
./init.sh
```

## 3. Tiến hành faucet

Vào link và paste địa chỉ ví allora dạng `allo1jzvjewf0...`  [https://faucet.testnet-1.testnet.allora.network/](https://faucet.testnet-1.testnet.allora.network/)

## 4. Chạy worker

- Chạy worker => đợi khi nào báo thành công hết thì là chạy xong

```bash
cd node
```

- Nếu lần đầu thì gõ lệnh dưới đây truyền vào `tên node`, `mnemonic - seedphase của ví`, `cgc_api_key - api key lấy từ coingecko`

```bash
./init.config.sh <node_name> <mnemonic> <cgc_api_key>
# ví dụ: ./init.config.sh "MysticWho" "gospel guess idle vessel motor step xxx xxx xxx xxx xxx xxx" "GC-xxxxxx"
```

- Nếu không cần thay đổi gì chỉ cần tạo lại config thì gõ lệnh dưới

```bash
./init.config.sh --i
```

- Nếu cần thêm trợ giúp ở file này thì gõ

```bash
./init.config.sh --help
```

Chạy worker

```bash
docker compose up -d
```

Kiểm tra từng worker đã chạy chưa

```bash
docker logs source-01 -f
```

```bash
docker logs updater -f
```

```bash
docker logs node -f
```

## 5. Hoàn tất giờ đợi nổ điểm tại

[https://app.allora.network/points/leaderboard](https://app.allora.network/points/leaderboard)

