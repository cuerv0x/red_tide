#!/usr/bin/env python3

import socket
import sys
import logging
from typing import Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def log_info(mensaje: str) -> None:
    print(f"[+] {mensaje}")
    logging.info(mensaje)


def log_error(mensaje: str) -> None:
    print(f"[-] {mensaje}")
    logging.error(mensaje)


def log_warning(mensaje: str) -> None:
    print(f"[!] {mensaje}")
    logging.warning(mensaje)


def obtener_entrada_usuario(mensaje: str, requerido: bool = True) -> Optional[str]:
    while True:
        try:
            entrada_usuario = input(f"[?] {mensaje}").strip()
            if not entrada_usuario and requerido:
                log_error("Este campo es requerido. Por favor intente de nuevo.")
                continue
            return entrada_usuario if entrada_usuario else None
        except KeyboardInterrupt:
            log_error("Operación cancelada por el usuario.")
            sys.exit(1)


def validar_direccion_ip(ip: str) -> bool:
    if not ip:
        return False

    partes = ip.split(".")
    if len(partes) != 4:
        return False

    try:
        for parte in partes:
            if not parte.isdigit():
                return False
            num = int(parte)
            if not 0 <= num <= 255:
                return False
        return True
    except ValueError:
        return False


def validar_puerto(puerto: str) -> bool:
    try:
        num_puerto = int(puerto)
        return 1 <= num_puerto <= 65535
    except ValueError:
        return False


def crear_socket_udp() -> socket.socket:
    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        log_info("Socket UDP creado exitosamente")
        return cliente
    except socket.error as e:
        log_error(f"Error al crear el socket UDP: {e}")
        raise


def enviar_datos(
    cliente: socket.socket, datos: bytes, servidor: Tuple[str, int]
) -> None:
    try:
        cliente.sendto(datos, servidor)
        log_info(f"Datos enviados a {servidor[0]}:{servidor[1]}")
        log_info(f"Contenido enviado: {datos}")
    except socket.error as e:
        log_error(f"Error al enviar datos: {e}")
        raise


def recibir_datos(
    cliente: socket.socket, tamano_buffer: int = 4096
) -> Tuple[bytes, Tuple[str, int]]:
    try:
        datos, direccion = cliente.recvfrom(tamano_buffer)
        log_info(f"Datos recibidos de {direccion[0]}:{direccion[1]}")
        log_info(f"Contenido recibido: {datos}")
        return datos, direccion
    except socket.error as e:
        log_error(f"Error al recibir datos: {e}")
        raise


def main() -> int:
    log_info("Cliente UDP Simple")
    print("=" * 30)
    log_info("Este script enviará datos a un servidor UDP y recibirá la respuesta.\n")

    try:
        host_servidor = obtener_entrada_usuario("Dirección IP del servidor: ")
        if not validar_direccion_ip(host_servidor):
            log_warning(
                "El formato de la dirección IP parece inválido. Continuando de todos modos..."
            )

        puerto_servidor = obtener_entrada_usuario("Puerto del servidor: ")
        if not validar_puerto(puerto_servidor):
            log_error("Puerto inválido. Debe ser un número entre 1 y 65535.")
            return 1

        puerto = int(puerto_servidor)
        servidor = (host_servidor, puerto)

        datos_a_enviar = obtener_entrada_usuario(
            "Datos a enviar (opcional, presione Enter para usar datos por defecto): ",
            requerido=False,
        )
        if not datos_a_enviar:
            datos_a_enviar = "AAABBBCCC"

        log_info("\nResumen de la conexión:")
        log_info(f"  Servidor: {host_servidor}")
        log_info(f"  Puerto: {puerto}")
        log_info(f"  Datos a enviar: {datos_a_enviar}")

        confirmar = obtener_entrada_usuario(
            "\n¿Proceder con la conexión? (s/N): ", requerido=False
        )
        if not (confirmar and confirmar.lower() in ["s", "si"]):
            log_warning("Operación cancelada.")
            return 0

        cliente = crear_socket_udp()

        try:
            enviar_datos(cliente, datos_a_enviar.encode(), servidor)

            datos_recibidos, direccion_remota = recibir_datos(cliente)

            print("\n" + "=" * 50)
            log_info("Conexión completada exitosamente")
            print(f"Datos recibidos: {datos_recibidos}")
            print(f"Desde: {direccion_remota[0]}:{direccion_remota[1]}")

        finally:
            cliente.close()
            log_info("Socket cerrado")

        return 0

    except KeyboardInterrupt:
        log_error("Operación cancelada por el usuario.")
        return 1
    except Exception as e:
        log_error(f"Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
