import socket
import threading
from crypto_utils import decrypt_message
from datetime import datetime

HOST = '127.0.0.1'
PORT = 5555

clients = []
lock = threading.Lock()


def broadcast(packet, sender):
    with lock:
        for client in clients:
            if client != sender:
                client.sendall(packet)


def handle_client(client, address):
    print(f"[CONNECTED] {address}")

    with open("chat_log.txt", "a", encoding="utf-8") as log:
        while True:
            try:
                # Receive message length
                length_bytes = client.recv(4)
                if not length_bytes:
                    break

                length = int.from_bytes(length_bytes, 'big')

                # Receive encrypted message
                enc_msg = client.recv(length).decode()

                # Decrypt
                msg = decrypt_message(enc_msg)

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Log to file
                log.write(f"[{timestamp}] {address}: {msg}\n")
                log.flush()

                print(f"{address}: {msg}")

                # Re-broadcast same encrypted packet
                packet = length_bytes + enc_msg.encode()
                broadcast(packet, client)

            except:
                break

    with lock:
        clients.remove(client)

    client.close()
    print(f"[DISCONNECTED] {address}")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("[SERVER STARTED]")

    try:
        while True:
            client, addr = server.accept()
            with lock:
                clients.append(client)
            threading.Thread(
                target=handle_client,
                args=(client, addr),
                daemon=True
            ).start()

    except KeyboardInterrupt:
        print("\n[SERVER STOPPED]")
        server.close()


if __name__ == "__main__":
    start_server()
