FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Instalar PyTorch CPU (cambiar a GPU si es necesario)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Descargar modelo YOLOv8n por defecto
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Comando por defecto
CMD ["python", "main.py", "--source", "0", "--display"]

