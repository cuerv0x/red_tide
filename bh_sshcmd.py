import paramiko
import sys
import getopt
from typing import Optional


def comando_ssh(ip: str, usuario: str, contrasena: str, comando: str) -> None:
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cliente.connect(ip, username=usuario, password=contrasena)
    sesion_ssh = cliente.get_transport().open_session()

    if sesion_ssh.active:
        sesion_ssh.exec_command(comando)
        print(sesion_ssh.recv(1024))

    cliente.close()


def mostrar_uso() -> None:
    print("Uso: python bh_sshcmd.py -i <ip> -u <usuario> -p <contraseña> -c <comando>")
    print(
        "Ejemplo: python bh_sshcmd.py -i 192.168.2.200 -u Odin -p vibor4sExisten -c ClientConnected"
    )
    sys.exit(1)


def main() -> None:
    if len(sys.argv) < 9:
        mostrar_uso()

    ip = ""
    usuario = ""
    contrasena = ""
    comando = ""

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "i:u:p:c:h",
            ["ip=", "usuario=", "contrasena=", "comando=", "help"],
        )
        for o, a in opts:
            if o in ("-h", "--help"):
                mostrar_uso()
            elif o in ("-i", "--ip"):
                ip = a
            elif o in ("-u", "--usuario"):
                usuario = a
            elif o in ("-p", "--contrasena"):
                contrasena = a
            elif o in ("-c", "--comando"):
                comando = a
            else:
                assert False, "Opción no manejada"
    except getopt.GetoptError as err:
        print(f"Error: {err}")
        mostrar_uso()

    if not ip or not usuario or not contrasena or not comando:
        print("Error: Todos los parámetros son requeridos")
        mostrar_uso()

    if (
        not ip.strip()
        or not usuario.strip()
        or not contrasena.strip()
        or not comando.strip()
    ):
        print("Error: Los parámetros no pueden estar vacíos")
        mostrar_uso()

    comando_ssh(ip, usuario, contrasena, comando)


if __name__ == "__main__":
    main()
