#### ﻿**Proyecto**: Sistema de detección y reconocimiento de letras y números en placas

### 🎥 Video demostración del modelo  

https://github.com/user-attachments/assets/bb2f609f-c5f9-4f0b-8578-9234eab2ada0


- **Lenguaje**: Python
- **Versión requerida**: Python 3.11.8

**Descripción**n- Proyecto para detectar placas con un detector de objetos (YOLO) y reconocer letras y números con un modelo OCR entrenado. El flujo general es:
  - Detectar la placa en la imagen/video con el modelo YOLO.
  - Recortar la región de la placa detectada.
  - Pasar la región recortada al modelo OCR (letras y números) para leer la matrícula.

**Estructura importante del repositorio**
- `prueba_yolo.py`: script principal para detectar la placa y extraer la región.
- `prueba_numero_letra.py`: script que toma la región recortada y ejecuta el OCR sobre letras y números.
- `modelos/detectar-Placa/best.pt`: modelo YOLO entrenado para detectar la placa.
- `modelos/leer_numero_placas/best.pt`: modelo OCR entrenado para lectura de letras y números.
- `placas_registradas.json`: (opcional) archivo donde se pueden guardar resultados/detecciones.


**Instalación y preparación (Windows, PowerShell)**
1. Verificar versión de Python (debe ser 3.11.8):

```powershell
py -3.11 --version
# o
python --version
```

2. Crear el entorno virtual (recomendado nombre: `.venv`):

```powershell
# crear el venv usando el lanzador py para Python 3.11
py -3.11 -m venv .venv

# activar en PowerShell
.\.venv\Scripts\Activate.ps1

# Si PowerShell bloquea la ejecución, permite scripts en la sesión actual:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
.\.venv\Scripts\Activate.ps1
```

3. Instalar dependencias desde `requirements.txt`:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

Alternativa (sin activar el venv):

```powershell
py -3.11 -m pip install -r requirements.txt
```

Explicación rápida de las dos maneras de instalar:
- Activando el `venv` e instalando con `pip install -r requirements.txt` instala paquetes dentro del entorno virtual; es la forma recomendada.
- Sin activar el `venv`, usando `py -3.11 -m pip` instala usando explícitamente el intérprete, pero no cambia el entorno de la consola.



**Ejecución de los scripts (orden recomendado)**
1. Detectar placa y guardar/mostrar la región: ejecutar `prueba_yolo.py`.

```powershell
python prueba_yolo.py
```

2. Ejecutar OCR sobre las regiones recortadas (o pasarlas al pipeline): ejecutar `prueba_numero_letra.py`.

```powershell
python prueba_numero_letra.py
```

Notas sobre ejecución:
- Los scripts deben ejecutarse en ese orden: primero detección (recorte), luego OCR.
- Si los scripts aceptan argumentos (ruta de imagen/video, modelo, etc.), puedes pasarlos desde la línea de comandos. Revisa el código de `prueba_yolo.py` y `prueba_numero_letra.py` para ver parámetros disponibles.

**Dónde están los modelos**
- `modelos/detectar-Placa/best.pt`: detector YOLO para localizar placas.
- `modelos/leer_numero_placas/best.pt`: modelo para reconocer letras y números.


**Guardar resultados**
- Los scripts pueden imprimir resultados por consola y/o guardar en `placas_registradas.json`. Revisa los scripts para entender el formato de salida y dónde se guardan los archivos.




