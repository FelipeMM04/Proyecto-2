import pandas as pd
import mysql.connector

# 1. Configuración de conexión a tu base de datos MySQL
config_db = {
    'host': 'localhost',
    'user': 'root',          
    'password': 'ADsemestre2025', 
    'database': 'dw_turismo_ods8'
}

print("==================================================")
print("  INICIANDO PERFILAMIENTO REAL DE DATOS (PUNTO 7)")
print("==================================================\n")

try:
    conn = mysql.connector.connect(**config_db)
    
    # --- A. PERFILAMIENTO FUENTE PRIMARIA (Tabla de hechos turismo) ---
    query_turismo = "SELECT * FROM fact_turismo_anual;"
    df_turismo = pd.read_sql(query_turismo, conn)
    
    print("--- 1. FUENTE PRIMARIA: fact_turismo_anual ---")
    print(f"Total de registros reales: {len(df_turismo)}")
    print(f"Total de PST únicos (codigo_rnt): {df_turismo['codigo_rnt'].nunique()}")
    print(f"Duplicados en codigo_rnt (por año): {df_turismo['codigo_rnt'].duplicated().sum()}")
    print("\nConteo de valores nulos:")
    print(df_turismo.isnull().sum())
    
    print("\nEstadísticas descriptivas (Empleados, Habitaciones, Camas):")
    print(df_turismo[['numero_de_empleados', 'numero_de_habitaciones', 'numero_de_camas']].describe())
    
    # Validación de inconsistencia lógica (Camas < Habitaciones)
    inconsistencias_camas = df_turismo[df_turismo['numero_de_camas'] < df_turismo['numero_de_habitaciones']]
    print(f"\nRegistros con camas < habitaciones: {len(inconsistencias_camas)}")

    # --- B. PERFILAMIENTO FUENTE EXTERNA (API DANE / Tabla DANE) ---
    query_dane = "SELECT * FROM fact_indicadores_departamentales;"
    df_dane = pd.read_sql(query_dane, conn)
    
    print("\n--------------------------------------------------")
    print("--- 2. FUENTE EXTERNA: fact_indicadores_departamentales (API DANE) ---")
    print(f"Total de departamentos en la tabla: {len(df_dane)}")
    print("\nTipos de datos detectados:")
    print(df_dane.dtypes)
    
    print("\nRango real de Tasa de Informalidad y Desempleo:")
    print(df_dane[['tasa_informalidad', 'tasa_desempleo']].describe())

    conn.close()

except Exception as e:
    print(f"Error al conectar o consultar MySQL: {e}")