import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, Entry, Button, Label, Frame
from crypto_utils import encrypt_message, decrypt_message
import base64

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuantumChat Client (Nikhil)")
        self.root.geometry("460x680")
        self.root.configure(bg="#0f172a") # Slate 900
        
        self.key = None
        self.client = None
        self.running = True

        # Custom Styling Palette
        self.bg_color = "#0f172a"
        self.card_color = "#1e293b" # Slate 800
        self.accent_color = "#3b82f6" # Blue 500
        self.accent_hover = "#2563eb" # Blue 600
        self.text_color = "#f8fafc"
        self.entry_bg = "#334155"
        self.font_main = ("Segoe UI", 10)
        self.font_bold = ("Segoe UI", 10, "bold")

        # Main Container Frame
        container = Frame(root, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Connection Configuration Frame
        config_frame = Frame(container, bg=self.card_color, padx=12, pady=12)
        config_frame.pack(fill=tk.X, pady=(0, 10))

        Label(config_frame, text="Server IP:", bg=self.card_color, fg=self.text_color, font=self.font_main).grid(row=0, column=0, sticky="w", pady=2)
        self.ip_entry = Entry(config_frame, width=22, bg=self.entry_bg, fg=self.text_color, insertbackground="white", relief="flat", font=self.font_main)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=2)
        self.ip_entry.insert(0, "127.0.0.1")

        Label(config_frame, text="Port:", bg=self.card_color, fg=self.text_color, font=self.font_main).grid(row=1, column=0, sticky="w", pady=2)
        self.port_entry = Entry(config_frame, width=22, bg=self.entry_bg, fg=self.text_color, insertbackground="white", relief="flat", font=self.font_main)
        self.port_entry.grid(row=1, column=1, padx=5, pady=2)

        self.connect_button = Button(config_frame, text="Connect", command=self.connect_thread, 
                                     bg=self.accent_color, fg="white", activebackground=self.accent_hover, 
                                     activeforeground="white", relief="flat", font=self.font_bold, cursor="hand2", padx=10)
        self.connect_button.grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky="ns")

        # Chat History Frame
        chat_frame = Frame(container, bg=self.card_color, padx=5, pady=5)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.chat_box = scrolledtext.ScrolledText(chat_frame, width=48, height=18, bg=self.entry_bg, fg=self.text_color, 
                                                  insertbackground="white", relief="flat", font=self.font_main)
        self.chat_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_box.config(state=tk.NORMAL)

        # Message Input Frame
        input_frame = Frame(container, bg=self.bg_color)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.entry = Entry(input_frame, width=32, bg=self.entry_bg, fg=self.text_color, insertbackground="white", relief="flat", font=("Segoe UI", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = Button(input_frame, text="Send", command=self.send_message, 
                                  bg=self.accent_color, fg="white", activebackground=self.accent_hover, 
                                  activeforeground="white", relief="flat", font=self.font_bold, cursor="hand2", padx=15)
        self.send_button.pack(side=tk.RIGHT, ipady=2)

        # Bottom Control Panel
        control_frame = Frame(container, bg=self.bg_color)
        control_frame.pack(fill=tk.X)

        self.end_button = Button(control_frame, text="End Session", command=self.end_session, 
                                 bg="#ef4444", fg="white", activebackground="#dc2626", 
                                 activeforeground="white", relief="flat", font=self.font_bold, cursor="hand2")
        self.end_button.pack(side=tk.LEFT, ipadx=10, ipady=2)

        self.status_label = Label(control_frame, text="Status: Not Connected", bg=self.bg_color, fg="#94a3b8", font=("Segoe UI", 9, "italic"))
        self.status_label.pack(side=tk.RIGHT, pady=2)

    def connect_thread(self):
        threading.Thread(target=self.connect_to_server, daemon=True).start()

    def recvall(self, sock, n):
        """Helper to receive exact number of bytes for the key"""
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    def connect_to_server(self):
        try:
            ip = self.ip_entry.get()
            port = int(self.port_entry.get())

            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((ip, port))

            # Safely receive exact 32-byte key
            self.key = self.recvall(self.client, 32)
            if not self.key or len(self.key) != 32:
                raise Exception("Failed to receive valid cryptographic key.")

            self.chat_box.insert(tk.END, "Connected to Lalit\n")
            self.chat_box.see(tk.END)
            self.status_label.config(text="Status: Connected", fg="#22c55e")

            # Use socket file stream for reliable line-by-line reading
            rfile = self.client.makefile('r', encoding='utf-8')

            while self.running:
                line = rfile.readline()
                if not line:
                    break

                encrypted_data = base64.b64decode(line.strip())
                msg = decrypt_message(encrypted_data, self.key)

                if msg == "SESSION_OVER":
                    self.chat_box.insert(tk.END, "Lalit ended the session\n")
                    self.chat_box.see(tk.END)
                    self.running = False
                    self.status_label.config(text="Status: Session Ended", fg="#ef4444")
                    self.send_button.config(state=tk.DISABLED)
                    self.entry.config(state=tk.DISABLED)
                    self.end_button.config(state=tk.DISABLED)
                    break

                self.chat_box.insert(tk.END, f"Lalit: {msg}\n")
                self.chat_box.see(tk.END)

        except Exception as e:
            self.chat_box.insert(tk.END, f"Connection Error: {e}\n")

    def send_message(self):
        if self.client and self.running:
            msg = self.entry.get()
            if msg:
                encrypted = encrypt_message(msg, self.key)
                encoded = base64.b64encode(encrypted).decode('utf-8') + '\n'
                self.client.sendall(encoded.encode('utf-8'))
                self.chat_box.insert(tk.END, f"Me: {msg}\n")
                self.chat_box.see(tk.END)
                self.entry.delete(0, tk.END)

    def end_session(self):
        if self.client and self.running:
            try:
                encrypted = encrypt_message("SESSION_OVER", self.key)
                encoded = base64.b64encode(encrypted).decode('utf-8') + '\n'
                self.client.sendall(encoded.encode('utf-8'))
            except:
                pass

            self.running = False
            try:
                self.client.close()
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
