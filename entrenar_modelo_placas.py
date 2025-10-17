from ultralytics import YOLO

# 1. Carga un modelo base preentrenado
# Puedes usar 'yolov8n.pt' (rápido) o 'yolov8m.pt' (más preciso)
model = YOLO('yolov8n.pt')

# 2. Entrena con tu dataset descargado desde Roboflow
# Asegúrate de que la ruta 'data.yaml' es correcta dentro de la carpeta descargada
# Ejemplo: si descargaste "OCR-1" desde Roboflow, verifica la ruta completa
model.train(
    data='OCR-1/data.yaml',   # ruta al data.yaml dentro de la carpeta del dataset
    epochs=50,               # más épocas = mejor precisión (si tienes tiempo)
    imgsz=640,                # resolución de las imágenes
    batch=8,                  # si tienes GPU puedes subirlo (16 o 32)
    device='cpu',             # usa '0' si tienes GPU CUDA
    name="ocr_placas_v1",     # nombre de la carpeta de resultados
    workers=2,                # reduce errores en Windows
    patience=10               # detiene entrenamiento si no mejora
)

# 3. Exporta los pesos del mejor modelo
model.export(format='pt')