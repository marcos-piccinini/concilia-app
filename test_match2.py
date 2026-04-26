import pandas as pd
from logic import procesar_conciliacion

banco4 = pd.DataFrame({
    'Fecha': ['2023-01-01'],
    'Monto': ['1.234'],
    'Desc': ['DEPOSITO']
})
conta4 = pd.DataFrame({
    'Fecha': ['2023-01-01'],
    'Monto': ['1234.00'],
    'Desc': ['DEPOSITO']
})
coinc4, _, _ = procesar_conciliacion(banco4, conta4, 'Fecha', 'Monto', 'Desc', 'Fecha', 'Monto', 'Desc')
print("--- TEST 4: SIN DECIMALES PERO CON PUNTO ---")
print("Coincidencias:", len(coinc4))

banco5 = pd.DataFrame({
    'Fecha': ['2023-01-01'],
    'Monto': ['1234.00'],
    'Desc': ['TRANSF']
})
conta5 = pd.DataFrame({
    'Fecha': ['2023-01-01'],
    'Monto': ['1234.00'],
    'Desc': ['COMPRA DE INSUMOS VARIOS']
})
coinc5, _, _ = procesar_conciliacion(banco5, conta5, 'Fecha', 'Monto', 'Desc', 'Fecha', 'Monto', 'Desc')
print("--- TEST 5: DESCRIPCIONES MUY DISTINTAS ---")
print("Coincidencias:", len(coinc5))

