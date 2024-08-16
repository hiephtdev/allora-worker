docker build -f Dockerfile_train_models -t allora-train-model:1.0.0 .
docker run --gpus all -v $(pwd)/models:/app/models -e DATABASE_PATH=/app/data/prices.db -v $(pwd)/source-data:/app/data -d allora-train-model:1.0.0
