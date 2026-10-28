import sys
import os
from datetime import datetime

# Importamos la función de validación del script del Paso 2
try:
    from validate_prepared import validate_prepared_data
except ImportError:
    print("ERROR: No se encontró el módulo 'validate_prepared.py' en el directorio actual.")
    sys.exit(1)

def execute_prepared_gate_step3():
    """
    Ejecuta el Gate 3 de Datos Preparados y genera el registro estructurado de auditoría
    para ser capturado por la consola y los logs del orquestador.
    """
    execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("==================================================================")
    print(f"  PUNTO 14 - PASO 3: EXECUTION OF PREPARED DATA VALIDATION GATE")
    print(f"  Timestamp: {execution_time}")
    print(f"  Target Database: dw_turismo_ods8")
    print("==================================================================\n")
    
    try:
        # Invoca la suite de auditoría de los 5 invariantes
        validate_prepared_data()
        
    except SystemExit as code:
        if code.code == 0:
            print("\n[PASO 3 COMPLETO] Todos los invariantes de datos preparados pasaron exitosamente.")
            print("[PIPELINE STATUS] Estado 0 retornado. Habilitado para Carga Dimensional.")
            sys.exit(0)
        else:
            print("\n[PASO 3 BLOQUEADO] Violación crítica detectada en los datos preparados.")
            print("[PIPELINE STATUS] Estado 1 retornado. Carga Dimensional bloqueada.")
            sys.exit(1)
    except Exception as err:
        print(f"\n[PASO 3 ERROR INESPERADO] Falla durante la ejecución del Gate: {err}")
        sys.exit(1)

if __name__ == "__main__":
    execute_prepared_gate_step3()