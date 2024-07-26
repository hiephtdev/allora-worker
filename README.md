# HƯỚNG DẪN CÀI ĐẶT ALLORA WORKER

## 1. Cài đặt môi trường

```bash
curl -sL1 https://raw.githubusercontent.com/hiephtdev/allora-worker/main/data/scripts/init.sh | bash
```

Sau khi cài đặt xong gõ các lệnh dưới nếu chạy thành công là hoàn tất cài đặt môi trường

Kiểm tra version go

```bash
go version
```

Kiểm tra version docker

```bash
go version
```

Kiểm tra version allorad => ra dòng trắng, không báo lỗi là đúng

```bash
allorad version
```

Kiểm tra version allocmd => ra phiên bản 2.0.10

```bash
allocmd --version
```

## 2. Đổi lại SEED PHASE

- Đổi lại worker-10m

```bash
nano worker-10m/docker-compose.yaml
```

- Dùng bàn phím lên xuống tìm đến 3 dòng `[SEED PHASE]` thay thế cụm này bằng seed phase ví của bạn

### Tương tự với worker-24h

```bash
nano worker-24h/docker-compose.yaml
```

## 3. Tiến hành faucet

Vào link và paste địa chỉ ví allora dạng `allo1jzvjewf0...`  [https://faucet.testnet-1.testnet.allora.network/](https://faucet.testnet-1.testnet.allora.network/)

## Chạy worker

- Chạy worker 10m => đợi khi nào báo thành công hết thì là chạy xong

```bash
cd worker-10m
docker compose up -d
```

Kiểm tra từng worker đã chạy chưa

```bash
docker logs net1-worker1-topic-1 -f
```

```bash
docker logs net1-worker1-topic-2 -f
```

```bash
docker logs net1-worker1-topic-3 -f
```

Nếu chưa chạy tất cả thì chạy lệnh dưới để restart => lại kiểm tra lại bằng các lệnh trên lặp lại đến khi chạy thành công

```bash
docker compose restart
```

- Chạy worker 24h => đợi khi nào báo thành công hết thì là chạy xong

```bash
cd worker-24h
docker compose up -d
```

Kiểm tra từng worker đã chạy chưa

```bash
docker logs net1-worker2-topic-2-f
```

```bash
docker logs net1-worker2-topic-4 -f
```

```bash
docker logs net1-worker2-topic-6 -f
```

Nếu chưa chạy tất cả thì chạy lệnh dưới để restart => lại kiểm tra lại bằng các lệnh trên lặp lại đến khi chạy thành công

```bash
docker compose restart
```

### Hoàn tất giờ đợi nổ điểm tại

[https://app.allora.network/points/leaderboard](https://app.allora.network/points/leaderboard)
