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

## 3. Đổi lại addressKeyName, addressRestoreMnemonic trong file node/config.json, CGC_API_KEY trong docker-compose

```bash
nano ./node/config.json
```

- Dùng bàn phím lên xuống tìm đến dòng `addressRestoreMnemonic` thay thế cụm này bằng seed phase ví của bạn, `addressKeyName` tên node

```bash
nano ./node/docker-compose.yaml
```

- Dùng bàn phím lên xuống tìm đến dòng `CGC_API_KEY` thay thế bằng api key của bạn lấy từ coingecko

- Sau khi sửa xong nhấn `Ctrl + O` để lưu, sau đó `Enter`, tiếp đến nhấn `Ctrl + X` để thoát

## 4. Tiến hành faucet

Vào link và paste địa chỉ ví allora dạng `allo1jzvjewf0...`  [https://faucet.testnet-1.testnet.allora.network/](https://faucet.testnet-1.testnet.allora.network/)

## 5. Chạy worker

- Chạy worker => đợi khi nào báo thành công hết thì là chạy xong

```bash
cd node

# Tạo file config
chmod +x ./init.config.sh
./init.config.sh
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
docker logs updater-01 -f
```

```bash
docker logs node -f
```

## 6. Hoàn tất giờ đợi nổ điểm tại

[https://app.allora.network/points/leaderboard](https://app.allora.network/points/leaderboard)

