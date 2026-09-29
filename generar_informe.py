import os
import re
import pandas as pd

LOW_STOCK_ITEMS = [
    "adaptador de poder 9v",
    "alargador 6 conexiones",
    "cable ethernet",
    "escuadra combinada con nivel",
    "extension de cable 20 metros"
]

def escape_latex(val) -> str:
    """Escapa los caracteres especiales de LaTeX en cadenas o valores."""
    if pd.isna(val) or val is None:
        return ""
    s = str(val)
    # Escapar caracter \ primero si existiera
    s = s.replace('\\', r'\textbackslash{}')
    # Escapar %, &, _, #, $
    s = s.replace('%', r'\%')
    s = s.replace('&', r'\&')
    s = s.replace('_', r'\_')
    s = s.replace('#', r'\#')
    s = s.replace('$', r'\$')
    return s

def resolve_excel_path() -> str:
    """Busca el archivo Excel en data/Inventario lab.xlsx o en la raíz."""
    data_path = os.path.join("data", "Inventario lab.xlsx")
    root_path = "Inventario lab.xlsx"
    
    if os.path.exists(data_path):
        return data_path
    elif os.path.exists(root_path):
        return root_path
    else:
        raise FileNotFoundError(
            f"No se encontró el archivo 'Inventario lab.xlsx' ni en '{data_path}' ni en '{root_path}'."
        )

def main():
    excel_path = resolve_excel_path()
    print(f"Leyendo archivo de inventario desde: {excel_path}")
    
    df = pd.read_excel(excel_path)
    
    # Normalizar nombres de columnas (strip espacios)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Identificar columnas de Descripción y Cantidad
    col_desc = None
    col_cant = None
    for c in df.columns:
        c_lower = c.lower()
        if 'descripc' in c_lower or 'item' in c_lower or 'nombre' in c_lower:
            col_desc = c
        elif 'cantid' in c_lower or 'stock' in c_lower or 'total' in c_lower:
            col_cant = c
            
    if not col_desc:
        col_desc = df.columns[0]
    if not col_cant:
        col_cant = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
    print(f"Usando columna de Descripción: '{col_desc}', Cantidad: '{col_cant}'")
    
    # Convertir Cantidad a numérico y filtrar los de cantidad > 0
    df[col_cant] = pd.to_numeric(df[col_cant], errors='coerce').fillna(0)
    df_valid = df[df[col_cant] > 0].copy()
    
    total_items_validos = len(df_valid)
    total_prestamos = 0
    
    rows_tex = []
    
    for _, row in df_valid.iterrows():
        desc_raw = str(row[col_desc]).strip()
        cant_raw = row[col_cant]
        
        # Formatear cantidad (int si es entero)
        if isinstance(cant_raw, float) and cant_raw.is_integer():
            cant_display = str(int(cant_raw))
        else:
            cant_display = str(cant_raw)
            
        desc_lower = desc_raw.lower()
        
        # Clasificación de estado
        if 'living lab' in desc_lower:
            estado_tex = r"\cellcolor{azulPrestamo} Préstamo (Living Lab)"
            total_prestamos += 1
        elif any(low_item in desc_lower for low_item in LOW_STOCK_ITEMS):
            estado_tex = r"\cellcolor{amarilloAlerta} Stock Bajo"
        else:
            estado_tex = r"\cellcolor{verdeOk} Disponible"
            
        desc_escaped = escape_latex(desc_raw)
        cant_escaped = escape_latex(cant_display)
        
        rows_tex.append(f"  {desc_escaped} & {cant_escaped} & {estado_tex} \\\\")
        
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
    print("Archivo 'tabla_inventario.tex' generado exitosamente.")
    
    # Generar metricas.tex
    metricas_content = f"""\\newcommand{{\\totalItemsValidos}}{{{total_items_validos}}}
\\newcommand{{\\totalPrestamos}}{{{total_prestamos}}}
"""
    with open("metricas.tex", "w", encoding="utf-8") as f:
        f.write(metricas_content)
    print(f"Archivo 'metricas.tex' generado exitosamente (Total Ítems: {total_items_validos}, Préstamos: {total_prestamos}).")

if __name__ == "__main__":
    main()
