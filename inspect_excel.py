import pandas as pd
import sys

try:
    file_path = 'data/raw/ReportHistory-314575560sa.xlsx'
    print(f"Leyendo archivo: {file_path}")
    
    # Leer sin header para ver todas las filas
    df = pd.read_excel(file_path, engine='openpyxl', header=None)
    
    print("\n--- Primeras 20 filas ---")
    for i in range(min(20, len(df))):
        row_values = [str(val).strip() for val in df.iloc[i].dropna().tolist() if str(val).strip() != '']
        print(f"Fila {i}: {row_values}")

except Exception as e:
    print(f"Error: {e}")
