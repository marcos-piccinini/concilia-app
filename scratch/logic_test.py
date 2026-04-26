import pandas as pd
from rapidfuzz import fuzz
from typing import Optional

def _limpiar_monto(s: pd.Series) -> pd.Series:
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
                val = val.replace('.', '').replace(',', '.')
            else:
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
    banco = df_banco.copy()
    contable = df_contable.copy()
    
    banco.loc[:, '_monto_clean'] = _limpiar_monto(banco[col_monto_banco])
    contable.loc[:, '_monto_clean'] = _limpiar_monto(contable[col_monto_conta])
    
    banco.loc[:, '_id'] = range(len(banco))
    contable.loc[:, '_id'] = range(len(contable))
    
    matched_b = set()
    matched_l = set()
    coincidencias_list = []
    
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
                
                if col_desc_banco and col_desc_conta:
                    desc_b = str(row_b[col_desc_banco])
                    desc_l = str(row_l[col_desc_conta])
                    score = fuzz.token_sort_ratio(desc_b, desc_l)
                else:
                    score = 100
                
                if score > best_score:
                    best_score = score
                    best_match = row_l
            
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
