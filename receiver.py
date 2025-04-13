import socket
import threading
from PIL import Image, ImageTk
import tkinter as tk
from io import BytesIO

class ScreenViewer:
    def on_click(self):
        self.root.quit()
    def __init__(self, host='0.0.0.0', port=9999):
        self.root = tk.Tk()
        self.root.title("Live Screen")

        self.width = 1280
        self.height = 720

        self.label = tk.Label(self.root)
        self.label.pack()

        self.button = tk.Button(self.root, text="Stop Sharing", command=self.on_click)
        self.button.pack(side=tk.BOTTOM)

        self.image_tk = None  # Keep a reference to prevent garbage collection

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(1)
        print("Waiting for sender to connect...")
        self.conn, _ = self.server.accept()
        print("Sender connected!")

    def receive_loop(self):
        try:
            while True:
                size_data = self.conn.recv(4)
                if not size_data:
                    break
                size = int.from_bytes(size_data, byteorder='little')
                data = b''
                while len(data) < size:
                    more = self.conn.recv(size - len(data))
                    if not more:
                        break
                    data += more
                if data:
                    img = Image.open(BytesIO(data)).convert("RGB")
                    img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)

                    self.image_tk = ImageTk.PhotoImage(img)
                    self.label.config(image=self.image_tk)
        except Exception as e:
            print("Disconnected:", e)

    def start(self):
        threading.Thread(target=self.receive_loop, daemon=True).start()
        self.root.mainloop()

viewer = ScreenViewer()
viewer.start()

