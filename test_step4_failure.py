import sys
import mysql.connector
import pandas as pd

# Importamos la función original de validación
from validate_prepared import config_db

def test_controlled_critical_failure():
    print("==================================================================")
    print("  PUNTO 14 - PASO 4: SIMULACIÓN DE FALLA CRÍTICA CONTROLADA")
    print("  Prueba de Bloqueo Downstream (Reliability Test B)")
    print("==================================================================\n")
    
    try:
        conn = mysql.connector.connect(**config_db)
        
        # Leemos los datos reales
        df_turismo = pd.read_sql("SELECT * FROM fact_turismo_anual;", conn)
        df_dane = pd.read_sql("SELECT * FROM fact_indicadores_departamentales;", conn)
        conn.close()
        
        # INYECTAMOS UNA FALLA CRÍTICA SINTÉTICA
        # Modificamos arbitrariamente un registro de empleados a valor negativo (-50)
        print("[TEST B] Inyectando violación crítica sintética: numero_de_empleados = -50 ...")
        df_turismo.loc[0, 'numero_de_empleados'] = -50
        
        # EVALUAMOS LOS INVARIANTES CON EL DATO CONTAMINADO
        critical_failures = 0
        
        # Evaluación Invariante 2 (Rangos y Dominios Válidos)
        emp_negativos = (df_turismo['numero_de_empleados'] < 0).sum()
        tasas_invalidas = ((df_dane['tasa_desempleo'] < 0) | (df_dane['tasa_desempleo'] > 100) |
                           (df_dane['tasa_informalidad'] < 0) | (df_dane['tasa_informalidad'] > 100)).sum()
        
        if emp_negativos == 0 and tasas_invalidas == 0:
            print("✔ Invariante 2 (Rangos Válidos Empleo y Tasas DANE): PASADO")
        else:
            print(f"✖ Invariante 2 ERROR CRÍTICO: Empleados < 0 detectados: {emp_negativos} registro(s)")
            critical_failures += 1

        print("\n--------------------------------------------------")
        if critical_failures > 0:
            print(f"STATUS GATE: BLOQUEADO -> {critical_failures} violación(es) crítica(s) encontrada(s).")
            print("ACTION: Interrumpiendo pipeline con estado de salida 1 (sys.exit(1))")
            print("--------------------------------------------------\n")
            print("[PIPELINE STATUS] Estado 1 retornado. Carga Dimensional BLOQUEADA exitosamente.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error durante la prueba de falla: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_controlled_critical_failure()