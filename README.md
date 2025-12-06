# 🚗 Sistema Integral: Detección de Placas + Reconocimiento Facial

Sistema completo de control de acceso a parqueadero que detecta placas, extrae el número, consulta Supabase y verifica la identidad del conductor con reconocimiento facial.

---

## 📋 Descripción General

**Flujo del sistema:**
1. 📸 Captura foto de placa desde cámara web
2. 🎯 Detecta la placa usando YOLO (modelo entrenado)
3. 📖 Lee los caracteres (OCR) para obtener el número
4. 🔍 Consulta Supabase por el conductor registrado
5. ⬇️ Descarga foto biométrica del Storage
6. 📷 Captura foto del rostro desde cámara web
7. 🔐 Compara rostro usando DeepFace
8. ✅ Autoriza o deniega acceso

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────┐
│ main_integrated.py (Python 3.11.8)             │
├─────────────────────────────────────────────────┤
│ ├─ Captura de cámara                           │
│ ├─ prueba_yolo.py (detección)                  │
│ ├─ prueba_numero_letra.py (OCR)                │
│ ├─ peticiones_supaBase.py (consultas)          │
│ └─ subprocess → reconocimientoFacial.py        │
│    (se ejecuta en venv deepface, Python 3.10)  │
└─────────────────────────────────────────────────┘
```

---

## 📦 Requisitos

| Componente | Python | Ubicación | Propósito |
|-----------|--------|-----------|----------|
| YOLO + OCR | 3.11.8 | `.venv` | Detección y lectura de placa |
| DeepFace | 3.10.11 | `face/deepface_env` | Reconocimiento facial |

---

## 🚀 Instalación Rápida

### Opción A: Instalación Automática (RECOMENDADA)

```powershell
# En la carpeta del proyecto
python instalar.py
```

Esto crea automáticamente:
- ✔️ venv 3.11.8 (`.venv`)
- ✔️ venv DeepFace 3.10.11 (`face/deepface_env`)
- ✔️ Instala todas las dependencias

### Opción B: Instalación Manual

**1. Crear venv 3.11.8:**
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
deactivate
```

**2. Crear venv DeepFace 3.10.11:**
```powershell
py -3.10 -m venv face/deepface_env
face\deepface_env\Scripts\Activate.ps1
pip install -r face/requirements.txt
pip install deepface
deactivate
```

---

## ⚙️ Configuración

### 1. Archivo `.env` (Supabase)

Crea o verifica que existe `.env` con:

```
SUPABASE_URL="https://tu-proyecto.supabase.co"
SUPABASE_KEY="tu-api-key-anon"
```

### 2. Base de Datos Supabase

**Tabla `conductores`:**
```sql
id: UUID (primary key)
nombre: TEXT
email: TEXT
placa: TEXT (unique)
foto: TEXT (ruta en Storage)
created_at: TIMESTAMP
```

**Storage Bucket:**
- Nombre: `biometria`
- Permisos: Lectura pública o restringida

---

## 🎬 Ejecución

### Iniciar el flujo completo

```powershell
cd C:\Users\HARRISON\Documents\modelo_deteccion_letra_numero_placa

# Activar venv principal
.\.venv\Scripts\Activate.ps1

# Ejecutar
python main_integrated.py
```

### Probar módulos por separado

```powershell
# Detección de placa (requiere venv 3.11.8)
.\.venv\Scripts\Activate.ps1
python -c "from placas.prueba_yolo import procesar_imagenes_de_carpeta; procesar_imagenes_de_carpeta()"

# OCR de placa
python -c "from placas.prueba_numero_letra import leer_placa; print(leer_placa('ruta/imagen.jpg'))"

# Reconocimiento facial (requiere venv DeepFace)
face\deepface_env\Scripts\Activate.ps1
python face/reconocimientoFacial.py
```

---

## 📁 Estructura del Proyecto

```
modelo_deteccion_letra_numero_placa/
├── main_integrated.py          ← 🎯 PUNTO DE ENTRADA (flujo completo)
├── diagnostico_venv.py         ← 🔍 Verificar entornos
├── instalar.py                 ← 🔧 Instalación automática
├── requirements.txt            ← 📦 Dependencias venv 3.11.8
├── .env                        ← 🔐 Credenciales Supabase
├── .gitignore                  ← 📝 Ignorar archivos
│
├── placas/                     ← 🚗 Detección y OCR
│   ├── prueba_yolo.py
│   ├── prueba_numero_letra.py
│   └── requirements.txt
│
├── face/                       ← 😊 Reconocimiento facial
│   ├── reconocimientoFacial.py
│   ├── requirements.txt
│   ├── deepface_env/           ← venv Python 3.10.11
│   └── imagenes_descargadas/
│
├── servicios/                  ← 🔗 Integración con Supabase
│   └── peticiones_supaBase.py
│
├── modelos/                    ← 🤖 Modelos entrenados
│   ├── detectar-Placa/
│   │   └── best.pt            (YOLO - detección)
│   └── leer_numero_placas/
│       └── best.pt            (OCR - lectura)
│
└── temp/                       ← 📸 Imágenes temporales
    ├── placa_captura.jpg
    └── rostro_captura.jpg
```

---

## 📖 Documentación Adicional

| Archivo | Descripción |
|---------|-----------|
| `GUIA_EJECUCION_RAPIDA.md` | Paso a paso para ejecutar |
| `INTEGRACION_MULTIPLES_VENV.md` | Detalles técnicos avanzados |

---

## ⚠️ Troubleshooting

### ❌ "No se pudo abrir la cámara"
```powershell
# Verifica que OpenCV reconoce tu cámara
python -c "import cv2; print('Cámara OK' if cv2.VideoCapture(0).isOpened() else 'Cámara NO detectada')"
```

### ❌ "No encontrado: deepface_env"
```powershell
# Crea el venv DeepFace
py -3.10 -m venv face/deepface_env
face\deepface_env\Scripts\Activate.ps1
pip install -r face/requirements.txt
```

### ❌ "La placa no está registrada"
- Verifica que el número OCR es correcto
- Agrega la placa manualmente en Supabase

### ❌ "Error en DeepFace"
- Verifica que `face/deepface_env` existe y tiene DeepFace instalado
- Aumenta timeout en `main_integrated.py` (línea ~215)

---

## 🎯 Próximos Pasos

1. ✅ Ejecuta `python instalar.py`
2. ✅ Verifica `.env` con credenciales Supabase
3. ✅ Ejecuta `python main_integrated.py`
4. ✅ Captura placa y rostro
5. ✅ Observa el resultado

---

## 📞 Soporte

Si tienes errores:
1. Ejecuta `python diagnostico_venv.py` para verificar estado
2. Lee `GUIA_EJECUCION_RAPIDA.md` para soluciones comunes
3. Revisa logs en `temp/log_ejecucion.txt` (si lo generas con Tee-Object)

---

## 📝 Notas Importantes

- **Dos venv completamente separados**: Sin conflictos de librerías
- **Subprocess**: Cada módulo se ejecuta en su entorno correcto
- **Cámara interactiva**: Presiona ESPACIO para capturar, ESC para cancelar
- **OCR colombiano**: Formato ABC-123 automáticamente corregido
- **DeepFace**: ~20-30 segundos por comparación (tiempo normal)

---

## 🔄 Flujo Visual

```
Inicio
  ↓
📸 Capturar placa
  ↓
🎯 YOLO detecta región
  ↓
📖 OCR extrae "ABC123"
  ↓
🔍 Supabase busca "ABC123"
  ↓
├─ ❌ No encontrado → Acceso denegado
└─ ✔ Encontrado: Juan Pérez
    ↓
    ⬇️ Descargar foto biométrica
    ↓
    📷 Capturar tu rostro
    ↓
    🔐 DeepFace compara
    ↓
    ├─ ✅ Coincide → ACCESO PERMITIDO
    └─ ❌ No coincide → ACCESO DENEGADO
```

---

**¿Preguntas? Revisa la documentación o ejecuta `python diagnostico_venv.py`**
