# 🎥 Reconocimiento Facial en Tiempo Real

## 📋 Descripción

Este módulo permite comparar rostros en tiempo real usando la cámara web contra una imagen de referencia descargada del bucket de Supabase (o cualquier foto de referencia).

## 🚀 Uso Rápido

### Opción 1: Ejecutar desde la raíz del proyecto

```powershell
python ejecutar_reconocimiento_tiempo_real.py
```

### Opción 2: Ejecutar directamente con el venv de DeepFace

```powershell
cd face
.\deepface_env\Scripts\python.exe reconocimiento_tiempo_real.py
```

## 📁 Imagen de Referencia

Por defecto, el script busca la imagen en:
```
face/referencia/mi_foto.jpeg
```

### Para usar una imagen descargada del bucket:

1. **Opción A**: Copia la imagen descargada a `face/referencia/mi_foto.jpeg`

2. **Opción B**: Modifica la ruta en el script `face/reconocimiento_tiempo_real.py`:
   ```python
   RUTA_IMAGEN_REFERENCIA = BASE_DIR / "imagenes_descargadas" / "front_xxxxx.jpg"
   ```

## ⌨️ Controles

- **Q** o **ESC**: Salir del reconocimiento
- El reconocimiento es automático cada 15 frames

## 📊 Información mostrada

- ✅ **Verde**: Coincidencia detectada (es la persona de la foto de referencia)
- ❌ **Rojo**: Sin coincidencia (persona desconocida)
- **Confianza**: Porcentaje de similitud entre rostros
- **Frame**: Número de frame actual

## 🔧 Solución de Problemas

### Error: "No se encuentra la imagen de referencia"

```powershell
# Verifica que existe la imagen
ls face\referencia\mi_foto.jpeg

# O coloca tu foto ahí:
# 1. Crea la carpeta si no existe
mkdir face\referencia -Force

# 2. Copia tu foto
copy "ruta\a\tu\foto.jpg" face\referencia\mi_foto.jpeg
```

### Error: "No se puede importar DeepFace"

```powershell
# Reinstala el entorno de DeepFace
python instalar.py
```

### Error: "No se puede acceder a la cámara"

- Verifica que ninguna otra aplicación esté usando la cámara
- Revisa los permisos de la cámara en Windows
- Intenta reiniciar el script

## 🛠️ Ajustes de Performance

En `face/reconocimiento_tiempo_real.py`, puedes modificar:

```python
# Línea 76: Comparar cada N frames
if frame_counter % 15 == 0:  # Cambiar 15 a 10 (más rápido) o 20 (más lento)
```

- **Valor menor (10)**: Más comparaciones por segundo, más uso de CPU
- **Valor mayor (20-30)**: Menos comparaciones, mejor performance

## 📝 Diferencias con el código original

### ❌ Tu código tenía estos errores:

```python
tri:  # ❌ Sintaxis incorrecta
    embedding_ref = DeepFace.represent(...)
```

### ✅ Código corregido:

```python
try:  # ✅ Sintaxis correcta
    embedding_ref = DeepFace.represent(...)
except Exception as e:
    print(f"Error: {e}")
```

### Mejoras adicionales:

1. ✅ **Manejo de errores robusto**: No se detiene si no detecta rostro
2. ✅ **Optimización**: Compara cada N frames, no todos
3. ✅ **Información visual**: Muestra confianza y estado en pantalla
4. ✅ **Logs informativos**: Imprime resultados en consola
5. ✅ **Configuración flexible**: Fácil cambiar imagen de referencia

## 🔗 Integración con Supabase

Para usar fotos del bucket de biometría:

```python
# 1. Descarga la foto del bucket (ya implementado en tu main_integrated.py)
ruta_foto_biometria = descargar_imagen_biometria(id_usuario)

# 2. Usa esa ruta en el reconocimiento
RUTA_IMAGEN_REFERENCIA = Path(ruta_foto_biometria)
```

## 💡 Ejemplo de uso en tu flujo

```python
# En main_integrated.py o tu flujo principal:

# 1. Usuario ingresa placa
placa = detectar_placa()

# 2. Buscar en Supabase
usuario = buscar_por_placa(placa)

# 3. Descargar foto de referencia
foto_ref = descargar_foto_biometria(usuario['id'])

# 4. Ejecutar reconocimiento en tiempo real
import subprocess
subprocess.run([
    str(PYTHON_DEEPFACE),
    "face/reconocimiento_tiempo_real.py"
])
```

## 📞 Soporte

Si tienes problemas, revisa:
1. Que el venv de DeepFace esté instalado: `python instalar.py`
2. Que la imagen de referencia exista
3. Que la cámara funcione correctamente
4. Los logs en la consola para más detalles

---

✨ **Creado por**: Sistema de Reconocimiento de Placas y Biometría  
📅 **Última actualización**: Diciembre 2025
