import cv2
import os
from datetime import datetime
from ultralytics import YOLO

# === CARGAR MODELO YOLO ===
model = YOLO("modelos/detectar-Placa/best.pt")

# Carpetas
CARPETA_ENTRADA = "imagenes_descargadas"
CARPETA_SALIDA = "detecciones"

os.makedirs(CARPETA_SALIDA, exist_ok=True)

def procesar_imagenes_de_carpeta():
    """
    Procesa todas las imágenes nuevas de la carpeta imagenes_descargadas/
    Recorta la placa detectada y la guarda en detecciones/.
    Retorna: la lista de rutas de placas recortadas.
    """

    print("🚗 Procesando imágenes desde:", CARPETA_ENTRADA)

    placas_recortadas = []
    archivos = os.listdir(CARPETA_ENTRADA)

    if not archivos:
        print("⚠ No hay imágenes para procesar.")
        return []

    for nombre in archivos:
        ruta_imagen = os.path.join(CARPETA_ENTRADA, nombre)

        # Solo jpg/png
        if not nombre.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        print(f"🔍 Analizando imagen: {nombre}")
        img = cv2.imread(ruta_imagen)
        if img is None:
            print(f"❌ No se pudo leer {nombre}")
            continue

        # Detectar con YOLO
        results = model(img)

        for result in results:
            boxes = result.boxes

            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])

                # Filtrar por confianza
                if conf >= 0.70:
                    placa_crop = img[y1:y2, x1:x2]

                    # Guardar recorte
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    ruta_salida = os.path.join(
                        CARPETA_SALIDA,
                        f"recorte_{timestamp}_{conf:.2f}.png"
                    )

                    cv2.imwrite(ruta_salida, placa_crop)
                    placas_recortadas.append(ruta_salida)

                    print(f"📸 Placa recortada guardada: {ruta_salida}")

    print("🏁 Procesamiento terminado.")
    return placas_recortadas


if __name__ == "__main__":
    procesar_imagenes_de_carpeta()
