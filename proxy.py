import sys
import socket
import threading
from typing import Optional, Tuple


def hexdump(src: bytes, length: int = 16) -> None:
    result = []
    digits = 2

    for i in range(0, len(src), length):
        s = src[i : i + length]
        hexa = b" ".join([b"%0*X" % (digits, x) for x in s])
        text = b"".join([x.to_bytes(1, "big") if 0x20 <= x < 0x7F else b"." for x in s])
        result.append(b"%04X   %-*s   %s" % (i, length * (digits + 1), hexa, text))

    print(b"\n".join(result))


def recibir_datos(conexion: socket.socket) -> bytes:
    buffer = b""
    conexion.settimeout(2)

    try:
        while True:
            datos = conexion.recv(4096)
            if not datos:
                break
            buffer += datos
    except TimeoutError:
        pass

    return buffer


def procesar_solicitud(buffer: bytes) -> bytes:
    return buffer


def procesar_respuesta(buffer: bytes) -> bytes:
    return buffer


def manejar_proxy(
    socket_cliente: socket.socket,
    host_remoto: str,
    puerto_remoto: int,
    recibir_primero: bool,
) -> None:
    socket_remoto = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_remoto.connect((host_remoto, puerto_remoto))

    if recibir_primero:
        buffer_remoto = recibir_datos(socket_remoto)
        hexdump(buffer_remoto)
        buffer_remoto = procesar_respuesta(buffer_remoto)

        if len(buffer_remoto):
            print(f"[<==] Enviando {len(buffer_remoto)} bytes al localhost.")
            socket_cliente.send(buffer_remoto)

    while True:
        buffer_local = recibir_datos(socket_cliente)

        if len(buffer_local):
            print(f"[==>] Recibidos {len(buffer_local)} bytes del localhost.")
            hexdump(buffer_local)
            buffer_local = procesar_solicitud(buffer_local)
            socket_remoto.send(buffer_local)
            print("[==>] Enviado al remoto.")

        buffer_remoto = recibir_datos(socket_remoto)

        if len(buffer_remoto):
            print(f"[<==] Recibidos {len(buffer_remoto)} bytes del remoto.")
            hexdump(buffer_remoto)
            buffer_remoto = procesar_respuesta(buffer_remoto)
            socket_cliente.send(buffer_remoto)
            print("[<==] Enviado al localhost.")

        if not len(buffer_local) or not len(buffer_remoto):
            socket_cliente.close()
            socket_remoto.close()
            print("[*] No hay más datos. Cerrando conexiones.")
            break


def bucle_servidor(
    host_local: str,
    puerto_local: int,
    host_remoto: str,
    puerto_remoto: int,
    recibir_primero: bool,
) -> None:
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        servidor.bind((host_local, puerto_local))
    except socket.error as exc:
        print(f"[!!] Error al escuchar en {host_local}:{puerto_local}")
        print("[!!] Verificar otros sockets o permisos.")
        print(f"[!!] Excepción: {exc}")
        sys.exit(1)

    print(f"[*] Escuchando en {host_local}:{puerto_local}")
    servidor.listen(5)

    while True:
        socket_cliente, direccion = servidor.accept()
        print(f"[==>] Conexión entrante desde {direccion[0]}:{direccion[1]}")

        hilo_proxy = threading.Thread(
            target=manejar_proxy,
            args=(socket_cliente, host_remoto, puerto_remoto, recibir_primero),
        )
        hilo_proxy.start()


def main() -> None:
    if len(sys.argv[1:]) != 5:
        print(
            "Uso: ./proxy.py [localhost] [puerto_local] [host_remoto] [puerto_remoto] [recibir_primero]"
        )
        print("Ejemplo: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(1)

    host_local = sys.argv[1]
    puerto_local = int(sys.argv[2])
    host_remoto = sys.argv[3]
    puerto_remoto = int(sys.argv[4])
    recibir_primero = sys.argv[5].lower() == "true"

    bucle_servidor(
        host_local, puerto_local, host_remoto, puerto_remoto, recibir_primero
    )


if __name__ == "__main__":
    main()
