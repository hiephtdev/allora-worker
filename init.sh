#!/bin/bash

# cài đặt jq
sudo apt-get update && apt-get -y install jq

# Kiểm tra xem Docker đã được cài đặt chưa
if command -v docker &> /dev/null
then
    echo "Docker đã được cài đặt."
else
    echo "Docker chưa được cài đặt. Đang tiến hành cài đặt Docker..."

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

    echo "Đã cài đặt Docker thành công."
fi