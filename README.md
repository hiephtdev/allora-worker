# HƯỚNG DẪN CÀI ĐẶT ALLORA WORKER

## 1. Clone code tại repo này về

```bash
git clone https://github.com/hiephtdev/allora-worker
```

## 2. Cài đặt môi trường

```bash
cd allora-worker
curl -sL1 https://raw.githubusercontent.com/hiephtdev/allora-worker/main/data/scripts/init.sh | bash
```

Sau khi cài đặt xong gõ các lệnh dưới nếu chạy thành công là hoàn tất cài đặt môi trường

Kiểm tra version go

```bash
go version
```

Kiểm tra version docker

```bash
docker -v
```

Kiểm tra version allorad => ra dòng trắng, không báo lỗi là đúng

```bash
allorad version
```

Kiểm tra version allocmd => ra phiên bản 2.0.10

```bash
allocmd --version
```

## 3. Đổi lại SEED PHASE

- Đổi lại worker-10m

```bash
nano worker-10m/docker-compose.yaml
```

- Dùng bàn phím lên xuống tìm đến 3 dòng `[SEED PHASE]` thay thế cụm này bằng seed phase ví của bạn

### Tương tự với worker-24h

```bash
nano worker-24h/docker-compose.yaml
```

## 4. Tiến hành faucet

Vào link và paste địa chỉ ví allora dạng `allo1jzvjewf0...`  [https://faucet.testnet-1.testnet.allora.network/](https://faucet.testnet-1.testnet.allora.network/)

## 5. Chạy worker

- Chạy worker 10m => đợi khi nào báo thành công hết thì là chạy xong

```bash
cd worker-10m

# Tạo thư mục cho worker-10m
mkdir -p worker-topic-1-data
chmod 777 worker-topic-1-data
mkdir -p worker-topic-3-data
chmod 777 worker-topic-3-data
mkdir -p worker-topic-5-data
chmod 777 worker-topic-5-data

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

Nếu hiện `net1-worker1-topic-3 | 2024-07-11T13:51:50Z INF Success: register node Tx Hash:=...` => node đã đăng ký thành công lần đầu

Hiện `net1-worker1-topic-3 | 2024-07-11T14:00:06Z INF node already registered for topic topic=3` => node đã đăng ký rồi, tức thành công kệ nó

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Da_Dang_ky_topic_thanh_cong.png">

Nếu không hiện 2 dòng trên thì chạy lệnh dưới để restart lại worker => worker nào lỗi thì restart worker đó, restart nhiều worker thì phân cách bởi dấu cách, như ở dưới là restart 3 worker

```bash
docker restart logs net1-worker1-topic-1 net1-worker1-topic-2 net1-worker1-topic-3
```

Tiếp theo lặp lại lệnh kiểm tra xem node có kết nối được head không, nếu không có log gì, đứng im như ảnh => kết nối head không thành công => tiến hành restart lại như lệnh trên

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Khong_ket_not_head_node.png">

Nếu như ảnh dưới chạy worker là thành công

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Chay_thanh_cong.png">

- Chạy worker 24h => đợi khi nào báo thành công hết thì là chạy xong

```bash
cd worker-24h
# Tạo thư mục cho worker-24h
mkdir -p worker-topic-2-data
chmod 777 worker-topic-2-data
mkdir -p worker-topic-4-data
chmod 777 worker-topic-4-data
mkdir -p worker-topic-6-data
chmod 777 worker-topic-6-data

docker compose up -d
```

Kiểm tra từng worker đã chạy chưa

```bash
docker logs net1-worker2-topic-2 -f
```

```bash
docker logs net1-worker2-topic-4 -f
```

```bash
docker logs net1-worker2-topic-6 -f
```

Nếu hiện `net1-worker1-topic-3 | 2024-07-11T13:51:50Z INF Success: register node Tx Hash:=...` => node đã đăng ký thành công lần đầu

Hiện `net1-worker1-topic-3 | 2024-07-11T14:00:06Z INF node already registered for topic topic=3` => node đã đăng ký rồi, tức thành công kệ nó

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Da_Dang_ky_topic_thanh_cong.png">

Nếu không hiện 2 dòng trên thì chạy lệnh dưới để restart lại worker => tương tự như worker 10m

```bash
docker restart net1-worker2-topic-2 net1-worker2-topic-4 net1-worker2-topic-6
```

Tiếp theo kiểm tra xem node có kết nối được head không, nếu không có log gì, đứng im như ảnh => kết nối head không thành công => tiến hành restart lại như lệnh trên

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Khong_ket_not_head_node.png">

Nếu như ảnh dưới chạy worker là thành công

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Chay_thanh_cong.png">

### Hoàn tất giờ đợi nổ điểm tại

[https://app.allora.network/points/leaderboard](https://app.allora.network/points/leaderboard)
