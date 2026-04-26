import pandas as pd
from logic import procesar_conciliacion, _limpiar_monto

banco = pd.DataFrame({
    'Fecha': ['2023-01-01'],
    'Monto': ['1.234,56'],
    'Desc': ['PAGO PROVEEDOR ABC']
})

conta = pd.DataFrame({
    'Fecha': ['2023-01-01'],
    'Monto': ['1234.56'],
    'Desc': ['PAGO A PROVEEDOR ABC']
})

coinc, solo_b, solo_c = procesar_conciliacion(
    banco, conta,
    'Fecha', 'Monto', 'Desc',
    'Fecha', 'Monto', 'Desc'
)
print("--- TEST 1: FORMATOS DIFERENTES ---")
print("Coincidencias:", len(coinc))
print("Solo banco:", len(solo_b))
print("Solo conta:", len(solo_c))

banco2 = pd.DataFrame({
    'Fecha': ['2023-01-01'],
    'Monto': [123.45],
    'Desc': ['DEPOSITO']
})

conta2 = pd.DataFrame({
    'Fecha': ['2023-01-01'],
    'Monto': [123.4500000000001],
    'Desc': ['DEPOSITO']
})

coinc2, solo_b2, solo_c2 = procesar_conciliacion(
    banco2, conta2,
    'Fecha', 'Monto', 'Desc',
    'Fecha', 'Monto', 'Desc'
)
print("--- TEST 2: PRECISIÓN FLOTANTE ---")
print("Coincidencias:", len(coinc2))

banco3 = pd.DataFrame({
    'Fecha': ['2023-01-01'],
    'Monto': ['-100.00'],
    'Desc': ['DEPOSITO']
})

conta3 = pd.DataFrame({
    'Fecha': ['2023-01-01'],
    'Monto': ['100.00'],
    'Desc': ['DEPOSITO']
})

coinc3, solo_b3, solo_c3 = procesar_conciliacion(
    banco3, conta3,
    'Fecha', 'Monto', 'Desc',
    'Fecha', 'Monto', 'Desc'
)
print("--- TEST 3: SIGNOS DIFERENTES ---")
print("Coincidencias:", len(coinc3))
