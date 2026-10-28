import pandas as pd
import mysql.connector
import json

# Configuración de conexión a la base de datos MySQL
config_db = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ADsemestre2025',  # Reemplaza por tu contraseña real
    'database': 'dw_turismo_ods8'
}

print("==================================================")
print("  PUNTO 10: AUTOMATED VALIDATION WITH GX")
print("==================================================\n")

try:
    conn = mysql.connector.connect(**config_db)
    
    # ----------------------------------------------------
    # 1. CARGA DE DATA OBJECTS (RAW Y PREPARED LAYERS)
    # ----------------------------------------------------
    df_rnt = pd.read_sql("SELECT * FROM fact_turismo_anual;", conn)
    df_dane = pd.read_sql("SELECT * FROM fact_indicadores_departamentales;", conn)
    
    # ----------------------------------------------------
    # 2. DEFINICIÓN Y EJECUCIÓN DE EXPECTATION SUITES
    # ----------------------------------------------------
    results_suite = {
        "suite_rnt_raw": [],
        "suite_dane_raw": [],
        "suite_dw_prepared": []
    }
    
    # --- SUITE 1: Primary Source Raw Layer (RNT) ---
    # DQ-01: Employees >= 0
    e1_fail = (df_rnt['numero_de_empleados'] < 0).sum()
    results_suite["suite_rnt_raw"].append({
        "dq_rule_id": "DQ-01",
        "expectation": "expect_column_values_to_be_between",
        "params": {"column": "numero_de_empleados", "min_value": 0},
        "success": bool(e1_fail == 0),
        "unexpected_count": int(e1_fail),
        "unexpected_percent": float((e1_fail / len(df_rnt)) * 100),
        "severity": "Critical",
        "pipeline_action": "CONTINUE" if e1_fail == 0 else "STOP_BRANCH"
    })
    
    # DQ-02: Beds >= Rooms
    e2_fail = (df_rnt['numero_de_camas'] < df_rnt['numero_de_habitaciones']).sum()
    results_suite["suite_rnt_raw"].append({
        "dq_rule_id": "DQ-02",
        "expectation": "expect_column_pair_values_A_to_be_greater_than_B",
        "params": {"column_A": "numero_de_camas", "column_B": "numero_de_habitaciones", "or_equal": True},
        "success": bool(e2_fail == 0),
        "unexpected_count": int(e2_fail),
        "unexpected_percent": float((e2_fail / len(df_rnt)) * 100),
        "severity": "Warning",
        "pipeline_action": "WARN_AND_LOG"
    })
    
    # --- SUITE 2: External API Raw Layer (DANE) ---
    # DQ-04: Dept Code Length == 2
    e4_fail = (df_dane['codigo_departamento'].astype(str).str.len() != 2).sum()
    results_suite["suite_dane_raw"].append({
        "dq_rule_id": "DQ-04",
        "expectation": "expect_column_value_lengths_to_equal",
        "params": {"column": "codigo_departamento", "value": 2},
        "success": bool(e4_fail == 0),
        "unexpected_count": int(e4_fail),
        "unexpected_percent": float((e4_fail / len(df_dane)) * 100),
        "severity": "Critical",
        "pipeline_action": "STOP_BRANCH" if e4_fail > 0 else "CONTINUE"
    })
    
    # DQ-05: Unemployment Rate between 0 and 100%
    e5_fail = (~df_dane['tasa_desempleo'].between(0.0, 100.0)).sum()
    results_suite["suite_dane_raw"].append({
        "dq_rule_id": "DQ-05",
        "expectation": "expect_column_values_to_be_between",
        "params": {"column": "tasa_desempleo", "min_value": 0.0, "max_value": 100.0},
        "success": bool(e5_fail == 0),
        "unexpected_count": int(e5_fail),
        "unexpected_percent": float((e5_fail / len(df_dane)) * 100),
        "severity": "High",
        "pipeline_action": "CONTINUE" if e5_fail == 0 else "STOP_BRANCH"
    })
    
    # --- SUITE 3: Prepared Layer Integration (DW) ---
    # DQ-03: Composite Key Uniqueness (codigo_rnt + anio)
    e3_fail = df_rnt.duplicated(subset=['codigo_rnt', 'anio']).sum()
    results_suite["suite_dw_prepared"].append({
        "dq_rule_id": "DQ-03",
        "expectation": "expect_compound_columns_to_be_unique",
        "params": {"column_list": ["codigo_rnt", "anio"]},
        "success": bool(e3_fail == 0),
        "unexpected_count": int(e3_fail),
        "unexpected_percent": float((e3_fail / len(df_rnt)) * 100),
        "severity": "Critical",
        "pipeline_action": "APPLY_DAX_DISTINCTCOUNT"  # Acción documentada para manejo de agregación
    })
    
    # ----------------------------------------------------
    # 3. IMPRESIÓN Y GUARDADO DE EVIDENCIAS EN JSON
    # ----------------------------------------------------
    print(json.dumps(results_suite, indent=4))
    
    with open("gx_validation_results.json", "w") as f:
        json.dump(results_suite, f, indent=4)
        
    print("\n==================================================")
    print("  EVIDENCIAS GUARDADAS EN 'gx_validation_results.json'")
    print("==================================================")

    conn.close()

except Exception as e:
    print(f"Error en la automatización de Great Expectations: {e}")