import os
import sys
import time
import schedule
import logging
import subprocess
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("programador.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def ejecutar_actualizacion():
    """Ejecuta el script de actualización"""
    try:
        logger.info("Iniciando actualización programada...")
        resultado = subprocess.run(["python", "actualizador.py", "actualizar"], 
                                  capture_output=True, text=True, check=True)
        logger.info(f"Actualización completada: {resultado.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error en la actualización: {str(e)}\n{e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return False

def programar_diario(hora="03:00"):
    """Programa una actualización diaria a la hora especificada"""
    schedule.every().day.at(hora).do(ejecutar_actualizacion)
    logger.info(f"Actualización diaria programada para las {hora}")

def programar_semanal(dia="monday", hora="03:00"):
    """Programa una actualización semanal en el día y hora especificados"""
    dias = {
        "monday": schedule.every().monday,
        "tuesday": schedule.every().tuesday,
        "wednesday": schedule.every().wednesday,
        "thursday": schedule.every().thursday,
        "friday": schedule.every().friday,
        "saturday": schedule.every().saturday,
        "sunday": schedule.every().sunday
    }
    
    if dia.lower() not in dias:
        logger.error(f"Día inválido: {dia}. Debe ser uno de: {', '.join(dias.keys())}")
        return False
    
    dias[dia.lower()].at(hora).do(ejecutar_actualizacion)
    logger.info(f"Actualización semanal programada para los {dia} a las {hora}")
    return True

def programar_mensual(dia_mes=1, hora="03:00"):
    """Programa una actualización mensual en el día del mes y hora especificados"""
    try:
        dia_mes = int(dia_mes)
        if dia_mes < 1 or dia_mes > 28:
            logger.warning("El día del mes debe estar entre 1 y 28 para evitar problemas con meses cortos")
            dia_mes = min(max(dia_mes, 1), 28)
        
        schedule.every().month.at(f"{dia_mes:02d} {hora}").do(ejecutar_actualizacion)
        logger.info(f"Actualización mensual programada para el día {dia_mes} de cada mes a las {hora}")
        return True
    except ValueError:
        logger.error(f"Día del mes inválido: {dia_mes}. Debe ser un número entre 1 y 28.")
        return False

def mostrar_programacion():
    """Muestra la programación actual"""
    jobs = schedule.get_jobs()
    if not jobs:
        print("No hay tareas programadas.")
        return
    
    print("\n=== Tareas programadas ===")
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job}")
    print()

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python programador.py [iniciar|diario|semanal|mensual|mostrar]")
        return
    
    comando = sys.argv[1].lower()
    
    if comando == "diario":
        hora = sys.argv[2] if len(sys.argv) > 2 else "03:00"
        programar_diario(hora)
        print(f"Actualización diaria programada para las {hora}")
    
    elif comando == "semanal":
        if len(sys.argv) < 3:
            print("Por favor, especifica el día de la semana: monday, tuesday, etc.")
            return
        
        dia = sys.argv[2]
        hora = sys.argv[3] if len(sys.argv) > 3 else "03:00"
        
        if programar_semanal(dia, hora):
            print(f"Actualización semanal programada para los {dia} a las {hora}")
    
    elif comando == "mensual":
        if len(sys.argv) < 3:
            print("Por favor, especifica el día del mes (1-28).")
            return
        
        dia_mes = sys.argv[2]
        hora = sys.argv[3] if len(sys.argv) > 3 else "03:00"
        
        if programar_mensual(dia_mes, hora):
            print(f"Actualización mensual programada para el día {dia_mes} de cada mes a las {hora}")
    
    elif comando == "mostrar":
        mostrar_programacion()
    
    elif comando == "iniciar":
        print("Iniciando el servicio de programación. Presiona Ctrl+C para salir.")
        
        # Configuración inicial - Puedes modificar aquí o usar los comandos
        programar_diario("03:00")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Revisar cada minuto si hay tareas pendientes
        except KeyboardInterrupt:
            print("\nServicio de programación detenido.")
    
    else:
        print(f"Comando desconocido: {comando}")
        print("Uso: python programador.py [iniciar|diario|semanal|mensual|mostrar]")

if __name__ == "__main__":
    main() 