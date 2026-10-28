import pandas as pd
import mysql.connector

# Configuración de conexión a MySQL
config_db = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ADsemestre2025', # Reemplaza por tu contraseña real de MySQL
    'database': 'dw_turismo_ods8'
}

print("==================================================")
print("  EJECUTANDO PIPELINE DE VALIDACIÓN (PUNTO 9)")
print("==================================================\n")

try:
    conn = mysql.connector.connect(**config_db)
    
    # ----------------------------------------------------
    # GATE 1: Primary Source Raw Validation (RNT)
    # ----------------------------------------------------
    print("--- GATE 1: Validando Fuente Primaria (RNT) ---")
    df_rnt_raw = pd.read_sql("SELECT * FROM fact_turismo_anual;", conn)
    
    # DQ-01: expect_column_values_to_be_between (empleados >= 0)
    dq_01_success = bool((df_rnt_raw['numero_de_empleados'] >= 0).all())
    
    # DQ-02: expect_column_pair_values_A_to_be_greater_than_B (camas >= habitaciones)
    dq_02_success = bool((df_rnt_raw['numero_de_camas'] >= df_rnt_raw['numero_de_habitaciones']).all())
    inconsistencias_camas = (df_rnt_raw['numero_de_camas'] < df_rnt_raw['numero_de_habitaciones']).sum()
    
    print(f"DQ-01 (Empleados >= 0): Exitoso = {dq_01_success}")
    print(f"DQ-02 (Camas >= Habitaciones): Exitoso = {dq_02_success} | Fallos registrados: {inconsistencias_camas} (POLÍTICA: WARNING - Permite continuidad con registro)")

    # ----------------------------------------------------
    # GATE 2: API Raw Validation (DANE)
    # ----------------------------------------------------
    print("\n--- GATE 2: Validando Fuente API (DANE) ---")
    df_dane_raw = pd.read_sql("SELECT * FROM fact_indicadores_departamentales;", conn)
    
    # DQ-04: expect_column_value_lengths_to_equal (codigo_departamento == 2 caracteres)
    dq_04_success = bool((df_dane_raw['codigo_departamento'].astype(str).str.len() == 2).all())
    
    # DQ-05: expect_column_values_to_be_between (tasas entre 0% y 100%)
    dq_05_desempleo = bool(df_dane_raw['tasa_desempleo'].between(0.0, 100.0).all())
    dq_05_informalidad = bool(df_dane_raw['tasa_informalidad'].between(0.0, 100.0).all())
    
    print(f"DQ-04 (Codigo Depto Longitud 2): Exitoso = {dq_04_success}")
    print(f"DQ-05 (Rango Tasa Desempleo 0-100%): Exitoso = {dq_05_desempleo}")
    print(f"DQ-05 (Rango Tasa Informalidad 0-100%): Exitoso = {dq_05_informalidad}")

    # ----------------------------------------------------
    # GATE 3: Prepared Data Validation (DW Integration)
    # ----------------------------------------------------
    print("\n--- GATE 3: Validando Datos Preparados para DW ---")
    
    # DQ-03: expect_compound_columns_to_be_unique (codigo_rnt + anio)
    duplicados_clave = df_rnt_raw.duplicated(subset=['codigo_rnt', 'anio']).sum()
    dq_03_success = bool(duplicados_clave == 0)
    
    print(f"DQ-03 (Unicidad Clave Compuesta codigo_rnt + anio): Exitoso = {dq_03_success}")

    print("\n==================================================")
    print("  VALIDACIÓN COMPLETADA EXITOSAMENTE")
    print("==================================================")

    conn.close()

except Exception as e:
    print(f"Error durante la ejecución del pipeline de validación: {e}")