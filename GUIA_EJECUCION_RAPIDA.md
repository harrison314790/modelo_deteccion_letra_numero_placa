# 🚀 GUÍA RÁPIDA: Ejecutar el flujo integrado (main_integrated.py)

## ✅ ESTADO ACTUAL DE TU PROYECTO

- ✔️ Tienes venv 3.11.8 con prueba_yolo.py y prueba_numero_letra.py
- ✔️ Tienes deepface_env con reconocimientoFacial.py  
- ✔️ Se creó main_integrated.py que integra ambos

---

## 🎯 ANTES DE EJECUTAR - CHECKLIST

### 1️⃣ Verificar que .env tiene credenciales de Supabase

Abre `.env` y verifica que tiene:
```
SUPABASE_URL="https://..."
SUPABASE_KEY="..."
```

Si falta algo, cópialo desde tu dashboard de Supabase.

---

### 2️⃣ Instalar dependencias en venv 3.11.8

```powershell
# Navega a la carpeta del proyecto
cd C:\Users\HARRISON\Documents\modelo_deteccion_letra_numero_placa

# Activa el venv 3.11.8
.\.venv\Scripts\Activate.ps1

# Si hay error de permisos, ejecuta:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# Instala/actualiza dependencias
pip install --upgrade pip
pip install -r placas/requirements.txt
pip install -r requirements.txt

# Si requirements.txt no existe en raíz, crea uno:
# (copiar el contenido de placas/requirements.txt a raíz o aquí)
```

**Librerías necesarias en este venv:**
```
ultralytics
torch
easyocr
opencv-python
pillow
supabase
python-dotenv
```

---

### 3️⃣ Instalar dependencias en deepface_env (Python 3.10.11)

```powershell
# Desde el venv 3.11.8 (o cualquier terminal)
# Activa el deepface_env
face\deepface_env\Scripts\Activate.ps1

# Instala dependencias
pip install --upgrade pip
pip install -r face/requirements.txt

# Si falta deepface, instálalo manualmente:
pip install deepface

# Desactiva
deactivate
```

**Librerías necesarias en este venv:**
```
deepface
tensorflow
opencv-python
python-dotenv
```

---

## 🎬 EJECUTAR EL FLUJO COMPLETO

### Opción A: Ejecución simple (RECOMENDADA)

```powershell
# 1. Navega a la carpeta
cd C:\Users\HARRISON\Documents\modelo_deteccion_letra_numero_placa

# 2. Activa el venv 3.11.8
.\.venv\Scripts\Activate.ps1

# 3. Ejecuta el flujo integrado
python main_integrated.py
```

### Opción B: Ejecución con mejor visualización (si hay errores)

```powershell
.\.venv\Scripts\Activate.ps1
python -u main_integrated.py 2>&1 | Tee-Object -FilePath log_ejecucion.txt
```

---

## 📺 QUÉ ESPERAR

Cuando ejecutes `main_integrated.py`:

```
==================================================
🚗 SISTEMA DE ACCESO A PARQUEADERO INICIADO
==================================================

📸 PASO 1: Capturar foto de la placa
--------------------------------------------------
📷 Abriendo cámara... (presiona ESPACIO para capturar, ESC para cancelar)

[Se abre ventana de cámara]
Presiona ESPACIO → captura la foto
Presiona ESC → cancela

✔ Foto capturada
✔ Foto guardada: temp/placa_captura.jpg

📍 PASO 2: Detectar placa con YOLO
--------------------------------------------------
[Procesa automáticamente]

📖 PASO 3: Leer placa (OCR)
--------------------------------------------------
✔ Placa detectada: ABC123

🔍 PASO 4: Consultando conductor en Supabase
--------------------------------------------------
✔ Conductor encontrado: Juan Pérez
✔ Email: juan@example.com
✔ Biometría en Storage: foto_juan_biometria.jpg

⬇️  PASO 5: Descargando foto biométrica
--------------------------------------------------
✔ Biometría descargada: face/imagenes_descargadas/foto_juan_biometria.jpg

📷 PASO 6: Capturar foto del rostro para verificación
--------------------------------------------------
📷 Abriendo cámara... (presiona ESPACIO para capturar, ESC para cancelar)

[Se abre ventana de cámara nuevamente]
Presiona ESPACIO → captura tu rostro
Presiona ESC → cancela

✔ Foto capturada
✔ Foto guardada: temp/rostro_captura.jpg

🔐 PASO 7: Verificando identidad del conductor
--------------------------------------------------
➡️  Comparando rostros con DeepFace...
[Procesa automáticamente en deepface_env]

==================================================
✅ ACCESO PERMITIDO
✔ Identificación confirmada: Juan Pérez
✔ Se le permite el acceso al parqueadero
==================================================
```

---

## ⚠️ ERRORES COMUNES Y SOLUCIONES

### ❌ Error: "No se pudo abrir la cámara"

**Solución:**
```powershell
# Verifica que OpenCV reconoce tu cámara
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

Si imprime `False`, tu cámara no está siendo detectada. Intenta:
- Reiniciar la aplicación
- Permitir acceso a cámara en Configuración > Privacidad (Windows)
- Cambiar a índice 1: `cv2.VideoCapture(1)`

---

### ❌ Error: "No se pudo leer la placa"

**Causas posibles:**
- La imagen está muy oscura o borrosa
- La placa no es visible en la captura
- El modelo YOLO no detectó la región

**Solución:**
- Toma una foto clara de la placa directamente
- Asegúrate de iluminación adecuada
- Prueba con `placas/prueba_numero_letra.py` directamente primero

---

### ❌ Error: "La placa no está registrada en Supabase"

**Causas posibles:**
- El número OCR fue leído incorrectamente
- La placa no existe en la base de datos
- Credenciales de Supabase inválidas

**Solución:**
1. Verifica que `.env` tiene credenciales correctas
2. Agrega la placa manualmente en Supabase (tabla `conductores`)
3. Prueba con una placa que sabes está registrada

---

### ❌ Error: "No se pudo descargar la biometría"

**Causas posibles:**
- Ruta en Storage es incorrecta
- Storage bucket no existe
- Permisos de Supabase insuficientes

**Solución:**
- Verifica que el bucket `biometria` existe en Storage de Supabase
- Verifica la ruta exacta en la tabla `conductores` (columna `foto`)
- Asegúrate que la API Key tiene permisos de lectura en Storage

---

### ❌ Error: "No coincide con la biometría"

**Casos normales:**
- Diferentes ángulos de cámara
- Iluminación diferente
- Expresión facial diferente

**Solución:**
- Intenta nuevamente en mejor iluminación
- Acércate más a la cámara
- Mira directamente a la cámara

---

### ❌ Error: "deepface_env no encontrado"

**Solución:**
```powershell
# Crea el venv deepface
py -3.10 -m venv face/deepface_env

# Activa e instala
face\deepface_env\Scripts\Activate.ps1
pip install -r face/requirements.txt
pip install deepface
deactivate
```

---

## 🔍 TROUBLESHOOTING AVANZADO

### Ver logs detallados de deepface

Modifica `main_integrated.py` línea ~220, cambia:
```python
resultado = subprocess.run(
    [str(PYTHON_DEEPFACE), str(script_temporal)],
    capture_output=True,  # ← Cambiar a False para ver output en vivo
    text=True,
    timeout=60
)
```

---

### Probar cada módulo por separado

```powershell
# Activar venv 3.11.8
.\.venv\Scripts\Activate.ps1

# Probar detección de placa
python -c "from placas.prueba_yolo import procesar_imagenes_de_carpeta; procesar_imagenes_de_carpeta()"

# Probar OCR
python -c "from placas.prueba_numero_letra import leer_placa; print(leer_placa('ruta/a/imagen.jpg'))"

# Probar Supabase
python -c "from servicios.peticiones_supaBase import obtener_conductor_por_placa; print(obtener_conductor_por_placa('ABC123'))"

# Probar DeepFace
face\deepface_env\Scripts\Activate.ps1
python face/reconocimientoFacial.py
```

---

## 📌 PRÓXIMOS PASOS

1. ✅ Completa el checklist arriba
2. ✅ Ejecuta `python main_integrated.py`
3. ✅ Captura una placa
4. ✅ Captura tu rostro
5. ✅ Observa el resultado

Si todo funciona → ✅ **Éxito!**
Si hay errores → Comparte el error exacto y ayudaré a solucionarlo.

---

## 💡 NOTAS IMPORTANTES

- **Cámara**: Se abre en ventana nueva. Presiona ESPACIO para capturar, ESC para cancelar
- **Placa**: Debe ser clara y legible
- **Rostro**: Mira directamente a la cámara en buena iluminación
- **Tiempo**: La comparación facial toma ~20-30 segundos (DeepFace es lento)

---

¿Alguna duda? ¿Necesitas cambiar algo?
