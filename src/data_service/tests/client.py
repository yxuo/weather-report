import socket


def send_shutdown_signal():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5784))
    valid_data = 'joao,joao@nimbusmeteorologia.com.br,01234567891,31'
    client_socket.sendall(valid_data.encode())
    response = client_socket.recv(1024)
    print("Server response:", response.decode("utf-8"))
    client_socket.close()


if __name__ == "__main__":
    send_shutdown_signal()
