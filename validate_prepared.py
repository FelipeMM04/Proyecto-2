import sys
import mysql.connector
import pandas as pd

# Configuración de conexión a MySQL dw_turismo_ods8
config_db = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ADsemestre2025',  # Reemplaza con tu contraseña de MySQL
    'database': 'dw_turismo_ods8'
}

def validate_prepared_data():
    print("==================================================")
    print("  EJECUTANDO GATE DE VALIDACIÓN PREPARADA (PUNTO 14)")
    print("==================================================\n")
    
    critical_failures = 0
    warning_count = 0

    try:
        conn = mysql.connector.connect(**config_db)
        
        # 1. Esquema y Lectura de Capa Preparada
        df_turismo = pd.read_sql("SELECT * FROM fact_turismo_anual;", conn)
        df_dane = pd.read_sql("SELECT * FROM fact_indicadores_departamentales;", conn)
        
        # ----------------------------------------------------
        # INVARIANTE 1: Esquema y Campos Obligatorios (NOT NULL)
        # ----------------------------------------------------
        null_turismo = df_turismo[['id_fact', 'codigo_rnt', 'codigo_municipio', 'anio']].isnull().sum().sum()
        null_dane = df_dane[['id_indicador', 'codigo_departamento', 'anio']].isnull().sum().sum()
        
        if null_turismo == 0 and null_dane == 0:
            print("✔ Invariante 1 (Campos Obligatorios NOT NULL): PASADO")
        else:
            print(f"✖ Invariante 1 ERROR: Nulos detectados -> Turismo: {null_turismo}, DANE: {null_dane}")
            critical_failures += 1

        # ----------------------------------------------------
        # INVARIANTE 2: Rangos y Dominios Válidos (DQ-01, DQ-05)
        # ----------------------------------------------------
        emp_negativos = (df_turismo['numero_de_empleados'] < 0).sum()
        tasas_invalidas = ((df_dane['tasa_desempleo'] < 0) | (df_dane['tasa_desempleo'] > 100) |
                           (df_dane['tasa_informalidad'] < 0) | (df_dane['tasa_informalidad'] > 100)).sum()
        
        if emp_negativos == 0 and tasas_invalidas == 0:
            print("✔ Invariante 2 (Rangos Válidos Empleo y Tasas DANE): PASADO")
        else:
            print(f"✖ Invariante 2 ERROR: Empleados < 0: {emp_negativos}, Tasas fuera de rango: {tasas_invalidas}")
            critical_failures += 1

        # ----------------------------------------------------
        # INVARIANTE 3: Conformidad de Códigos DANE (DQ-04)
        # ----------------------------------------------------
        # Verifica formato de 2 caracteres en departamento
        depto_invalidos = (df_dane['codigo_departamento'].astype(str).str.zfill(2).str.len() != 2).sum()
        if depto_invalidos == 0:
            print("✔ Invariante 3 (Conformidad Código DANE zfill(2)): PASADO")
        else:
            print(f"✖ Invariante 3 ERROR: Códigos DANE deformados: {depto_invalidos}")
            critical_failures += 1

        # ----------------------------------------------------
        # INVARIANTE 4: Unicidad y Evaluación de Grano
        # ----------------------------------------------------
        # Verificación de ID Primario en Fact
        duplicados_id = df_turismo.duplicated(subset=['id_fact']).sum()
        if duplicados_id == 0:
            print("✔ Invariante 4 (Unicidad Clave Primaria id_fact): PASADO")
        else:
            print(f"✖ Invariante 4 ERROR: Claves id_fact duplicadas: {duplicados_id}")
            critical_failures += 1

        # ----------------------------------------------------
        # INVARIANTE 5: Preparación Analítica R1 - R7
        # ----------------------------------------------------
        if len(df_turismo) > 0 and len(df_dane) > 0:
            print("✔ Invariante 5 (Aptitud Analítica R1-R7): PASADO")
        else:
            print("✖ Invariante 5 ERROR: Datasets vacíos para la analítica.")
            critical_failures += 1

        conn.close()

        # ----------------------------------------------------
        # DECISIÓN DEL GATE Y RESPUETA DEL PIPELINE
        # ----------------------------------------------------
        print("\n--------------------------------------------------")
        if critical_failures == 0:
            print("STATUS GATE: VALIDACIÓN EXITOSA -> Proceder a Carga Dimensional")
            print("--------------------------------------------------\n")
            sys.exit(0)
        else:
            print(f"STATUS GATE: BLOQUEADO -> {critical_failures} violaciones críticas encontradas.")
            print("--------------------------------------------------\n")
            sys.exit(1)

    except Exception as e:
        print(f"Error grave al conectar o consultar MySQL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    validate_prepared_data()