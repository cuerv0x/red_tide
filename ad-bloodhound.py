#!/usr/bin/env python3

import subprocess
import sys
import logging
from typing import Optional

logging.basicConfig(
    filename="bloodhound.log",
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


def validar_dominio(dominio: str) -> bool:
    if not dominio:
        return False

    if "." not in dominio:
        return False

    caracteres_validos = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-"
    )
    return all(caracter in caracteres_validos for caracter in dominio)


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


def ejecutar_bloodhound_python(
    dominio: str, usuario: str, contrasena: str, direccion_ip: str
) -> int:
    cmd = [
        "bloodhound-ce-python",
        "-d",
        dominio,
        "-u",
        usuario,
        "-p",
        contrasena,
        "-d",
        dominio,
        "-c",
        "all",
        "-ns",
        direccion_ip,
        "--zip",
    ]

    log_info(f"Ejecutando: {' '.join(cmd)}")
    print("=" * 50)

    try:
        resultado = subprocess.run(cmd, check=True, capture_output=False)
        return resultado.returncode
    except FileNotFoundError:
        log_error("Error: comando bloodhound-ce-python no encontrado.")
        log_error(
            "Por favor asegúrese de que bloodhound-ce-python esté instalado y disponible en su PATH."
        )
        return 1
    except subprocess.CalledProcessError as e:
        log_error(
            f"Error: el comando bloodhound-ce-python falló con código de salida {e.returncode}"
        )
        return e.returncode


def main() -> int:
    log_info("BloodHound Python automatizado")
    print("=" * 30)
    log_info("Este script solicitará los parámetros requeridos")
    log_info("y ejecutará bloodhound-ce-python con los valores proporcionados.\n")

    try:
        dominio = obtener_entrada_usuario("Dominio: ")
        if not validar_dominio(dominio):
            log_warning(
                "El formato del dominio parece inválido. Continuando de todos modos..."
            )

        usuario = obtener_entrada_usuario("Usuario: ")

        contrasena = obtener_entrada_usuario("Contraseña: ")

        direccion_ip = obtener_entrada_usuario("IP del Dominio: ")
        if not validar_direccion_ip(direccion_ip):
            log_warning(
                "El formato de la dirección IP parece inválido. Continuando de todos modos..."
            )

        log_info("\nParámetros:")
        log_info(f"  Dominio: {dominio}")
        log_info(f"  Usuario: {usuario}")
        log_info(f"  Contraseña: {'*' * len(contrasena)}")
        log_info(f"  Dirección IP: {direccion_ip}")

        confirmar = obtener_entrada_usuario(
            "\n¿Proceder con estos parámetros? (s/N): ", requerido=False
        )
        if confirmar and confirmar.lower() in ["s", "si"]:
            return ejecutar_bloodhound_python(
                dominio, usuario, contrasena, direccion_ip
            )
        else:
            log_warning("Operación cancelada.")
            return 0

    except KeyboardInterrupt:
        log_error("\nOperación cancelada por el usuario.")
        return 1
    except Exception as e:
        log_error(f"Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
