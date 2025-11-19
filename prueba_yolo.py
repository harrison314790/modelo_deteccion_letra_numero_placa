import cv2
import time
import os
import numpy as np
from datetime import datetime
from ultralytics import YOLO

#you Only Look Once

# === CARGAR MODELO ENTRENADO ===
model = YOLO("modelos/detectar-Placa/best.pt")

# === VARIABLES PARA DETECCIÓN DE ESTABILIDAD ===
ultimo_bbox = None
frames_estable = 0
FRAMES_ESTABLES_REQUERIDOS = 2  
UMBRAL_MOVIMIENTO = 20  
ultima_captura = time.time()
TIEMPO_ENTRE_CAPTURAS = 2  

# === CONFIGURAR CÁMARA ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.5)


# === CREAR CARPETA PARA GUARDAR DETECCIONES ===
output_dir = "detecciones"
os.makedirs(output_dir, exist_ok=True)

print("🚗 Iniciando detección de placas con YOLOv8. Capturando 4 imágenes...")

# Contador de imágenes guardadas
imagenes_guardadas = 0
MAX_IMAGENES = 5

try:
    while imagenes_guardadas < MAX_IMAGENES:
        # Leer frame de la cámara
        ret, frame = cap.read()
        if not ret:
            print("Error al leer la cámara")
            break

        # Realizar la detección
        results = model(frame)
        
        # Dibujar las detecciones en el frame y guardar recortes
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Obtener coordenadas y confianza
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                # Solo procesar si la confianza es mayor a 0.85 (85%)
                if conf >= 0.85:
                    bbox_actual = (x1, y1, x2, y2)
                    
                    # Verificar estabilidad
                    if ultimo_bbox is not None:
                        # Calcular la diferencia en la posición
                        diff_x = abs(bbox_actual[0] - ultimo_bbox[0])
                        diff_y = abs(bbox_actual[1] - ultimo_bbox[1])
                        
                        # Si la placa está estable (poco movimiento)
                        if diff_x < UMBRAL_MOVIMIENTO and diff_y < UMBRAL_MOVIMIENTO:
                            frames_estable += 1
                        else:
                            frames_estable = 0
                    
                    ultimo_bbox = bbox_actual
                    
                    # Si la placa ha estado estable por suficientes frames
                    if frames_estable >= FRAMES_ESTABLES_REQUERIDOS:
                        tiempo_actual = time.time()
                        # Solo capturar si ha pasado suficiente tiempo desde la última captura
                        if tiempo_actual - ultima_captura >= TIEMPO_ENTRE_CAPTURAS:
                            # Añadir un pequeño margen alrededor de la placa
                            margen = 5  # Reducido el margen para evitar ruido extra
                            y1_margin = max(0, y1 - margen)
                            y2_margin = min(frame.shape[0], y2 + margen)
                            x1_margin = max(0, x1 - margen)
                            x2_margin = min(frame.shape[1], x2 + margen)
                            
                            # Recortar la región de la placa con margen
                            placa_recortada = frame[y1_margin:y2_margin, x1_margin:x2_margin]
                            
                            # Redimensionar a un tamaño estándar manteniendo la proporción
                            alto_deseado = 150  # altura reducida para mantener mejor calidad
                            ratio = alto_deseado / placa_recortada.shape[0]
                            ancho_nuevo = int(placa_recortada.shape[1] * ratio)
                            placa_recortada = cv2.resize(placa_recortada, (ancho_nuevo, alto_deseado), 
                                                       interpolation=cv2.INTER_AREA)
                            
                            # Guardar la imagen mejorada
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            conf_str = f"{conf:.2f}"
                            nombre_archivo = f"placa_{timestamp}_{conf_str}.png"
                            ruta_completa = os.path.join(output_dir, nombre_archivo)
                            cv2.imwrite(ruta_completa, placa_recortada)
                            print(f"✅ Nueva placa guardada: {nombre_archivo} (Confianza: {conf:.2%})")
                            
                            # Actualizar tiempo de última captura
                            ultima_captura = tiempo_actual
                    
                    # Esperar 1 segundo entre capturas
                    time.sleep(1)
                
                # Dibujar rectángulo y mostrar confianza con color según el nivel
                if conf >= 0.85:
                    if frames_estable >= FRAMES_ESTABLES_REQUERIDOS:
                        color = (0, 255, 0)  # Verde brillante cuando está estable
                    elif frames_estable > 0:
                        # Gradiente de amarillo a verde según la estabilidad
                        intensidad = min(frames_estable / FRAMES_ESTABLES_REQUERIDOS, 1.0)
                        color = (0, 255, int(255 * (1 - intensidad)))
                    else:
                        color = (0, 255, 255)  # Amarillo cuando está en movimiento
                elif conf >= 0.70:
                    color = (0, 255, 255)  # Amarillo para media confianza
                else:
                    color = (0, 0, 255)  # Rojo para baja confianza
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Mostrar confianza y estado de estabilidad
                estado = f"{conf:.2%}"
                if conf >= 0.85:
                    estado += f" ({frames_estable}/{FRAMES_ESTABLES_REQUERIDOS})"
                cv2.putText(frame, estado, (x1, y1-10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Mostrar el frame
        cv2.imshow("Deteccion de Placas", frame)

        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    if imagenes_guardadas >= MAX_IMAGENES:
        print("✅ Se han capturado las 4 imágenes correctamente.")
    print("Programa finalizado.")

# === BUCLE PRINCIPAL ===
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ No se pudo acceder a la cámara.")
            break

        # Tiempo de inicio
        start_time = time.time()

        # Detección con YOLO
        results = model.predict(source=frame, conf=0.5, verbose=False)

        # Procesar resultados
        detecciones = results[0].boxes.xyxy.cpu().numpy() if len(results) > 0 else []
        nombres = results[0].names

        if len(detecciones) > 0:
            for i, box in enumerate(detecciones):
                x1, y1, x2, y2 = map(int, box[:4])
                conf = box[4]
                cls = int(box[5])
                etiqueta = nombres.get(cls, "placa")

                # Recortar la placa detectada
                placa_crop = frame[y1:y2, x1:x2]

                # Guardar imagen recortada
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                nombre_archivo = f"{output_dir}/placa_{timestamp}.png"
                cv2.imwrite(nombre_archivo, placa_crop)
                print(f"📸 Placa detectada ({etiqueta}, conf={conf:.2f}) guardada en: {nombre_archivo}")

        # Calcular FPS
        fps = 1.0 / (time.time() - start_time)
        print(f"⏱️ FPS: {fps:.2f}")

except KeyboardInterrupt:
    print("\n🛑 Detección interrumpida manualmente.")

# === LIMPIAR ===
cap.release()
print("🟢 Cámara cerrada correctamente.")

