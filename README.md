# Automatización de Informe de Inventario en LaTeX

Sistema automatizado para la generación y compilación de informes de inventario de laboratorio en formato PDF a partir de datos estructurados en Excel (`Inventario lab.xlsx`), utilizando Python, LaTeX y GitHub Actions.

---

## 📁 Estructura del Proyecto

```text
.
├── .github/
│   └── workflows/
│       └── compilar_informe.yml  # Pipeline de CI/CD para automatización en GitHub Actions
├── data/
│   └── Inventario lab.xlsx       # Hoja de cálculo fuente con los datos del inventario
├── generar_informe.py            # Script en Python que procesa los datos y genera tablas/métricas LaTeX
├── main.tex                      # Documento principal en LaTeX con formato y estilos
├── tabla_inventario.tex          # Tabla longtable generada dinámicamente (auto-generado)
├── metricas.tex                  # Comandos de métricas dinámicas (auto-generado)
├── requirements.txt              # Dependencias de Python requeridas
└── README.md                     # Documentación general del proyecto
```

---

## ⚙️ Reglas de Procesamiento y Clasificación (`generar_informe.py`)

1. **Ubicación del archivo de datos:** El script busca prioritariamente en `data/Inventario lab.xlsx` y, si no existe, en la raíz del proyecto (`Inventario lab.xlsx`).
2. **Filtrado de Ítems:** Se excluyen del informe todos aquellos elementos con cantidad igual a `0`.
3. **Escapado de Caracteres LaTeX:** Se procesan automáticamente caracteres reservados de LaTeX (`%`, `&`, `_`, `#`, `$`) en nombres y cantidades.
4. **Clasificación de Estados:**
   - **`Préstamo (Living Lab)`** (`\cellcolor{azulPrestamo}`): Si el nombre/descripción contiene la frase "Living Lab" (insensible a mayúsculas/minúsculas).
   - **`Stock Bajo`** (`\cellcolor{amarilloAlerta}`): Si el ítem figura en la lista de alerta:
     - *Adaptador de poder 9v*
     - *Alargador 6 conexiones*
     - *Cable ethernet*
     - *Escuadra combinada con nivel*
     - *Extension de cable 20 metros*
   - **`Disponible`** (`\cellcolor{verdeOk}`): Para todos los demás ítems válidos.
5. **Generación de Archivos TeX:**
   - `tabla_inventario.tex`: Genera la estructura `longtable` con encabezados repetibles (`\endfirsthead`, `\endhead`).
   - `metricas.tex`: Define los comandos LaTeX con los totales calculados:
     - `\totalItemsValidos`: Cantidad total de registros de ítems válidos (sin ceros).
     - `\totalPrestamos`: Cantidad total de ítems asignados a Living Lab.

---

## 🚀 Ejecución Local

### Prerrequisitos

- Python 3.11 o superior.
- Distribución de LaTeX instalada localmente (opcional si solo se desea probar la generación de los `.tex` con Python).

### Pasos

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar el script de procesamiento:**
   ```bash
   python generar_informe.py
   ```
   *Esto generará los archivos `tabla_inventario.tex` y `metricas.tex`.*

3. **Compilar el documento PDF (si cuenta con LaTeX instalado):**
   ```bash
   pdflatex main.tex
   ```

---

## 🔄 Integración Continua (GitHub Actions CI/CD)

El archivo `.github/workflows/compilar_informe.yml` automatiza el ciclo de vida completo:

1. **Disparadores (Triggers):** Cada `push` a la rama `main` o ejecución manual vía `workflow_dispatch`.
2. **Entorno:** `ubuntu-latest` con Python 3.11.
3. **Procesamiento:** Instala dependencias y ejecuta `python generar_informe.py`.
4. **Compilación:** Utiliza la acción `xu-cheng/latex-action@v3` para compilar `main.tex` a `main.pdf`.
5. **Artefacto:** Sube el archivo `main.pdf` resultante como un artefacto descargable (`informe-inventario-pdf`) disponible en la pestaña **Actions** del repositorio.
