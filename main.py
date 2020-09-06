import socket

# START Settings

DEBUG = True
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 25565


# END Settings

def dprint(*args, **kwargs):
    """Print a debug message when DEBUG = True"""
    if DEBUG:
        print(*args, **kwargs)


def read_var_int(sock: socket.socket) -> int:
    return -100


def handle_client_socket(client_socket: socket.socket, client_address: tuple) -> None:
    """
    Handle receiving a package.

    :param client_socket:
    :param client_address:
    """
    print(f"Received a packet from {client_address[0]}:{client_address[1]}")

    # Read the first byte
    length = read_var_int(client_socket)
    print(f"Length: {length}")
    packet_id = read_var_int(client_socket)
    print(f"Packet ID: {packet_id}")

    # Close the connection
    client_socket.shutdown(True)
    client_socket.close()


def main():
    """
    Main entry point.
    """
    print("Program starting")

    print("Binding socket")
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setblocking(True)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((LISTEN_HOST, LISTEN_PORT))
    listen_socket.listen(5)

    print("Listening")

    # Continuously listen for new packets
    while True:
        client_socket, client_address = listen_socket.accept()
        handle_client_socket(client_socket, client_address)


if __name__ == '__main__':
    main()
