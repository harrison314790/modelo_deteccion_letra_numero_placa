from ultralytics import YOLO
import cv2, os
import numpy as np

MODELO_PATH = "modelos/leer_numero_placas/best.pt"

model = YOLO(MODELO_PATH)

# ============================================================
# === Mapa de clases (corrección Roboflow) ===
# ============================================================

mapa_indices = {
    0:0,1:1,2:10,3:11,4:12,5:13,6:14,7:15,8:16,9:17,
    10:18,11:19,12:2,13:20,14:21,15:22,16:23,17:24,18:25,19:26,
    20:27,21:28,22:29,23:3,24:30,25:31,26:32,27:33,28:34,29:35,
    30:4,31:5,32:6,33:7,34:8,35:9
}

class_map_real = {
    0:'0',1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',
    10:'A',11:'B',12:'C',13:'D',14:'E',15:'F',16:'G',17:'H',18:'I',19:'J',
    20:'K',21:'L',22:'M',23:'N',24:'P',25:'Q',26:'R',27:'S',28:'T',
    29:'U',30:'V',31:'W',32:'X',33:'Y',34:'Z',
    35:'1'
}

# ============================================================
# === Corrección de formato colombiano ===
# ============================================================

def corregir_formato_colombia(placa):
    placa = list(placa)

    # Primeras 3 letras → deben ser letras
    for i in range(min(3, len(placa))):
        c = placa[i]
        if c.isdigit():
            placa[i] = "O" if c == "0" else ""

    # Últimos 3 caracteres → deben ser números
    conversion = {"O": "0", "I": "1", "Z": "2", "B": "8", "S": "5"}

    for i in range(3, len(placa)):
        c = placa[i]
        if c.isalpha():
            placa[i] = conversion.get(c.upper(), "")

    return "".join(placa)


# ============================================================
# === FUNCION PRINCIPAL — Procesar UNA imagen ===
# ============================================================

def leer_placa(ruta_img):
    """
    Procesa una imagen recortada de placa y devuelve el texto detectado.
    """

    results = model.predict(source=ruta_img, conf=0.5, verbose=False)
    r = results[0]
    boxes = r.boxes

    if len(boxes) == 0:
        print("⚠ No se detectaron caracteres en la placa.")
        return None

    detecciones = []

    for box in boxes:
        clase_pred = int(box.cls[0])
        clase_real = mapa_indices[clase_pred]
        conf = float(box.conf[0])
        x1 = float(box.xyxy[0][0])
        char = class_map_real.get(clase_real, "?")

        detecciones.append((x1, char, conf))

    detecciones.sort(key=lambda x: x[0])
    placa_raw = "".join([x[1] for x in detecciones])
    placa = corregir_formato_colombia(placa_raw)
    print(f"Placa corregida: {placa}")

    return placa


if __name__ == "__main__":
    print("Este archivo no debe ejecutarse directamente.")


