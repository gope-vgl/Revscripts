import sys
import csv
import os
from datetime import datetime
import paramiko
from paramiko import SSHClient, AutoAddPolicy

def execute_ssh_command(ip, username, password, equipo, ssh_client, output_file):
    # Obtener la fecha y hora actual en formato 'YYYY-MM-DD_HH-MM-SS'
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    try:
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(ip, username=username, password=password)

        # Obtener el hostname
        stdin, stdout, stderr = ssh_client.exec_command('hostname')
        server_name = stdout.read().decode().strip()

        # Comando de red específico
        command = """ip -o link show | grep -E "master bond0|master bond1" | awk '{for(i=1;i<=NF;i++) if($i=="state") print $2, $(i+1), $(i-1)}' | sed 's/://'"""
        stdin, stdout, stderr = ssh_client.exec_command(command)
        command_output = stdout.read().decode()
        error_output = stderr.read().decode()

        if error_output:
            print(f"Error al ejecutar comando en {ip}: {error_output}")
            return

        full_output = f"Servidor: {server_name}\nFecha y Hora: {timestamp}\n\n"
        full_output += f"--- Salida del comando de red ---\n{command_output}\n"
        full_output += f"{'-'*50}\n"

        with open(output_file, 'a') as f:
            f.write(full_output)

        print(f"Salida del comando para {server_name} guardada.")
    except Exception as e:
        print(f"Error al procesar {ip}: {e}")
    finally:
        ssh_client.close()

if __name__ == "__main__":

    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    datosssh_csv_path = os.path.join(application_path, 'datosssh.csv')

    # Carpeta 'screenshots' para guardar el historial de resultados
    screenshots_dir = os.path.join(application_path, 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)

    # Crear archivo de salida con timestamp único
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(screenshots_dir, f'{timestamp}.txt')

    with open(datosssh_csv_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ilo_ip = row['ILO']
            username = row['User']
            password = row['Pass']
            equipo = row['Equipo']
            print(f"Conectando a {ilo_ip} ({equipo})...")

            ssh_client = SSHClient()
            execute_ssh_command(ilo_ip, username, password, equipo, ssh_client, output_file)

            print("-" * 50)