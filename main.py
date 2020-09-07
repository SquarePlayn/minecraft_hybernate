import socket
from typing import Tuple

# START Settings

DEBUG = True
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 25565


# END Settings

def dprint(*args, **kwargs):
    """
    Print a debug message when DEBUG = True
    """
    if DEBUG:
        print(*args, **kwargs)


def rshift(value: int, n: int) -> int:
    """
    Move the bits of a value n positions to the right, including the sign bit
    @param value: Value to move
    @param n: Number of positions to move
    @return: Value with its bits moved n positions to the right
    """
    if value >= 0:
        return value >> n
    else:
        return (value + (1 << 32)) >> n


def read_var_int(sock: socket.socket) -> Tuple[int, int]:
    """
    Read a VarInt from a socket stream
    """
    result = 0
    for bytes_read in range(5):
        read = ord(sock.recv(1))
        value = read & 0b01111111
        result |= (value << (7 * bytes_read))

        if read & 0b10000000 == 0:
            return result, bytes_read + 1

    raise Exception("More than 5 bytes in VarInt")


def read_string(sock: socket.socket) -> Tuple[str, int]:
    """
    Read a string from a socket stream
    """
    length, num_read = read_var_int(sock)
    read = sock.recv(length)
    result = read.decode("utf-8")
    return result, num_read


def read_unsigned_short(sock: socket.socket) -> Tuple[int, int]:
    """
    Read an unsigned short from a socket stream
    @param sock:
    @return:
    """
    return ord(sock.recv(1)) * (2 ** 8) + ord(sock.recv(1)), 2


def encode_var_int(value: int) -> bytearray:
    """
    Encode a Python integer as an MC VarInt type
    @param value:
    @return:
    """
    result = bytearray(0)
    for i in range(100):
        temp = value & 0b01111111
        value = rshift(value, 7)
        if value != 0:
            temp |= 0b10000000
        result.append(temp)
        if value == 0:
            return result


def encode_string(text: str) -> bytearray:
    """
    Encode a Python string as an MC String type
    @param text:
    @return:
    """
    str_enc = text.encode('utf-8')
    str_enc_len = len(str_enc)
    str_enc_len_enc = encode_var_int(str_enc_len)
    result = str_enc_len_enc + str_enc
    return result


def encode_packet(packet_id: int, contents: bytearray) -> bytearray:
    """
    Encode a packet so it can be sent to a client
    @param packet_id:
    @param contents:
    @return:
    """
    # Packet: Length of ID+Contents - Packet ID - Contents
    packet_id_enc = encode_var_int(packet_id)
    main_data = packet_id_enc + contents
    main_length = len(main_data)
    main_length_enc = encode_var_int(main_length)
    packet = main_length_enc + main_data
    return packet


def send_packet(packet_id: int, content: bytearray, sock: socket.socket) -> None:
    """
    Send a packet

    @param packet_id:
    @param content:
    @param sock:
    @return:
    """
    packet = encode_packet(packet_id, content)
    sock.sendall(packet)


def handle_client_socket(client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
    """
    Handle receiving a package.

    :param client_socket:
    :param client_address:
    """
    print(f"Received a packet from {client_address[0]}:{client_address[1]}")

    # Read length and packet_id (present on any packet)
    length = read_var_int(client_socket)
    print(f"Length: {length}")
    packet_id = read_var_int(client_socket)
    print(f"Packet ID: {packet_id}")

    if packet_id[0] == 0:
        # Assuming it's a handshake, read fields
        protocol_version = read_var_int(client_socket)
        print(f"Protocol version: {protocol_version}")
        server_address = read_string(client_socket)
        print(f"Server address: {server_address}")
        server_port = read_unsigned_short(client_socket)
        print(f"Server port: {server_port}")
        next_state = read_var_int(client_socket)
        print(f"Next state: {next_state}")
        leftover_int_1 = read_var_int(client_socket)

        # Reply with the server status
        send_server_status(client_socket, client_address)

        # Ping usually follows (length 1 packet id 0 no other info)
        print(f"Leftover int 1: {leftover_int_1}")
        leftover_int_2 = read_var_int(client_socket)
        print(f"Leftover int 2: {leftover_int_2}")

    else:
        # Unknown packet
        first_int = read_var_int(client_socket)
        print(f"First int: ", first_int)

    # Close the connection
    client_socket.shutdown(True)
    client_socket.close()


def send_server_status(client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
    """
    Send a server status packet
    @param client_socket:
    @param client_address:
    """
    message = '{"version":{"name":"1.20.2","protocol":751},"description":{"text":"Hello world"}}'
    message_enc = encode_string(message)
    send_packet(0, message_enc, client_socket)


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
