# Changelog

## [2025-11-25] - Soporte para archivos Excel

### ✨ Nuevas características
- **Soporte para archivos XLSX/XLS**: Ahora el sistema acepta archivos de Excel además de CSV
  - Formatos soportados: `.csv`, `.xlsx`, `.xls`
  - Validación automática de extensiones en el endpoint de upload
  - Detección automática del formato de archivo para procesamiento

### 🔧 Cambios técnicos
- **TradeParserService**:
  - Renombrado: `load_trades_from_csv()` → `load_trades_from_file()`
  - Agregada detección automática de extensión de archivo
  - Uso de `pd.read_excel()` con engine `openpyxl` para archivos Excel
  
- **Analytics API**:
  - Actualizado endpoint `/upload-trades` con validación de extensiones
  - Todos los endpoints ahora buscan archivos `.csv`, `.xlsx`, y `.xls`
  - Mensajes de error más descriptivos

### 📦 Dependencias
- Ya incluye `openpyxl==3.1.2` en requirements.txt

### 🚀 Uso
```python
# Ahora puedes subir tanto CSV como Excel
POST /api/v1/analytics/upload-trades
Content-Type: multipart/form-data

file: operaciones_mt5.xlsx  # ✅ Ahora funciona!
file: operaciones_mt5.csv   # ✅ También funciona!
```
