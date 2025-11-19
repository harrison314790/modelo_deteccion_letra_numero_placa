from ultralytics import YOLO
import cv2, os, json
import numpy as np


# ============================================================
# === Cargar base de datos de placas registradas ===
# ============================================================

with open("placas_registradas.json", "r", encoding="utf-8") as f:
    placas_registradas = json.load(f)

print("📘 Base de datos cargada correctamente:", placas_registradas)

# ============================================================
# === Rutas ===
# ============================================================

MODELO_PATH = "modelos/leer_numero_placas/best.pt"
CARPETA_IMAGENES = "detecciones"

# ============================================================
# === Cargar modelo OCR YOLO ===
# ============================================================

model = YOLO(MODELO_PATH)
print("✅ Modelo cargado correctamente.\n")

# ============================================================
# === Corrección del orden de clases del dataset (Roboflow) ===
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
# === Función para corregir placa al formato colombiano ===
# ============================================================

def corregir_formato_colombia(placa):
    placa = list(placa)

    # --- PRIMEROS 3 → DEBEN SER LETRAS ---
    for i in range(min(3, len(placa))):
        c = placa[i]

        if c.isdigit():
            if c == "0":
                placa[i] = "O"      # 0 → O
            else:
                placa[i] = ""       # eliminar números en zona de letras

    # --- ÚLTIMOS 3 → DEBEN SER NÚMEROS ---
    conversion_letra_a_numero = {
        "O": "0",
        "I": "1",
        "Z": "2",
        "B": "8",
        "S": "5"
    }

    for i in range(3, len(placa)):
        c = placa[i]

        if c.isalpha():  # letra donde deberían ir números
            placa[i] = conversion_letra_a_numero.get(c.upper(), "")

    return "".join(placa)


# ============================================================
# === Procesar imágenes ===
# ============================================================

contador = 0

for archivo in os.listdir(CARPETA_IMAGENES):
    if not archivo.lower().endswith((".png", ".jpg", ".jpeg")):
        continue

    ruta_img = os.path.join(CARPETA_IMAGENES, archivo)
    contador += 1
    print(f"\n📸  -{contador}- Procesando: {archivo}")

    results = model.predict(source=ruta_img, conf=0.5, verbose=False)
    r = results[0]
    boxes = r.boxes

    if len(boxes) == 0:
        print("⚠️ No se detectaron caracteres.\n")
        continue

    # ------------------------------------------------------------
    # Mostrar detecciones sin ordenar
    # ------------------------------------------------------------
    print("\n🔍 Detecciones del modelo (sin ordenar):")
    detecciones = []

    for box in boxes:
        clase_pred = int(box.cls[0])          
        clase_real = mapa_indices[clase_pred] 
        conf = float(box.conf[0])
        x1 = float(box.xyxy[0][0])            
        char = class_map_real.get(clase_real, '?')

        print(f"   • Clase modelo: {clase_pred:02d} → Real: {clase_real:02d} ({char}) | Conf: {conf:.2f} | X: {x1:.0f}")

        detecciones.append((x1, char, conf))

    # ------------------------------------------------------------
    # Ordenar caracteres de izquierda a derecha
    # ------------------------------------------------------------
    detecciones.sort(key=lambda x: x[0])

    # Placa detectada cruda
    placa_raw = "".join([d[1] for d in detecciones])

    # Corregir según formato colombiano
    placa = corregir_formato_colombia(placa_raw)

    print(f"\n🧩 Placa detectada (ordenada): {placa_raw}")
    print(f"🔧 Placa corregida: {placa}")

    # ------------------------------------------------------------
    # VALIDACIÓN CONTRA JSON
    # ------------------------------------------------------------
    if placa in placas_registradas:
        propietario = placas_registradas[placa]["propietario"]
        print(f"\n🟢 VALIDADA: {placa} → Propietario: {propietario}")
        mensaje = f"Propietario: {propietario}"
        color = (0, 180, 0)
    else:
        print(f"\n🔴 NO REGISTRADA: {placa}")
        mensaje = f"No registrada: {placa}"
        color = (0, 0, 255)

    # ========================================
    #  CREAR IMAGEN MÁS GRANDE PARA MOSTRAR TEXTO
    # =======================================
    img_resultado = results[0].plot()
    h, w = img_resultado.shape[:2]
    panel_height = 150

    panel = 255 * np.ones((h + panel_height, w, 3), dtype=np.uint8)
    panel[0:h, 0:w] = img_resultado


    cv2.putText(panel, f"Detectada: {placa}", (20, h + 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)

    cv2.putText(panel, mensaje, (20, h + 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 1)

    cv2.imshow("Validación de Placa", panel)
    key = cv2.waitKey(3000)
    if key & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
print("\n✅ Prueba finalizada.")

