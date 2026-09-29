import os
import re
import pandas as pd

GOOGLE_SHEET_ID = "15dYC-f3m6a8jXznqIXOjXATL-2SplD1UakYHBMTt5hk"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=xlsx"

LOW_STOCK_ITEMS = [
    "adaptador de poder 9v",
    "alargador 6 conexiones",
    "cable ethernet",
    "escuadra combinada con nivel",
    "extension de cable 20 metros"
]

def escape_latex(val) -> str:
    """Escapa caracteres especiales de LaTeX (%, &, _, #, $ y \\)."""
    if pd.isna(val) or val is None:
        return ""
    s = str(val).strip()
    s = s.replace('\\', r'\textbackslash{}')
    s = s.replace('%', r'\%')
    s = s.replace('&', r'\&')
    s = s.replace('_', r'\_')
    s = s.replace('#', r'\#')
    s = s.replace('$', r'\$')
    return s

def extract_numeric_quantity(cant_raw) -> int:
    """Extrae el primer valor entero de la cantidad para filtrado de ceros."""
    if pd.isna(cant_raw) or cant_raw is None:
        return 0
    s = str(cant_raw).strip()
    match = re.search(r'\d+', s)
    if match:
        return int(match.group(0))
    return 0

def load_inventory_dataframe() -> pd.DataFrame:
    """Intenta cargar los datos desde Google Sheets. En caso de fallo, recurre al Excel local."""
    print(f"Intentando descargar inventario desde Google Sheets (ID: {GOOGLE_SHEET_ID})...")
    try:
        df = pd.read_excel(GOOGLE_SHEET_URL)
        print("¡Datos descargados exitosamente desde Google Sheets!")
        return df
    except Exception as e:
        print(f"Advertencia: No se pudo conectar a Google Sheets ({e}). Buscando archivo local...")
        data_path = os.path.join("data", "Inventario lab.xlsx")
        root_path = "Inventario lab.xlsx"
        if os.path.exists(data_path):
            print(f"Cargando desde '{data_path}'...")
            return pd.read_excel(data_path)
        elif os.path.exists(root_path):
            print(f"Cargando desde '{root_path}'...")
            return pd.read_excel(root_path)
        else:
            raise FileNotFoundError("No se encontró el archivo de inventario ni en Google Sheets ni localmente.")

def main():
    df = load_inventory_dataframe()
    
    # Normalizar nombres de columnas
    df.columns = [str(c).strip() for c in df.columns]
    
    # Mapear columnas dinámicamente
    col_item = None
    col_cant = None
    col_desc = None
    
    for c in df.columns:
        c_lower = c.lower()
        if 'instrument' in c_lower or 'item' in c_lower or 'nombre' in c_lower:
            col_item = c
        elif 'cantid' in c_lower or 'stock' in c_lower or 'total' in c_lower:
            col_cant = c
        elif 'descrip' in c_lower or 'nota' in c_lower or 'observ' in c_lower:
            col_desc = c
            
    if not col_item:
        col_item = df.columns[0]
    if not col_cant:
        col_cant = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    if not col_desc and len(df.columns) > 2:
        col_desc = df.columns[2]
        
    print(f"Columnas detectadas -> Ítem: '{col_item}', Cantidad: '{col_cant}', Descripción: '{col_desc}'")
    
    rows_tex = []
    total_items_validos = 0
    total_prestamos = 0
    
    for _, row in df.iterrows():
        item_name = str(row[col_item]).strip() if pd.notna(row[col_item]) else ""
        cant_raw = row[col_cant]
        desc_text = str(row[col_desc]).strip() if col_desc and pd.notna(row[col_desc]) else ""
        
        # Ignorar si no hay nombre de ítem
        if not item_name or item_name.lower() == 'nan':
            continue
            
        # Filtrar ítems con cantidad = 0
        num_cant = extract_numeric_quantity(cant_raw)
        if num_cant <= 0:
            continue
            
        total_items_validos += 1
        
        # Formato visible para la cantidad
        cant_str = str(cant_raw).strip()
        if isinstance(cant_raw, float) and cant_raw.is_integer():
            cant_str = str(int(cant_raw))
            
        combined_info_lower = f"{item_name} {desc_text}".lower()
        item_lower = item_name.lower()
        
        # Clasificación de estado
        if 'living lab' in combined_info_lower:
            estado_tex = r"\cellcolor{azulPrestamo} Préstamo (Living Lab)"
            total_prestamos += 1
        elif any(low_item in item_lower for low_item in LOW_STOCK_ITEMS):
            estado_tex = r"\cellcolor{amarilloAlerta} Stock Bajo"
        else:
            estado_tex = r"\cellcolor{verdeOk} Disponible"
            
        item_escaped = escape_latex(item_name)
        cant_escaped = escape_latex(cant_str)
        
        rows_tex.append(f"  {item_escaped} & {cant_escaped} & {estado_tex} \\\\")
        
    # Generar tabla_inventario.tex
    tabla_content = r"""\begin{longtable}{p{8.5cm} c l}
\toprule
\textbf{Descripción} & \textbf{Cantidad} & \textbf{Estado} \\
\midrule
\endfirsthead
\toprule
\textbf{Descripción} & \textbf{Cantidad} & \textbf{Estado} \\
\midrule
\endhead
\bottomrule
\endfoot
""" + "\n".join(rows_tex) + r"""
\end{longtable}
"""

    with open("tabla_inventario.tex", "w", encoding="utf-8") as f:
        f.write(tabla_content)
    print(f"Archivo 'tabla_inventario.tex' generado con {total_items_validos} ítems.")
    
    # Generar metricas.tex
    metricas_content = f"""\\newcommand{{\\totalItemsValidos}}{{{total_items_validos}}}
\\newcommand{{\\totalPrestamos}}{{{total_prestamos}}}
"""
    with open("metricas.tex", "w", encoding="utf-8") as f:
        f.write(metricas_content)
    print(f"Archivo 'metricas.tex' generado (Ítems Válidos: {total_items_validos}, Préstamos: {total_prestamos}).")

if __name__ == "__main__":
    main()
