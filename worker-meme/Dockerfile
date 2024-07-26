FROM alloranetwork/allora-inference-base:latest

COPY requirements.txt /app/
RUN pip3 install --requirement /app/requirements.txt

COPY main.py /app/