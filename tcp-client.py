#!/usr/bin/env python3

import socket
import re
from typing import Tuple, Optional
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validar_host(host: str) -> bool:
    if not host or not isinstance(host, str):
        return False

    patron_dominio = r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"

    patron_ip = r"^(\d{1,3}\.){3}\d{1,3}$"

    if re.match(patron_dominio, host):
        return True

    if re.match(patron_ip, host):
        octetos = host.split(".")
        return all(0 <= int(octeto) <= 255 for octeto in octetos)

    return False


def validar_puerto(puerto: int) -> bool:
    return isinstance(puerto, int) and 1 <= puerto <= 65535


def pedir_host() -> str:
    while True:
        host = input(
            "Ingrese el host objetivo (ej: www.google.com o 192.168.1.1): "
        ).strip()
        if validar_host(host):
            return host
        else:
            print("Host inválido. Intente nuevamente.")


def pedir_puerto() -> int:
    while True:
        try:
            puerto = input("Ingrese el puerto objetivo (1-65535): ").strip()
            puerto_int = int(puerto)
            if validar_puerto(puerto_int):
                return puerto_int
            else:
                print("Puerto inválido. Debe estar entre 1 y 65535.")
        except ValueError:
            print("Puerto inválido. Debe ser un número entero.")


def crear_conexion_tcp(
    host: str, puerto: int, tiempo_espera: int = 10
) -> Optional[socket.socket]:
    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.settimeout(tiempo_espera)

        logger.info(f"Conectando a {host}:{puerto}...")
        cliente.connect((host, puerto))
        logger.info("Conexión establecida exitosamente")

        return cliente

    except socket.timeout:
        logger.error(f"Timeout al conectar a {host}:{puerto}")
        return None
    except socket.error as error:
        logger.error(f"Error de conexión a {host}:{puerto}: {error}")
        return None


def enviar_solicitud_http(cliente: socket.socket, host: str, ruta: str = "/") -> bool:
    try:
        solicitud = f"GET {ruta} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

        logger.info(f"Enviando solicitud HTTP a {host}{ruta}")
        cliente.send(solicitud.encode("utf-8"))
        logger.info("Solicitud enviada exitosamente")

        return True

    except socket.error as error:
        logger.error(f"Error al enviar solicitud: {error}")
        return False


def recibir_respuesta(
    cliente: socket.socket, tamano_buffer: int = 4096
) -> Optional[bytes]:
    try:
        logger.info("Recibiendo respuesta del servidor...")
        respuesta = cliente.recv(tamano_buffer)
        logger.info(f"Respuesta recibida: {len(respuesta)} bytes")

        return respuesta

    except socket.error as error:
        logger.error(f"Error al recibir respuesta: {error}")
        return None


def main() -> None:
    print("Cliente TCP")
    print("=" * 40)

    host_objetivo = pedir_host()
    puerto_objetivo = pedir_puerto()

    print(f"\nConfiguración:")
    print(f"   Host: {host_objetivo}")
    print(f"   Puerto: {puerto_objetivo}")
    print("=" * 40)

    logger.info("=== Cliente TCP ===")
    logger.info(f"Host objetivo: {host_objetivo}")
    logger.info(f"Puerto objetivo: {puerto_objetivo}")

    logger.info("Parámetros validados correctamente")

    cliente = crear_conexion_tcp(host_objetivo, puerto_objetivo)
    if cliente is None:
        logger.error("No se pudo establecer la conexión")
        return

    try:
        if not enviar_solicitud_http(cliente, host_objetivo):
            logger.error("No se pudo enviar la solicitud")
            return

        respuesta = recibir_respuesta(cliente)
        if respuesta is None:
            logger.error("No se pudo recibir la respuesta")
            return

        print("\n" + "=" * 50)
        print("RESPUESTA DEL SERVIDOR:")
        print("=" * 50)
        try:
            print(respuesta.decode("utf-8"))
        except UnicodeDecodeError:
            print("Respuesta (bytes):", respuesta)
        print("=" * 50)

    finally:
        logger.info("Cerrando conexión...")
        cliente.close()
        logger.info("Conexión cerrada")


if __name__ == "__main__":
    main()
