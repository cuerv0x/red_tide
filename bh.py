import sys
import socket
import getopt
import threading
import subprocess
from typing import Optional


escuchar = False
comando = False
subir = False
ejecutar = ""
objetivo = ""
destino_subida = ""
puerto = 0


def ejecutar_comando(cmd: str) -> bytes:
    cmd = cmd.rstrip()

    try:
        salida = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        salida = e.output

    return salida


def manejar_cliente(socket_cliente: socket.socket) -> None:
    global subir
    global ejecutar
    global comando

    if len(destino_subida):
        buffer_archivo = ""

        while True:
            datos = socket_cliente.recv(1024)

            if not datos:
                break
            else:
                buffer_archivo += datos

        try:
            descriptor_archivo = open(destino_subida, "wb")
            descriptor_archivo.write(buffer_archivo.encode("utf-8"))
            descriptor_archivo.close()

            socket_cliente.send(
                f"Archivo guardado exitosamente en {destino_subida}\r\n".encode("utf-8")
            )
        except OSError:
            socket_cliente.send(
                f"Error al guardar archivo en {destino_subida}\r\n".encode("utf-8")
            )

    if len(ejecutar):
        salida = ejecutar_comando(ejecutar)
        socket_cliente.send(salida)

    if comando:
        while True:
            socket_cliente.send("<BHP:#> ".encode("utf-8"))

            buffer_comando = b""
            while b"\n" not in buffer_comando:
                buffer_comando += socket_cliente.recv(1024)

            respuesta = ejecutar_comando(buffer_comando.decode())
            socket_cliente.send(respuesta)


def bucle_servidor() -> None:
    global objetivo
    global puerto

    if not len(objetivo):
        objetivo = "0.0.0.0"

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((objetivo, puerto))
    servidor.listen(5)

    while True:
        socket_cliente, direccion = servidor.accept()

        hilo_cliente = threading.Thread(target=manejar_cliente, args=(socket_cliente,))
        hilo_cliente.start()


def enviar_cliente(buffer: str) -> None:
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((objetivo, puerto))

        if len(buffer):
            cliente.send(buffer.encode("utf-8"))

        while True:
            longitud_recv = 1
            respuesta = b""

            while longitud_recv:
                datos = cliente.recv(4096)
                longitud_recv = len(datos)
                respuesta += datos

                if longitud_recv < 4096:
                    break

            print(respuesta.decode("utf-8"), end=" ")

            buffer = input("")
            buffer += "\n"

            cliente.send(buffer.encode("utf-8"))

    except socket.error as exc:
        print("[*] Excepción! Saliendo.")
        print(f"[*] Excepción capturada socket.error: {exc}")

        cliente.close()


def mostrar_uso() -> None:
    print("Reemplazo de Netcat")
    print()
    print("Uso: bhpnet.py -t host_objetivo -p puerto")
    print(
        "-l --listen                - escuchar en [host]:[puerto] para conexiones entrantes"
    )
    print(
        "-e --execute=archivo_ejecutar   - ejecutar el archivo dado al recibir una conexión"
    )
    print("-c --command               - inicializar una shell de comandos")
    print(
        "-u --upload=destino    - al recibir conexión subir un archivo y escribir en [destino]"
    )
    print()
    print()
    print("Ejemplos: ")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print('bhpnet.py -t 192.168.0.1 -p 5555 -l -e="cat /etc/passwd"')
    print("echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135")
    sys.exit(0)


def main() -> None:
    global escuchar
    global puerto
    global ejecutar
    global comando
    global destino_subida
    global objetivo

    if not len(sys.argv[1:]):
        mostrar_uso()

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hle:t:p:cu:",
            ["help", "listen", "execute", "target", "port", "command", "upload"],
        )
        for o, a in opts:
            if o in ("-h", "--help"):
                mostrar_uso()
            elif o in ("-l", "--listen"):
                escuchar = True
            elif o in ("-e", "--execute"):
                ejecutar = a
            elif o in ("-c", "--commandshell"):
                comando = True
            elif o in ("-u", "--upload"):
                destino_subida = a
            elif o in ("-t", "--target"):
                objetivo = a
            elif o in ("-p", "--port"):
                puerto = int(a)
            else:
                assert False, "Opción no manejada"

    except getopt.GetoptError as err:
        print(str(err))
        mostrar_uso()

    if not escuchar and len(objetivo) and puerto > 0:
        buffer = sys.stdin.read()
        enviar_cliente(buffer)

    if escuchar:
        bucle_servidor()


if __name__ == "__main__":
    main()
