import pandas as pd
from rapidfuzz import fuzz
from typing import Optional

def _limpiar_monto(s: pd.Series) -> pd.Series:
    """Función auxiliar para limpiar los montos y asegurar que sean numéricos."""
    s_str = s.astype(str)
    s_str = s_str.str.replace(r'[^\d,\.\-]', '', regex=True)
    
    def format_number(val):
        if pd.isna(val) or val == '': 
            return val
        val = str(val)
        
        last_comma = val.rfind(',')
        last_dot = val.rfind('.')
        
        if last_comma > -1 and last_dot > -1:
            if last_comma > last_dot:
                # Formato 1.234,56
                val = val.replace('.', '').replace(',', '.')
            else:
                # Formato 1,234.56
                val = val.replace(',', '')
        elif last_comma > -1:
            if val.count(',') > 1 or (len(val) - last_comma == 4):
                val = val.replace(',', '')
            else:
                val = val.replace(',', '.')
        elif last_dot > -1:
            if val.count('.') > 1 or (len(val) - last_dot == 4):
                val = val.replace('.', '')
                
        return val

    s_str = s_str.apply(format_number)
    # Convertimos a numérico, aplicamos valor absoluto (por diferencias Debe/Haber o retiros/depósitos) y redondeamos a 2 decimales para precisión
    num = pd.to_numeric(s_str, errors='coerce')
    return num.abs().round(2)

def procesar_conciliacion(
    df_banco: pd.DataFrame, 
    df_contable: pd.DataFrame, 
    col_fecha_banco: Optional[str], 
    col_monto_banco: str, 
    col_desc_banco: Optional[str], 
    col_fecha_conta: Optional[str], 
    col_monto_conta: str, 
    col_desc_conta: Optional[str]
):
    # Crear copias para no alterar los originales y evitar SettingWithCopyWarning
    banco = df_banco.copy()
    contable = df_contable.copy()
    
    # Limpieza de montos y forzado a numérico utilizando .loc
    banco.loc[:, '_monto_clean'] = _limpiar_monto(banco[col_monto_banco])
    contable.loc[:, '_monto_clean'] = _limpiar_monto(contable[col_monto_conta])
    
    # Generar identificadores únicos
    banco.loc[:, '_id'] = range(len(banco))
    contable.loc[:, '_id'] = range(len(contable))
    
    matched_b = set()
    matched_l = set()
    coincidencias_list = []
    
    # Agrupamos por monto para optimizar la búsqueda
    for monto, group_b in banco.groupby('_monto_clean'):
        if pd.isna(monto): 
            continue
        
        group_l = contable[contable['_monto_clean'] == monto]
        if group_l.empty: 
            continue
        
        for _, row_b in group_b.iterrows():
            if row_b['_id'] in matched_b: 
                continue
            
            best_match = None
            best_score = -1
            
            for _, row_l in group_l.iterrows():
                if row_l['_id'] in matched_l: 
                    continue
                
                # Evaluación Fuzzy si hay descripciones disponibles
                if col_desc_banco and col_desc_conta:
                    desc_b = str(row_b[col_desc_banco])
                    desc_l = str(row_l[col_desc_conta])
                    score = fuzz.token_sort_ratio(desc_b, desc_l)
                else:
                    score = 100
                
                if score > best_score:
                    best_score = score
                    best_match = row_l
            
            # Si se encuentra una coincidencia de monto exacta, se asume match.
            # El fuzzy score (similitud) sirve para decidir en caso de empate de montos.
            if best_match is not None:
                matched_b.add(row_b['_id'])
                matched_l.add(best_match['_id'])
                
                res = {}
                for c in df_banco.columns:
                    res[f'{c}_banco'] = row_b[c]
                for c in df_contable.columns:
                    res[f'{c}_contable'] = best_match[c]
                res['Similitud_Detalle_%'] = best_score
                coincidencias_list.append(res)
                
    coincidencias = pd.DataFrame(coincidencias_list)
    solo_banco = banco[~banco['_id'].isin(matched_b)].drop(columns=['_id', '_monto_clean'])
    solo_contable = contable[~contable['_id'].isin(matched_l)].drop(columns=['_id', '_monto_clean'])
    
    return coincidencias, solo_banco, solo_contable
