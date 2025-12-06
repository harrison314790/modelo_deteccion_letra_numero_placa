"""
Script de prueba para verificar la velocidad de la cámara SIN DeepFace.
Esto ayuda a diagnosticar si el problema es la cámara o DeepFace.
"""

import cv2
import time

def test_camara_sola():
    """Prueba la cámara sin procesamiento pesado."""
    print("="*60)
    print("🎥 PRUEBA DE VELOCIDAD DE CÁMARA (SIN DEEPFACE)")
    print("="*60)
    print("📊 Midiendo FPS de la cámara...")
    print("⏱️  Capturando 150 frames...")
    print("")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ No se puede abrir la cámara")
        return
    
    frames_capturados = 0
    start_time = time.time()
    
    while frames_capturados < 150:
        ret, frame = cap.read()
        if not ret:
            break
        
        frames_capturados += 1
        
        # Agregar texto al frame
        cv2.putText(frame, f"Frame: {frames_capturados}/150", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Presiona Q para salir", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Test de Camara", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    end_time = time.time()
    elapsed = end_time - start_time
    fps = frames_capturados / elapsed
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Resultados
    print("\n" + "="*60)
    print("📊 RESULTADOS:")
    print("="*60)
    print(f"Frames capturados: {frames_capturados}")
    print(f"Tiempo total: {elapsed:.2f} segundos")
    print(f"FPS promedio: {fps:.1f}")
    print("")
    
    # Diagnóstico
    if fps >= 25:
        print("✅ EXCELENTE - La cámara funciona muy bien")
        print("   💡 El problema de lentitud es DeepFace, no la cámara")
    elif fps >= 15:
        print("🟡 ACEPTABLE - La cámara funciona OK")
        print("   💡 Puede mejorar cerrando otras aplicaciones")
    else:
        print("❌ LENTO - Hay problema con la cámara o sistema")
        print("   💡 Posibles causas:")
        print("      - Otra aplicación está usando la cámara")
        print("      - Drivers de cámara desactualizados")
        print("      - CPU sobrecargado por otras aplicaciones")
    
    print("="*60)


def test_camara_con_procesamiento():
    """Prueba la cámara simulando procesamiento pesado."""
    print("\n" + "="*60)
    print("🎥 PRUEBA CON PROCESAMIENTO SIMULADO")
    print("="*60)
    print("📊 Simulando carga de CPU cada 30 frames...")
    print("⏱️  Capturando 150 frames...")
    print("")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ No se puede abrir la cámara")
        return
    
    frames_capturados = 0
    start_time = time.time()
    procesamiento_count = 0
    
    while frames_capturados < 150:
        ret, frame = cap.read()
        if not ret:
            break
        
        frames_capturados += 1
        
        # Simular procesamiento pesado cada 30 frames
        if frames_capturados % 30 == 0:
            procesamiento_count += 1
            time.sleep(0.3)  # Simular 300ms de procesamiento (como DeepFace)
            color = (0, 255, 255)  # Amarillo cuando procesa
            texto_estado = "[PROCESANDO...]"
        else:
            color = (0, 255, 0)  # Verde normal
            texto_estado = "Normal"
        
        # Agregar texto al frame
        cv2.putText(frame, f"Frame: {frames_capturados}/150", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, texto_estado, (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f"Comparaciones: {procesamiento_count}", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Test con Procesamiento", frame)
        
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break
    
    end_time = time.time()
    elapsed = end_time - start_time
    fps = frames_capturados / elapsed
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Resultados
    print("\n" + "="*60)
    print("📊 RESULTADOS:")
    print("="*60)
    print(f"Frames capturados: {frames_capturados}")
    print(f"Tiempo total: {elapsed:.2f} segundos")
    print(f"FPS promedio: {fps:.1f}")
    print(f"Comparaciones simuladas: {procesamiento_count}")
    print("")
    
    # Diagnóstico
    if fps >= 20:
        print("✅ BUENO - Con waitKey(10) la UI debería responder bien")
    elif fps >= 10:
        print("🟡 ACEPTABLE - Puede haber algo de lag")
    else:
        print("❌ PROBLEMA - Lag severo incluso con optimizaciones")
    
    print("="*60)


if __name__ == "__main__":
    print("\n🧪 SUITE DE PRUEBAS DE CÁMARA\n")
    
    # Test 1: Cámara sola
    test_camara_sola()
    
    input("\n⏸️  Presiona ENTER para continuar con el siguiente test...")
    
    # Test 2: Cámara con procesamiento simulado
    test_camara_con_procesamiento()
    
    print("\n✅ Pruebas completadas!")
    print("💡 Usa estos resultados para ajustar la configuración en OPTIMIZACION_RECONOCIMIENTO.md")
