import socket
import paramiko
import threading
import sys
from typing import Optional


clave_host = paramiko.RSAKey(filename="test_rsa.key")


class Servidor(paramiko.ServerInterface):
    def __init__(self) -> None:
        self.evento = threading.Event()

    def check_channel_request(self, tipo: str, id_canal: int) -> int:
        if tipo == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, usuario: str, contraseña: str) -> int:
        if usuario == "root" and contraseña == "toor":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


def main() -> None:
    if len(sys.argv) != 3:
        print("Uso: python bhsshserver.py <servidor> <puerto>")
        sys.exit(1)

    servidor = sys.argv[1]

    try:
        puerto_ssh = int(sys.argv[2])
        if puerto_ssh < 1 or puerto_ssh > 65535:
            print("Error: El puerto debe estar entre 1 y 65535")
            sys.exit(1)
    except ValueError:
        print("Error: El puerto debe ser un número entero")
        sys.exit(1)

    if not servidor or servidor.strip() == "":
        print("Error: El servidor no puede estar vacío")
        sys.exit(1)

    try:
        socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_servidor.bind((servidor, puerto_ssh))
        socket_servidor.listen(100)
        print("[+] Escuchando conexiones...")
        cliente, direccion = socket_servidor.accept()
    except Exception as e:
        print(f"[-] Error al escuchar: {e}")
        sys.exit(1)

    print("[+] Conexión establecida!")

    try:
        sesion_ssh = paramiko.Transport(cliente)
        sesion_ssh.add_server_key(clave_host)
        servidor_ssh = Servidor()

        try:
            sesion_ssh.start_server(server=servidor_ssh)
        except paramiko.SSHException:
            print("[-] Falló la negociación SSH.")
            return

        canal = sesion_ssh.accept(20)
        print("[+] Autenticado!")
        print(canal.recv(1024))
        canal.send("Bienvenido a bh_ssh!")

        while True:
            try:
                comando = input("Ingrese comando: ").strip("\n")
                if comando != "salida":
                    canal.send(comando)
                    print(canal.recv(1024).decode(errors="ignore") + "\n")
                else:
                    canal.send("salida")
                    print("Saliendo...")
                    sesion_ssh.close()
                    raise Exception("salida")
            except KeyboardInterrupt:
                sesion_ssh.close()
                break
            except Exception as e:
                print(f"[-] Excepción capturada: {e}")
                sesion_ssh.close()
                break
    finally:
        sys.exit(1)


if __name__ == "__main__":
    main()
