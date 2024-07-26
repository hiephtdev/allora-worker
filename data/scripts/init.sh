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

# Cập nhật PATH
echo "export PATH=$PATH:/root/.local/bin" >> ~/.bashrc
source ~/.bashrc
