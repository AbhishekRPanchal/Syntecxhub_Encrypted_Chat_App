import socket
import threading
import tkinter as tk
from tkinter import ttk
from crypto_utils import encrypt_message, decrypt_message

HOST = '127.0.0.1'
PORT = 5555


class ChatClientGUI:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((HOST, PORT))

        self.root = tk.Tk()
        self.root.title("🔐 Encrypted Chat App")
        self.root.geometry("520x600")
        self.root.configure(bg="#f4f6f9")
        self.root.resizable(False, False)

        self.build_header()
        self.build_chat_area()
        self.build_input_area()

        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.root.mainloop()

    # ---------- HEADER ----------
    def build_header(self):
        header = tk.Frame(self.root, bg="#1f2933", height=60)
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="Encrypted Chat Application",
            bg="#1f2933",
            fg="white",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=10)

        status = tk.Label(
            header,
            text="● Connected",
            bg="#1f2933",
            fg="#22c55e",
            font=("Segoe UI", 10)
        )
        status.place(x=420, y=38)

    # ---------- CHAT AREA ----------
    def build_chat_area(self):
        chat_frame = tk.Frame(self.root, bg="#f4f6f9")
        chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.chat_area = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="white",
            fg="#111827",
            state=tk.DISABLED
        )
        self.chat_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(chat_frame, command=self.chat_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_area.config(yscrollcommand=scrollbar.set)

        # Message tags (bubble effect)
        self.chat_area.tag_config(
            "sent",
            foreground="white",
            background="#22c55e",
            spacing3=8,
            lmargin1=200,
            lmargin2=200
        )
        self.chat_area.tag_config(
            "received",
            foreground="white",
            background="#3b82f6",
            spacing3=8,
            lmargin1=10,
            lmargin2=10
        )

    # ---------- INPUT AREA ----------
    def build_input_area(self):
        input_frame = tk.Frame(self.root, bg="#e5e7eb", height=60)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.msg_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            width=32
        )
        self.msg_entry.pack(side=tk.LEFT, padx=10, pady=10)
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        send_btn = tk.Button(
            input_frame,
            text="Send",
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            relief=tk.FLAT,
            width=10,
            command=self.send_message
        )
        send_btn.pack(side=tk.RIGHT, padx=10)

    # ---------- SEND MESSAGE ----------
    def send_message(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return

        enc = encrypt_message(msg)
        enc_bytes = enc.encode()

        packet = len(enc_bytes).to_bytes(4, 'big') + enc_bytes
        self.client.sendall(packet)

        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"You: {msg}\n", "sent")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

        self.msg_entry.delete(0, tk.END)

    # ---------- RECEIVE MESSAGE ----------
    def receive_messages(self):
        while True:
            try:
                length = int.from_bytes(self.client.recv(4), 'big')
                enc_msg = self.client.recv(length).decode()
                msg = decrypt_message(enc_msg)

                self.chat_area.config(state=tk.NORMAL)
                self.chat_area.insert(tk.END, f"Friend: {msg}\n", "received")
                self.chat_area.config(state=tk.DISABLED)
                self.chat_area.see(tk.END)

            except:
                break


if __name__ == "__main__":
    ChatClientGUI()
