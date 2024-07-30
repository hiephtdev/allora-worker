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

Sau khi cài đặt xong chạy lệnh

```bash
echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc
source ~/.bashrc

echo "export PATH=$PATH:/root/.local/bin" >> ~/.bashrc
source ~/.bashrc
```

Sau đó gõ các lệnh dưới nếu chạy thành công là hoàn tất cài đặt môi trường

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

- Sau khi sửa xong nhấn `Ctrl + O` để lưu, sau đó `Enter`, tiếp đến nhấn `Ctrl + X` để thoát

### Tương tự với worker-24h

```bash
nano worker-24h/docker-compose.yaml
```

- Sau khi sửa xong nhấn `Ctrl + O` để lưu, sau đó `Enter`, tiếp đến nhấn `Ctrl + X` để thoát

### Tương tự với các worker khác

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
```

Sửa lại file docker compose đổi lại SEED PHARSE (nếu chưa sửa ở 2)

```bash
nano docker-compose.yaml
```

Sau khi sửa xong nhấn `Ctrl + O` để lưu, sau đó `Enter`, tiếp đến nhấn `Ctrl + X` để thoát

Chạy worker

```bash
docker compose up -d
```

Kiểm tra từng worker đã chạy chưa

```bash
docker logs net1-worker1-topic-1 -f
```

```bash
docker logs net1-worker1-topic-3 -f
```

```bash
docker logs net1-worker1-topic-5 -f
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
```

Sửa lại file docker compose đổi lại SEED PHARSE (nếu chưa sửa ở 2)

```bash
nano docker-compose.yaml
```

Sau khi sửa xong nhấn `Ctrl + O` để lưu, sau đó `Enter`, tiếp đến nhấn `Ctrl + X` để thoát

Chạy worker

```bash
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

- Chạy worker 20m => đợi khi nào báo thành công hết thì là chạy xong

```bash
cd worker-20m
# Tạo thư mục cho worker-20m
mkdir -p worker-topic-7-data
chmod 777 worker-topic-7-data
mkdir -p worker-topic-8-data
chmod 777 worker-topic-8-data
mkdir -p worker-topic-9-data
chmod 777 worker-topic-9-data
```

Sửa lại file docker compose đổi lại SEED PHARSE (nếu chưa sửa ở 2)

```bash
nano docker-compose.yaml
```

Sau khi sửa xong nhấn `Ctrl + O` để lưu, sau đó `Enter`, tiếp đến nhấn `Ctrl + X` để thoát

Chạy worker

```bash
docker compose up -d
```

Kiểm tra từng worker đã chạy chưa

```bash
docker logs net1-worker3-topic-7 -f
```

```bash
docker logs net1-worker3-topic-8 -f
```

```bash
docker logs net1-worker3-topic-9 -f
```

Nếu hiện `net1-worker1-topic-7 | 2024-07-11T13:51:50Z INF Success: register node Tx Hash:=...` => node đã đăng ký thành công lần đầu

Hiện `net1-worker1-topic-7 | 2024-07-11T14:00:06Z INF node already registered for topic topic=3` => node đã đăng ký rồi, tức thành công kệ nó

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Da_Dang_ky_topic_thanh_cong.png">

Nếu không hiện 2 dòng trên thì chạy lệnh dưới để restart lại worker => tương tự như worker 10m

```bash
docker restart net1-worker3-topic-7 net1-worker3-topic-8 net1-worker3-topic-9
```

Tiếp theo kiểm tra xem node có kết nối được head không, nếu không có log gì, đứng im như ảnh => kết nối head không thành công => tiến hành restart lại như lệnh trên

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Khong_ket_not_head_node.png">

Nếu như ảnh dưới chạy worker là thành công

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Chay_thanh_cong.png">

- Chạy worker đự đoán giá meme => đợi khi nào báo thành công hết thì là chạy xong

```bash
cd worker-meme
# Tạo thư mục cho worker-20m
mkdir -p worker-topic-10-data
chmod 777 worker-topic-10-data
```

Sửa lại file docker compose đổi lại SEED PHARSE (nếu chưa sửa ở 2)

```bash
nano docker-compose.yaml
```

Sau khi sửa xong nhấn `Ctrl + O` để lưu, sau đó `Enter`, tiếp đến nhấn `Ctrl + X` để thoát

Vào trang [https://developer.upshot.xyz/](https://developer.upshot.xyz/) đăng ký lấy API

Sửa API Key trong `main.py`

```bash
nano main.py
```

Tìm đến `API_KEY = 'UP-'  # Replace with your actual API key` thay thế UP- bằng API key lấy được ở trên

Sau khi sửa xong nhấn `Ctrl + O` để lưu, sau đó `Enter`, tiếp đến nhấn `Ctrl + X` để thoát

Vào trang [https://www.coingecko.com/en/developers/dashboard](https://www.coingecko.com/en/developers/dashboard) đăng ký lấy API

Sửa API Key trong `app.py`

```bash
nano app.py
```

Tìm đến `coingecko_api_key = ""` thay thế bằng API key lấy được ở trên

Sau khi sửa xong nhấn `Ctrl + O` để lưu, sau đó `Enter`, tiếp đến nhấn `Ctrl + X` để thoát

Chạy worker

```bash
docker compose up -d
```

Kiểm tra worker đã chạy chưa

```bash
docker logs worker_topic_10 -f
```

Nếu hiện `worker_topic_10 | 2024-07-11T13:51:50Z INF Success: register node Tx Hash:=...` => node đã đăng ký thành công lần đầu

Hiện `worker_topic_10 | 2024-07-11T14:00:06Z INF node already registered for topic topic=3` => node đã đăng ký rồi, tức thành công kệ nó

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Da_Dang_ky_topic_thanh_cong.png">

Nếu không hiện 2 dòng trên thì chạy lệnh dưới để restart lại worker => tương tự như worker 10m

```bash
docker restart worker_topic_10
```

Tiếp theo kiểm tra xem node có kết nối được head không, nếu không có log gì, đứng im như ảnh => kết nối head không thành công => tiến hành restart lại như lệnh trên

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Khong_ket_not_head_node.png">

Nếu như ảnh dưới chạy worker là thành công

<img src="https://github.com/hiephtdev/allora-worker/blob/main/images/Chay_thanh_cong.png">

### Hoàn tất giờ đợi nổ điểm tại

[https://app.allora.network/points/leaderboard](https://app.allora.network/points/leaderboard)
