#!/bin/bash

set -e

# Cài đặt docker
sudo apt-get update &&
sudo apt-get -y install ca-certificates curl gnupg &&
sudo install -m 0755 -d /etc/apt/keyrings &&
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg &&
sudo chmod a+r /etc/apt/keyrings/docker.gpg &&
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null &&
sudo apt-get update &&
sudo apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin &&
sudo apt-get -y install docker-compose &&
sudo usermod -aG docker $USER &&
newgrp docker

# Tải và cài đặt Go
curl -OL https://go.dev/dl/go1.22.4.linux-amd64.tar.gz
sudo tar -C /usr/local -xvf go1.22.4.linux-amd64.tar.gz
echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc
source ~/.bashrc

# Cài đặt Python3-pip và nâng cấp pip mà không hiển thị màn hình xác nhận
sudo apt-get -y install python3-pip
pip install allocmd --upgrade --no-input

# Cài đặt Allora
curl -sSL https://raw.githubusercontent.com/allora-network/allora-chain/main/install.sh | bash -s -- v0.2.11

# Cập nhật PATH cho pip
echo 'export PATH="$PATH:/root/.local/bin"' >> ~/.bashrc
source ~/.bashrc

# Tạo thư mục cho worker-10m
mkdir -p worker-10m/worker-topic-1-data
chmod 777 worker-10m/worker-topic-1-data
mkdir -p worker-10m/worker-topic-3-data
chmod 777 worker-10m/worker-topic-3-data
mkdir -p worker-10m/worker-topic-5-data
chmod 777 worker-10m/worker-topic-5-data

# Tạo thư mục cho worker-24h
mkdir -p worker-24h/worker-topic-2-data
chmod 777 worker-24h/worker-topic-2-data
mkdir -p worker-24h/worker-topic-4-data
chmod 777 worker-24h/worker-topic-4-data
mkdir -p worker-24h/worker-topic-6-data
chmod 777 worker-24h/worker-topic-6-data