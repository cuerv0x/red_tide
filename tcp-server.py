import socket
import threading
import re


def validar_ip(ip):
    try:
        partes = ip.split(".")
        if len(partes) != 4:
            return False
        for parte in partes:
            if not parte.isdigit() or not 0 <= int(parte) <= 255:
                return False
        return True
    except:
        return False


def validar_puerto(puerto):
    try:
        puerto_int = int(puerto)
        return 1 <= puerto_int <= 65535
    except ValueError:
        return False


while True:
    ip = input("Ingrese dirección IP: ")
    if validar_ip(ip):
        break
    print("Dirección IP inválida. Intente nuevamente.")

while True:
    puerto = input("Ingrese número de puerto: ")
    if validar_puerto(puerto):
        puerto = int(puerto)
        break
    print("Puerto inválido. Debe estar entre 1 y 65535.")

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((ip, puerto))
servidor.listen(5)

print(f"[*] Escuchando en {ip}:{puerto}")


def manejar_cliente(socket_cliente):
    solicitud = socket_cliente.recv(1024)
    print(f"[*] Recibido: {solicitud}")
    socket_cliente.send(b"ACK!")
    print(socket_cliente.getpeername())
    socket_cliente.close()


while True:
    cliente, direccion = servidor.accept()
    print(f"[*] Conexión aceptada desde: {direccion[0]}:{direccion[1]}")
    manejador_cliente = threading.Thread(target=manejar_cliente, args=(cliente,))
    manejador_cliente.start()
