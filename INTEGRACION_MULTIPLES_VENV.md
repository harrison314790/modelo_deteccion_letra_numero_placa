# 🔧 Integración de Múltiples Entornos Python

Tu proyecto tiene **dos entornos Python diferentes** que necesitan trabajar juntos:

| Módulo | Entorno | Python | Propósito |
|--------|---------|--------|----------|
| `prueba_yolo.py` + `prueba_numero_letra.py` | `.venv` | 3.11.8 | Detección y OCR |
| `reconocimientoFacial.py` | `deepface-env` | 3.10.11 | Reconocimiento facial |

---

## ✅ SOLUCIÓN IMPLEMENTADA: `main_integrated.py`

He creado `main_integrated.py` que usa **`subprocess`** para ejecutar cada módulo en su entorno correcto.

### **Ventajas:**
- ✔ Sin conflictos de librerías
- ✔ Cada módulo funciona de forma aislada
- ✔ Fácil de mantener y escalar

### **Cómo funciona:**

```
┌─────────────────────────────────────────────────────────┐
│  main_integrated.py (venv 3.11.8)                      │
├─────────────────────────────────────────────────────────┤
│ 1. Captura foto placa desde cámara                     │
│ 2. Detecta placa (YOLO) - MISMO VENV                  │
│ 3. Lee OCR - MISMO VENV                               │
│ 4. Consulta Supabase - MISMO VENV                     │
│ 5. Captura rostro desde cámara                        │
│ 6. Llama subprocess → reconocimientoFacial.py         │
│    (ejecuta en deepface-env, Python 3.10.11)          │
│ 7. Retorna resultado (True/False)                      │
│ 8. Autoriza o deniega acceso                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 PASOS PARA USAR

### **1. Verificar que tienes ambos venv activos**

```powershell
# Verifica que existen:
ls .venv
ls face/deepface_env

# Si no existen, créalos primero (ver abajo)
```

### **2. Asegúrate de que ambos venv tienen las dependencias correctas**

**Para venv 3.11.8 (.venv):**
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r placas/requirements.txt
deactivate
```

**Para deepface-env (Python 3.10.11):**
```powershell
# Usa el python 3.10.11 si lo tienes instalado
py -3.10 -m venv face/deepface_env

# Activar
face\deepface_env\Scripts\Activate.ps1

# Instalar dependencias de deepface
pip install -r face/requirements.txt
# o si lo tienes en deepface_env/requirements.txt:
pip install -r face/deepface_env/requirements.txt

deactivate
```

### **3. Ejecutar main_integrated.py**

```powershell
# IMPORTANTE: Debe ejecutarse en el venv 3.11.8
.\.venv\Scripts\Activate.ps1

python main_integrated.py
```

### **Flujo del programa:**

1. **Captura placa**: Abre cámara, presiona ESPACIO para capturar, ESC para cancelar
2. **Detecta y lee placa**: Automático (usa `prueba_numero_letra.py`)
3. **Consulta Supabase**: Busca conductor por placa
4. **Descarga biometría**: Obtiene foto de referencia desde Storage
5. **Captura rostro**: Abre cámara nuevamente, presiona ESPACIO
6. **Compara rostros**: Usa DeepFace en su propio venv
7. **Resultado**: ✅ ACCESO PERMITIDO o ❌ ACCESO DENEGADO

---

## 📋 ALTERNATIVAS (si quieres cambiar de estrategia)

### **Alternativa A: Convertir todo a Python 3.11.8**

Si quieres un solo venv:

```powershell
# 1. Instala DeepFace en el venv 3.11.8
.\.venv\Scripts\Activate.ps1
pip install deepface

# 2. Modifica reconocimientoFacial.py para no usar TensorFlow 2.10
#    (puede haber conflictos con PyTorch de YOLO)

# 3. Importa directamente en main.py sin subprocess
```

**Riesgo**: TensorFlow 2.10 (DeepFace) vs PyTorch (YOLO) pueden tener problemas.

---

### **Alternativa B: API REST con Flask**

Exponer `reconocimientoFacial.py` como servicio:

```python
# face/app_facial.py
from flask import Flask, request, jsonify
from reconocimientoFacial import comparar_rostros

app = Flask(__name__)

@app.route('/comparar', methods=['POST'])
def api_comparar():
    img1 = request.form.get('img1')
    img2 = request.form.get('img2')
    resultado = comparar_rostros(img1, img2)
    return jsonify({"match": resultado})

if __name__ == "__main__":
    app.run(port=5000)
```

Luego desde `main.py`:
```python
import requests

resultado = requests.post('http://localhost:5000/comparar', 
    data={'img1': ruta1, 'img2': ruta2}).json()['match']
```

**Ventajas**: Separación limpia, escalable
**Desventajas**: Más complejo, overhead de red

---

### **Alternativa C: Docker Containers**

Cada servicio en su propio contenedor con su Python.

**Ventajas**: Portabilidad, aislamiento total
**Desventajas**: Necesita Docker instalado

---

## ⚠️ TROUBLESHOOTING

### **Error: "No se pudo abrir la cámara"**
- Verifica que tu cámara web esté conectada
- Prueba con: `python -m cv2 --version`

### **Error: "No encontrado: .venv/Scripts/python.exe"**
- Asegúrate de crear el venv 3.11.8:
  ```powershell
  py -3.11 -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

### **Error en DeepFace: "deepface_env no encontrado"**
- Crea el venv para DeepFace:
  ```powershell
  py -3.10 -m venv face/deepface_env
  face\deepface_env\Scripts\Activate.ps1
  pip install -r face/requirements.txt
  ```

### **Error en Supabase: "No se puede conectar"**
- Verifica que `.env` contiene tus credenciales:
  ```
  SUPABASE_URL=https://...
  SUPABASE_KEY=...
  ```

---

## 📌 RECOMENDACIÓN FINAL

**Usa `main_integrated.py` con Opción A (subprocess)**:
- ✅ Funciona con ambos venv
- ✅ Sin cambios necesarios en código existente
- ✅ Fácil de mantener

Si después quieres optimizar, puedes migrar a API REST o Docker.

---

## 🔄 PRÓXIMOS PASOS

1. ✅ Verifica ambos venv están creados y tienen dependencias
2. ✅ Ejecuta `main_integrated.py`
3. ✅ Prueba el flujo completo
4. ✅ Si hay errores, comparte los mensajes exactos

¿Necesitas ayuda con algo de esto?
