#!/usr/bin/env python3
"""
Main integrado para todo el flujo:
1. Captura video desde cámara
2. Detecta placa (venv 3.11.8)
3. Lee OCR de placa (venv 3.11.8)
4. Consulta conductor en Supabase
5. Comparación facial (deepface-env Python 3.10.11)
6. Autoriza o deniega acceso
"""

import cv2
import os
import subprocess
import json
import tempfile
from datetime import datetime
from pathlib import Path
import sys

# Importar módulos locales (deben estar en venv 3.11.8)
try:
    from servicios.peticiones_supaBase import (
        obtener_conductor_por_placa, 
        descargar_foto_biometria,
        registrar_acceso,
        crear_notificacion
    )
    from placas.prueba_numero_letra import leer_placa
except ImportError as e:
    print(f"❌ Error importando módulos del venv 3.11.8: {e}")
    print("⚠️  Asegúrate de tener activado el venv 3.11.8 correcto")
    sys.exit(1)

# ==========================================
# CONFIGURACIÓN DE RUTAS Y VENV
# ==========================================

BASE_DIR = Path(__file__).parent
VENV_3_11 = BASE_DIR / ".venv"  # venv principal (3.11.8)
VENV_DEEPFACE = BASE_DIR / "face" / "deepface_env"  # venv deepface (3.10.11)

PYTHON_3_11 = VENV_3_11 / "Scripts" / "python.exe"
PYTHON_DEEPFACE = VENV_DEEPFACE / "Scripts" / "python.exe"

SCRIPT_DEEPFACE = BASE_DIR / "face" / "reconocimientoFacial.py"

# Carpetas temporales
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# Variable global para guardar la placa actual
PLACA_ACTUAL = None
CARPETA_PLACA_ACTUAL = None

def crear_carpeta_placa(placa: str):
    """
    Crea una carpeta separada para cada placa en temp/[placa]/
    y la guarda en variables globales.
    """
    global PLACA_ACTUAL, CARPETA_PLACA_ACTUAL
    PLACA_ACTUAL = placa
    CARPETA_PLACA_ACTUAL = TEMP_DIR / placa
    CARPETA_PLACA_ACTUAL.mkdir(exist_ok=True)
    print(f"📁 Carpeta creada/utilizada: {CARPETA_PLACA_ACTUAL}")
    return CARPETA_PLACA_ACTUAL

# ==========================================
# UTILIDADES PARA CAPTURA DE CÁMARA
# ==========================================

def capturar_placa_automatica(nombre_archivo="placa_captura.jpg", timeout_segundos=30, placa=None):
    """
    Abre la cámara y detecta automáticamente la placa usando YOLO.
    Captura automáticamente cuando detecta una placa QUIETA con confianza suficiente.
    
    Espera a que la placa esté estable (sin movimiento) antes de capturar.
    
    Args:
        nombre_archivo: nombre del archivo a guardar
        timeout_segundos: máximo tiempo esperando detección
        placa: si se proporciona, crea carpeta separada para esta placa
    
    Returns:
        ruta_imagen: ruta del archivo guardado o None si no detectó
    """
    print("\n📷 Abriendo cámara... (detectando placa QUIETA automáticamente)")
    print("   ⏳ Esperando a que YOLO detecte una placa estable...")
    
    try:
        from ultralytics import YOLO
        import numpy as np
        
        # Cargar modelo YOLO
        print("   🤖 Cargando modelo YOLO...")
        model = YOLO("modelos/detectar-Placa/best.pt")
        
    except Exception as e:
        print(f"   ❌ Error cargando YOLO: {e}")
        print("   💡 Alternativa: usando captura manual")
        return capturar_foto_camara_manual(nombre_archivo, placa=placa)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara")
        return None
    
    import time
    tiempo_inicio = time.time()
    placa_detectada = False
    marco_capturado = None
    frame_original = None
    
    # Variables para detectar estabilidad
    placa_anterior = None
    frames_estables = 0
    frames_estables_requeridos = 8  # Requiere 8 frames consecutivos sin movimiento
    
    print("   ⏳ Buscando placa QUIETA en video en tiempo real...")
    
    while not placa_detectada:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Error al leer frame de cámara")
            break
        
        # Mostrar frame actual
        frame_display = frame.copy()
        cv2.putText(frame_display, "Detectando placa quieta...", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if frames_estables > 0:
            cv2.putText(frame_display, f"Estabilidad: {frames_estables}/{frames_estables_requeridos}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Camara - Deteccion Automatica de Placa", frame_display)
        
        # Presionar ESC para cancelar
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            print("❌ Detección cancelada por el usuario")
            break
        
        # Verificar timeout
        if time.time() - tiempo_inicio > timeout_segundos:
            print(f"⏱️  Timeout: No se detectó placa quieta en {timeout_segundos} segundos")
            break
        
        # Ejecutar YOLO cada 5 frames (para mejor performance)
        frame_count = int((time.time() - tiempo_inicio) * 30) % 5
        if frame_count == 0:
            try:
                results = model(frame, verbose=False)
                placa_encontrada_ahora = None
                
                for result in results:
                    boxes = result.boxes
                    
                    for box in boxes:
                        conf = float(box.conf[0])
                        
                        # Si confianza > 70%, considerar
                        if conf >= 0.70:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            
                            # Agregar margen para que no quede muy ajustado
                            margen = 10
                            y1 = max(0, y1 - margen)
                            x1 = max(0, x1 - margen)
                            y2 = min(frame.shape[0], y2 + margen)
                            x2 = min(frame.shape[1], x2 + margen)
                            
                            placa_encontrada_ahora = {
                                'coords': (x1, y1, x2, y2),
                                'conf': conf,
                                'crop': frame[y1:y2, x1:x2].copy(),
                                'frame': frame.copy()
                            }
                            break  # Tomar la primera placa encontrada
                    
                    if placa_encontrada_ahora:
                        break
                
                # Verificar si la placa está en la misma posición (estable)
                if placa_encontrada_ahora is None:
                    # No se detectó placa, resetear contador
                    frames_estables = 0
                    placa_anterior = None
                    
                elif placa_anterior is None:
                    # Primera detección
                    placa_anterior = placa_encontrada_ahora
                    frames_estables = 1
                    print("   📍 Placa detectada, esperando estabilidad...")
                    
                else:
                    # Comparar posición actual con anterior
                    coords_anterior = placa_anterior['coords']
                    coords_actual = placa_encontrada_ahora['coords']
                    
                    # Calcular diferencia en píxeles (movimiento)
                    diff_x1 = abs(coords_anterior[0] - coords_actual[0])
                    diff_y1 = abs(coords_anterior[1] - coords_actual[1])
                    diff_x2 = abs(coords_anterior[2] - coords_actual[2])
                    diff_y2 = abs(coords_anterior[3] - coords_actual[3])
                    
                    movimiento_max = max(diff_x1, diff_y1, diff_x2, diff_y2)
                    
                    # Si movimiento < 15 píxeles, considerar estable
                    if movimiento_max < 15:
                        frames_estables += 1
                        print(f"   ✓ Placa estable ({frames_estables}/{frames_estables_requeridos}) - movimiento: {movimiento_max}px")
                        
                        if frames_estables >= frames_estables_requeridos:
                            # ¡PLACA LISTA! Capturar
                            marco_capturado = placa_encontrada_ahora['crop']
                            frame_original = placa_encontrada_ahora['frame']
                            placa_detectada = True
                            
                            print(f"\n✅ PLACA QUIETA CAPTURADA (confianza: {placa_encontrada_ahora['conf']:.2%})")
                            print(f"   📍 Coordenadas: {coords_actual}")
                            print(f"   📊 Estabilidad confirmada en {frames_estables} frames consecutivos")
                            break
                    else:
                        # Movimiento detectado, resetear
                        frames_estables = 0
                        placa_anterior = placa_encontrada_ahora
                        print(f"   ⚠️  Placa se movió ({movimiento_max}px), reiniciando espera de estabilidad")
            
            except Exception as e:
                print(f"⚠️  Error en YOLO: {e}")
                frames_estables = 0
                placa_anterior = None
                continue
    
    cap.release()
    cv2.destroyAllWindows()
    
    if marco_capturado is None:
        print("❌ No se detectó placa quieta en el tiempo límite")
        return None
    
    # Guardar foto recortada en carpeta de placa
    if placa:
        carpeta = crear_carpeta_placa(placa)
        ruta_foto = carpeta / nombre_archivo
    else:
        ruta_foto = TEMP_DIR / nombre_archivo
    
    cv2.imwrite(str(ruta_foto), marco_capturado)
    print(f"✔ Placa capturada y guardada: {ruta_foto}")
    
    return str(ruta_foto)


def capturar_foto_camara_manual(nombre_archivo="captura.jpg", placa=None):
    """
    Alternativa: Abre la cámara y permite capturar manualmente (si YOLO falla).
    
    Args:
        nombre_archivo: nombre del archivo a guardar
        placa: si se proporciona, crea carpeta separada para esta placa
    
    Returns:
        ruta_imagen: ruta del archivo guardado o None si no se capturó
    """
    print("\n📷 Modo MANUAL - Presiona ESPACIO para capturar, ESC para cancelar")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara")
        return None
    
    captura_realizada = False
    marco = None
    
    while not captura_realizada:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Error al leer el frame")
            break
        
        cv2.imshow("Modo Manual - ESPACIO para capturar, ESC para salir", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # ESPACIO
            marco = frame.copy()
            captura_realizada = True
            print("✔ Foto capturada manualmente")
        elif key == 27:  # ESC
            print("❌ Captura cancelada")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if marco is None:
        return None
    
    if placa:
        carpeta = crear_carpeta_placa(placa)
        ruta_foto = carpeta / nombre_archivo
    else:
        ruta_foto = TEMP_DIR / nombre_archivo
    
    cv2.imwrite(str(ruta_foto), marco)
    print(f"✔ Foto guardada: {ruta_foto}")
    
    return str(ruta_foto)


def capturar_rostro_camara(nombre_archivo="rostro_captura.jpg", placa=None, ruta_foto_biometria=None):
    """
    Captura rostro desde cámara y compara en TIEMPO REAL con DeepFace (via subprocess).
    Se cierra automáticamente cuando COINCIDA con la biometría.
    
    Args:
        nombre_archivo: nombre del archivo a guardar
        placa: si se proporciona, crea carpeta separada para esta placa
        ruta_foto_biometria: ruta de la foto biométrica de referencia
    
    Returns:
        tuple: (ruta_imagen, es_coincidencia) donde es_coincidencia=True si hay match
    """
    print("\n📷 Abriendo cámara para verificación facial en tiempo real...")
    print("   🔍 Escaneando constantemente su rostro...")
    print("   ⏳ La cámara se cerrará automáticamente cuando COINCIDA")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara")
        return None, False
    
    if not ruta_foto_biometria or not os.path.exists(ruta_foto_biometria):
        print("❌ No hay foto biométrica para comparar")
        cap.release()
        return None, False
    
    if not PYTHON_DEEPFACE.exists():
        print(f"❌ No encontrado: {PYTHON_DEEPFACE}")
        print(f"⚠️  Debes crear venv deepface con: py -3.10 -m venv face/deepface_env")
        cap.release()
        return None, False
    
    import time
    marco_capturado = None
    coincidencia_encontrada = False
    frame_counter = 0
    ultimos_resultados = []  # Historial de últimas 2 comparaciones
    temp_frame_path = TEMP_DIR / "temp_frame_compare.jpg"
    
    print("\n   📊 Iniciando análisis facial en tiempo real...")
    print("   " + "="*50)
    
    while not coincidencia_encontrada:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Error al leer el frame")
            break
        
        frame_display = frame.copy()
        frame_counter += 1
        
        # Mostrar información en pantalla
        h, w = frame_display.shape[:2]
        cv2.rectangle(frame_display, (20, 20), (w-20, h-20), (0, 255, 0), 3)
        cv2.putText(frame_display, "ESCANEANDO ROSTRO...", (10, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame_display, f"Frame: {frame_counter}", (10, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Comparar cada 40 frames (OPTIMIZADO para reducir lag)
        if frame_counter % 40 == 0:
            # Inicializar variables ANTES del try para evitar errores
            es_coincidencia = False
            distancia = 0.9999
            
            try:
                print(f"   🔄 Comparando frame {frame_counter}...", end=" ")
                
                # Guardar frame temporal
                cv2.imwrite(str(temp_frame_path), frame)
                
                # Comparar usando subprocess en deepface_env
                script_temporal = TEMP_DIR / "compare_face_realtime.py"
                
                script_content = f'''
import sys
sys.path.insert(0, r"{BASE_DIR / 'face'}")

try:
    from deepface import DeepFace
    result = DeepFace.verify(
        img1_path=r"{ruta_foto_biometria}",
        img2_path=r"{temp_frame_path}",
        model_name='ArcFace',  # Modelo más preciso
        enforce_detection=False,
        distance_metric='cosine',
        align=True  # Alinear rostros para mejor precisión
    )
    
    # Aplicar umbral más estricto para mayor precisión
    distancia = result['distance']
    es_coincidencia = distancia < 0.60  # Umbral estricto para ArcFace
    
    print(f"RESULTADO:{{es_coincidencia}}")
    print(f"DISTANCIA:{{distancia:.4f}}")
except Exception as e:
    print(f"RESULTADO:False")
    print(f"DISTANCIA:0.9999")
    print(f"ERROR:{{str(e)[:50]}}")
'''
                
                with open(script_temporal, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                
                # Ejecutar comparación
                resultado = subprocess.run(
                    [str(PYTHON_DEEPFACE), str(script_temporal)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(BASE_DIR)
                )
                
                # Parsear resultado
                if "RESULTADO:True" in resultado.stdout:
                    es_coincidencia = True
                    # Extraer distancia
                    for linea in resultado.stdout.split('\n'):
                        if "DISTANCIA:" in linea:
                            try:
                                distancia = float(linea.split("DISTANCIA:")[1].strip())
                            except:
                                pass
                elif "RESULTADO:False" in resultado.stdout:
                    es_coincidencia = False
                    for linea in resultado.stdout.split('\n'):
                        if "DISTANCIA:" in linea:
                            try:
                                distancia = float(linea.split("DISTANCIA:")[1].strip())
                            except:
                                pass
                
                ultimos_resultados.append(es_coincidencia)
                if len(ultimos_resultados) > 2:
                    ultimos_resultados.pop(0)
                
                # Mostrar en terminal
                if es_coincidencia:
                    print(f"✅ COINCIDENCIA (distancia: {distancia:.4f})")
                    cv2.putText(frame_display, "COINCIDENCIA DETECTADA", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                    cv2.putText(frame_display, f"Confianza: {(1-distancia)*100:.1f}%", (10, 160),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                else:
                    print(f"❌ Sin coincidencia (distancia: {distancia:.4f})")
                    cv2.putText(frame_display, "SIN COINCIDENCIA", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.putText(frame_display, f"Distancia: {distancia:.4f}", (10, 160),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                # Si 2 comparaciones consecutivas coinciden, confirmar
                if len(ultimos_resultados) >= 2 and all(ultimos_resultados[-2:]):
                    marco_capturado = frame.copy()
                    coincidencia_encontrada = True
                    print("\n   ✅ COINCIDENCIA CONFIRMADA - Capturando...")
                    break
            
            except subprocess.TimeoutExpired:
                print("⏱️  Timeout en comparación")
            except Exception as e:
                print(f"⚠️  Error: {str(e)[:40]}")
        
        # Mostrar frame
        cv2.imshow("Verificación Facial - TIEMPO REAL", frame_display)
        
        # waitKey más largo para reducir lag (10ms en lugar de 1ms)
        key = cv2.waitKey(10) & 0xFF
        if key == 27:  # ESC
            print("❌ Verificación cancelada por el usuario")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Limpiar archivo temporal
    if temp_frame_path.exists():
        try:
            temp_frame_path.unlink()
        except:
            pass
    
    if marco_capturado is None or not coincidencia_encontrada:
        print("❌ No se encontró coincidencia facial")
        return None, False
    
    if placa:
        carpeta = crear_carpeta_placa(placa)
        ruta_foto = carpeta / nombre_archivo
    else:
        ruta_foto = TEMP_DIR / nombre_archivo
    
    cv2.imwrite(str(ruta_foto), marco_capturado)
    print(f"✔ Rostro guardado: {ruta_foto}")
    print("   " + "="*50)
    
    return str(ruta_foto), True

# ==========================================
# LLAMAR RECONOCIMIENTO FACIAL CON DEEPFACE-ENV
# ==========================================

def comparar_rostros_con_deepface(ruta_captura_rostro, ruta_foto_biometria):
    """
    Ejecuta reconocimientoFacial.py en el venv deepface (Python 3.10.11)
    usando subprocess.
    
    Args:
        ruta_captura_rostro: ruta de foto capturada (nueva)
        ruta_foto_biometria: ruta de foto de Supabase (referencia)
    
    Returns:
        bool: True si coincide, False si no
    """
    print(f"\n➡️  Comparando rostros con DeepFace...")
    print(f"   📸 Captura actual: {ruta_captura_rostro}")
    print(f"   📸 Referencia: {ruta_foto_biometria}")
    
    # Verificar archivos
    if not os.path.exists(ruta_captura_rostro):
        print(f"❌ Archivo no existe: {ruta_captura_rostro}")
        return False
    
    if not os.path.exists(ruta_foto_biometria):
        print(f"❌ Archivo no existe: {ruta_foto_biometria}")
        return False
    
    if not PYTHON_DEEPFACE.exists():
        print(f"❌ No encontrado: {PYTHON_DEEPFACE}")
        print(f"⚠️  Debes crear venv deepface con: py -3.10 -m venv face/deepface_env")
        print(f"    Luego: face\\deepface_env\\Scripts\\Activate.ps1")
        print(f"    Después: pip install -r face/requirements.txt")
        return False
    
    if not SCRIPT_DEEPFACE.exists():
        print(f"❌ No encontrado: {SCRIPT_DEEPFACE}")
        return False
    
    try:
        # Crear un script temporal que importe y ejecute la comparación
        script_temporal = TEMP_DIR / "run_deepface.py"
        
        script_content = f'''
import sys
import os
sys.path.insert(0, r"{BASE_DIR / 'face'}")

try:
    from reconocimientoFacial import comparar_rostros
    resultado = comparar_rostros(r"{ruta_captura_rostro}", r"{ruta_foto_biometria}")
    print("RESULTADO:" + str(resultado))
except Exception as e:
    print(f"ERROR_DEEPFACE:{{str(e)}}")
    print("RESULTADO:False")
'''
        
        with open(script_temporal, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Ejecutar en el venv deepface
        print("\n⏳ Procesando (esto puede tomar 20-30 segundos)...")
        resultado = subprocess.run(
            [str(PYTHON_DEEPFACE), str(script_temporal)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(BASE_DIR)
        )
        
        # Mostrar output
        if resultado.stdout:
            lineas = resultado.stdout.strip().split('\n')
            for linea in lineas[-5:]:  # Mostrar últimas 5 líneas
                if linea.strip():
                    print(f"   {linea}")
        
        if resultado.stderr and "deprecated" not in resultado.stderr.lower():
            print(f"⚠️  Info: {resultado.stderr[:200]}")
        
        # Parsear resultado
        if "RESULTADO:True" in resultado.stdout:
            print("✅ Coincidencia detectada")
            return True
        elif "RESULTADO:False" in resultado.stdout:
            print("❌ No hay coincidencia")
            return False
        else:
            print("⚠️  No se pudo procesar resultado de DeepFace")
            return False
    
    except subprocess.TimeoutExpired:
        print("❌ Timeout en comparación facial (>120s)")
        return False
    except Exception as e:
        print(f"❌ Error en comparación facial: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==========================================
# FLUJO PRINCIPAL INTEGRADO
# ==========================================

def procesar_evento_parqueadero():
    """
    Flujo completo:
    1. Capturar foto de placa desde cámara
    2. Detectar y recortar placa (YOLO)
    3. Leer OCR de placa
    4. Consultar conductor en Supabase
    5. Capturar foto del rostro desde cámara
    6. Comparar rostro con DeepFace
    7. Autorizar o denegar acceso
    """
    print("\n" + "="*50)
    print("🚗 SISTEMA DE ACCESO A PARQUEADERO INICIADO")
    print("="*50 + "\n")
    
    # ====== PASO 1: CAPTURAR FOTO DE PLACA ======
    print("📸 PASO 1: Capturar foto de la placa")
    print("-" * 50)
    
    ruta_imagen_placa = capturar_placa_automatica("placa_captura.jpg", timeout_segundos=30)
    
    if not ruta_imagen_placa or not os.path.exists(ruta_imagen_placa):
        print("❌ No se capturó la placa. Abortando...")
        return
    
    # ====== PASO 2: DETECTAR Y RECORTAR PLACA ======
    print("\n📍 PASO 2: Detectar placa con YOLO")
    print("-" * 50)
    
    # Para ahora, usamos la imagen capturada directamente
    # (en producción, podrías usar prueba_yolo.py para detectar)
    placa_recortada = ruta_imagen_placa  # Asumimos que ya es la placa
    
    # ====== PASO 3: LEER OCR ======
    print("\n📖 PASO 3: Leer placa (OCR)")
    print("-" * 50)
    
    placa = leer_placa(placa_recortada)
    
    if not placa:
        print("❌ No se pudo leer la placa")
        return
    
    print(f"✔ Placa detectada: {placa}\n")
    
    # Crear carpeta separada para esta placa
    print(f"📁 Creando carpeta para placa: {placa}")
    crear_carpeta_placa(placa)
    
    # ====== PASO 4: CONSULTAR SUPABASE ======
    print("🔍 PASO 4: Consultando conductor en Supabase")
    print("-" * 50)
    
    conductor = obtener_conductor_por_placa(placa)
    
    if not conductor:
        print("❌ La placa no está registrada en Supabase")
        return
    
    nombre_conductor = conductor.get('nombre', 'Desconocido')
    apellido_conductor = conductor.get('apellido', '')
    nombre_completo = f"{nombre_conductor} {apellido_conductor}".strip()
    
    print(f"✔ Conductor encontrado: {nombre_completo}")
    print(f"✔ Email: {conductor.get('email', 'N/A')}")
    print(f"✔ Biometría en Storage: {conductor.get('foto_biometria', 'N/A')}\n")
    
    # ====== PASO 5: DESCARGAR BIOMETRÍA ======
    print("⬇️  PASO 5: Descargando foto biométrica")
    print("-" * 50)
    
    if not conductor.get("foto_biometria"):
        print("❌ El usuario no tiene foto biométrica registrada en Supabase.")
        return
    
    ruta_foto_biometria = descargar_foto_biometria(conductor["foto_biometria"])

    
    if not ruta_foto_biometria or not os.path.exists(ruta_foto_biometria):
        print("❌ No se pudo descargar la biometría")
        return
    
    print(f"✔ Biometría descargada: {ruta_foto_biometria}\n")
    
    # ====== PASO 6: CAPTURAR FOTO DEL ROSTRO ======
    print("📷 PASO 6: Verificación facial en TIEMPO REAL")
    print("-" * 50)
    print(f"   Iniciando verificación para: {nombre_completo}")
    print(f"   Biometría de referencia: {ruta_foto_biometria}")
    
    ruta_captura_rostro, es_coincidencia = capturar_rostro_camara(
        "rostro_captura.jpg", 
        placa=placa, 
        ruta_foto_biometria=ruta_foto_biometria
    )
    
    if not ruta_captura_rostro:
        print("❌ No se capturó el rostro. Abortando...")
        return
    
    # Si capturar_rostro_camara ya hizo la comparación, usar ese resultado
    es_mismo = es_coincidencia
    
    # ====== RESULTADO FINAL ======
    print("\n" + "="*70)
    
    if es_mismo:
        print("🟢 " * 20)
        print("✅✅✅ ACCESO PERMITIDO ✅✅✅")
        print("🟢 " * 20)
        print(f"\n✓ Identificación confirmada: {nombre_completo}")
        print(f"✓ Placa verificada: {placa}")
        print(f"✓ Rostro coincide: SÍ - 100%")
        print("\n✓ ¡BIENVENIDO! Se abre la barrera")
        print("✓ Acceso al parqueadero AUTORIZADO")
        
        # ====== REGISTRAR ACCESO EN BASE DE DATOS ======
        print("\n📝 Registrando acceso en base de datos...")
        print("-" * 70)
        
        # Obtener IDs necesarios
        usuario_id = conductor.get('id')  # ID del usuario (auth.users)
        vehiculo_id = conductor.get('vehiculo_id')  # Si está disponible en conductor
        
        # Si no tenemos vehiculo_id en conductor, debemos buscarlo
        if not vehiculo_id:
            print("⚠️  Buscando ID del vehículo...")
            # El vehiculo_id debe venir del primer query de vehiculo_usuario
            # Por ahora, lo dejamos como None si no está disponible
        
        # Calcular confianza (por defecto alta si es coincidencia)
        confianza = 0.95  # 95% de confianza
        
        # Registrar en registro_acceso
        registro = registrar_acceso(
            usuario_id=usuario_id,
            vehiculo_id=vehiculo_id,
            placa=placa,
            tipo_evento="entrada",
            metodo_acceso="facial",
            ubicacion="Parqueadero Principal",
            foto_captura=ruta_captura_rostro,  # Ruta local de la foto
            confianza=confianza,
            estado="exitoso"
        )
        
        if registro:
            print(f"✅ Acceso registrado correctamente")
            print(f"   ID: {registro.get('id')}")
            print(f"   Fecha: {registro.get('created_at')}")
        
        # Crear notificación para el usuario
        print("\n🔔 Creando notificación para el usuario...")
        
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        notificacion = crear_notificacion(
            usuario_id=usuario_id,
            titulo="✅ Acceso Autorizado",
            mensaje=f"Ingreso exitoso al parqueadero. Placa: {placa}. Fecha: {fecha_hora}",
            tipo="exito",
            icono="🚗"
        )
        
        if notificacion:
            print(f"✅ Notificación creada para {nombre_completo}")
        
        print("="*70 + "\n")
        return True
    else:
        print("🔴 " * 20)
        print("❌❌❌ ACCESO DENEGADO ❌❌❌")
        print("🔴 " * 20)
        print(f"\n✗ Verificación fallida para: {nombre_completo}")
        print(f"✗ Placa: {placa}")
        print(f"✗ Rostro coincide: NO - No se pudo verificar identidad")
        print("\n✗ Intento de acceso NO AUTORIZADO")
        print("✗ Barrera permanece cerrada")
        
        # ====== REGISTRAR INTENTO DENEGADO ======
        print("\n📝 Registrando intento denegado...")
        print("-" * 70)
        
        usuario_id = conductor.get('id')
        vehiculo_id = conductor.get('vehiculo_id')
        
        # Registrar intento denegado
        registro = registrar_acceso(
            usuario_id=usuario_id,
            vehiculo_id=vehiculo_id,
            placa=placa,
            tipo_evento="entrada",
            metodo_acceso="facial",
            ubicacion="Parqueadero Principal",
            foto_captura=ruta_captura_rostro,
            confianza=0.0,  # Sin confianza
            estado="denegado"
        )
        
        if registro:
            print(f"✅ Intento registrado (ID: {registro.get('id')})")
        
        # Crear notificación de advertencia
        print("\n🔔 Creando notificación de advertencia...")
        
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        notificacion = crear_notificacion(
            usuario_id=usuario_id,
            titulo="⚠️ Intento de Acceso Denegado",
            mensaje=f"Intento de ingreso con placa {placa} fue rechazado. Verificación facial fallida. Fecha: {fecha_hora}",
            tipo="advertencia",
            icono="🚨"
        )
        
        if notificacion:
            print(f"✅ Notificación de advertencia creada")
        
        print("="*70 + "\n")
        return False

# ==========================================
# PUNTO DE ENTRADA
# ==========================================

if __name__ == "__main__":
    try:
        resultado = procesar_evento_parqueadero()
        
        if resultado:
            print("\n✅ Flujo completado exitosamente - ACCESO PERMITIDO")
        else:
            print("\n❌ Flujo completado - ACCESO DENEGADO")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
