"""
Script para reconocimiento facial en tiempo real.
Compara el rostro de la cámara con una imagen de referencia descargada del bucket.

Uso:
    python reconocimiento_tiempo_real.py

Asegúrate de tener una imagen de referencia en: face/referencia/mi_foto.jpeg
O descarga una del bucket de Supabase primero.
"""

import cv2
import sys
import threading
import time
from pathlib import Path
from collections import deque

# Configuración de rutas
BASE_DIR = Path(__file__).parent
RUTA_IMAGEN_REFERENCIA = BASE_DIR / "referencia" / "mi_foto.jpeg"

# Puedes cambiar esta ruta por la imagen descargada del bucket:
# RUTA_IMAGEN_REFERENCIA = BASE_DIR / "imagenes_descargadas" / "front_xxxxx.jpg"

def main():
    """Función principal para reconocimiento facial en tiempo real."""
    
    # Verificar que existe la imagen de referencia
    if not RUTA_IMAGEN_REFERENCIA.exists():
        print(f"❌ Error: No se encuentra la imagen de referencia en:")
        print(f"   {RUTA_IMAGEN_REFERENCIA}")
        print(f"\n💡 Opciones:")
        print(f"   1. Coloca tu foto en: face/referencia/mi_foto.jpeg")
        print(f"   2. O modifica la variable RUTA_IMAGEN_REFERENCIA en este script")
        return
    
    # Importar DeepFace (debe estar en el venv de deepface)
    try:
        from deepface import DeepFace
        print("✅ DeepFace cargado correctamente")
    except ImportError:
        print("❌ Error: No se puede importar DeepFace")
        print("💡 Asegúrate de ejecutar este script con el Python del venv deepface:")
        print(f"   {BASE_DIR / 'deepface_env' / 'Scripts' / 'python.exe'}")
        return
    
    # Validar imagen de referencia
    try:
        print(f"🔍 Validando imagen de referencia...")
        embedding_ref = DeepFace.represent(
            img_path=str(RUTA_IMAGEN_REFERENCIA), 
            model_name="Facenet512"
        )
        print("✅ Imagen de referencia cargada correctamente")
    except Exception as e:
        print(f"❌ Error cargando imagen de referencia: {e}")
        return
    
    # Iniciar captura de video
    video = cv2.VideoCapture(0)
    
    if not video.isOpened():
        print("❌ Error: No se puede acceder a la cámara")
        return
    
    print("\n" + "="*60)
    print("🎥 RECONOCIMIENTO FACIAL EN TIEMPO REAL")
    print("="*60)
    print("📸 Cámara iniciada correctamente")
    print("🔑 Presiona 'Q' o 'ESC' para salir")
    print("⚡ Modo optimizado con threading")
    print("="*60 + "\n")
    
    frame_counter = 0
    
    # Variables compartidas entre threads
    ultimo_resultado = {"verificado": False, "distancia": 0.9999, "timestamp": 0}
    historial_comparaciones = deque(maxlen=3)  # Últimas 3 comparaciones
    lock = threading.Lock()
    procesando = False
    frame_para_procesar = None
    coincidencias_consecutivas = 0
    
    def procesar_frame_async(frame_rgb, timestamp):
        """Procesa el frame en un hilo separado para no bloquear la UI."""
        nonlocal procesando, ultimo_resultado
        
        try:
            # Realizar verificación facial con ArcFace (MÁS PRECISO que Facenet512)
            result = DeepFace.verify(
                img1_path=frame_rgb,
                img2_path=str(RUTA_IMAGEN_REFERENCIA),
                model_name="ArcFace",  # Modelo más preciso
                enforce_detection=False,
                distance_metric='cosine',
                align=True  # Alinear rostros para mejor precisión
            )
            
            # Aplicar umbral más estricto para mayor precisión
            distancia = result["distance"]
            # ArcFace: umbral recomendado 0.68 (más bajo = más estricto)
            es_coincidencia = distancia < 0.60  # Umbral estricto
            
            with lock:
                ultimo_resultado = {
                    "verificado": es_coincidencia,
                    "distancia": distancia,
                    "timestamp": timestamp,
                    "confianza_raw": result["verified"]
                }
        except Exception as e:
            with lock:
                ultimo_resultado = {
                    "verificado": False,
                    "distancia": 0.9999,
                    "timestamp": timestamp,
                    "error": str(e)[:50]
                }
        finally:
            procesando = False
    
    while True:
        ret, frame = video.read()
        if not ret:
            print("⚠️  No se pudo capturar frame")
            break
        
        frame_counter += 1
        frame_display = frame.copy()
        
        # Lanzar procesamiento en hilo separado cada 30 frames (más espaciado)
        if frame_counter % 30 == 0 and not procesando:
            procesando = True
            # Lanzar thread para procesamiento en background
            thread = threading.Thread(
                target=procesar_frame_async,
                args=(frame.copy(), frame_counter),
                daemon=True
            )
            thread.start()
        
        # Leer último resultado disponible (sin bloquear)
        with lock:
            resultado_actual = ultimo_resultado.copy()
            es_coincidencia = resultado_actual["verificado"]
            distancia = resultado_actual["distancia"]
            confianza = (1 - distancia) * 100
            
            # Agregar al historial solo si es un resultado nuevo
            if resultado_actual["timestamp"] != 0 and (not historial_comparaciones or 
                historial_comparaciones[-1]["timestamp"] != resultado_actual["timestamp"]):
                historial_comparaciones.append(resultado_actual)
        
        # Validación por mayoría de últimas 3 comparaciones (reduce falsos positivos)
        if len(historial_comparaciones) >= 3:
            coincidencias_en_historial = sum(1 for r in historial_comparaciones if r["verificado"])
            es_coincidencia_validada = coincidencias_en_historial >= 2  # Al menos 2 de 3
        else:
            es_coincidencia_validada = es_coincidencia
        
        # Determinar texto y color según resultado validado
        if es_coincidencia_validada and distancia < 0.60:
            texto_principal = "HARRISON :)"
            texto_estado = f"COINCIDENCIA CONFIRMADA ({len(historial_comparaciones)}/3)"
            color = (0, 255, 0)  # Verde
            coincidencias_consecutivas += 1
        else:
            texto_principal = "Desconocido"
            texto_estado = f"SIN COINCIDENCIA ({len(historial_comparaciones)}/3)"
            color = (0, 0, 255)  # Rojo
            coincidencias_consecutivas = 0
        
        # Mostrar información en el frame
        cv2.putText(frame_display, texto_principal, (30, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
        cv2.putText(frame_display, texto_estado, (30, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame_display, f"Confianza: {confianza:.1f}%", (30, 140),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame_display, f"Distancia: {distancia:.4f}", (30, 180),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Indicador de modelo mejorado
        cv2.putText(frame_display, "Modelo: ArcFace (Alta Precision)", (30, frame_display.shape[0] - 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Indicador de procesamiento
        if procesando:
            cv2.putText(frame_display, "[Analizando...]", (30, 220),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Agregar contador de frames
        cv2.putText(frame_display, f"Frame: {frame_counter}", (30, frame_display.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Mostrar frame
        cv2.imshow("Reconocimiento Facial - Tiempo Real", frame_display)
        
        # Detectar tecla presionada (waitKey más corto para mejor respuesta)
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q') or key == ord('Q') or key == 27:  # Q o ESC
            print("\n🛑 Reconocimiento detenido por el usuario")
            break
    
    # Liberar recursos
    video.release()
    cv2.destroyAllWindows()
    print("✅ Recursos liberados correctamente")


if __name__ == "__main__":
    main()
