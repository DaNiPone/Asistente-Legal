import json
import sys
import subprocess
import time

def main():
    # Cargar las URLs del archivo JSON
    try:
        with open('urls_a_agregar.json', 'r', encoding='utf-8') as f:
            urls = json.load(f)
    except Exception as e:
        print(f"Error al cargar el archivo JSON: {str(e)}")
        return
    
    # Contar cuántas URLs hay para agregar
    total = len(urls)
    print(f"Se van a agregar {total} URLs a la lista de vigiladas.")
    
    # Agregar cada URL a la lista de vigiladas
    for i, item in enumerate(urls, 1):
        url = item.get('url')
        desc = item.get('descripcion', '')
        
        if not url:
            print(f"[{i}/{total}] Error: URL vacía, omitiendo...")
            continue
        
        print(f"[{i}/{total}] Agregando: {desc}")
        
        try:
            # Ejecutar el comando para agregar la URL
            comando = ["python", "actualizador.py", "agregar", url, desc]
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                print(f"  ✓ Agregada correctamente")
                # Si la salida contiene "ya está en la lista", informar
                if "ya está en la lista" in resultado.stdout:
                    print(f"  ℹ Esta URL ya estaba en la lista")
            else:
                print(f"  ✗ Error al agregar: {resultado.stderr}")
        
        except Exception as e:
            print(f"  ✗ Error al ejecutar el comando: {str(e)}")
        
        # Pequeña pausa para evitar problemas
        time.sleep(1)
    
    print("\nProceso completado. Listando URLs vigiladas:")
    # Listar las URLs vigiladas para verificar
    subprocess.run(["python", "actualizador.py", "listar"])

if __name__ == "__main__":
    main() 