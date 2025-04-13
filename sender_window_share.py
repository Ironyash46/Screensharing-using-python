import socket
import threading
import time
import mss
from PIL import Image
from io import BytesIO
import tkinter as tk
import Quartz
import AppKit
import numpy as np
from tkinter import ttk

# ------------ FULL SCREEN CAPTURE ------------
def capture_full_screen(ip, port=9999):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary screen
            print(f"📺 Sharing full screen: {monitor['width']}x{monitor['height']}")

            while True:
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

                buffer = BytesIO()
                img.save(buffer, format='PNG')
                img_bytes = buffer.getvalue()
                buffer.close()

                size = len(img_bytes).to_bytes(4, byteorder='little')
                try:
                    sock.sendall(size + img_bytes)
                    time.sleep(0.05)
                except Exception as e:
                    print("...Disconnected...")
                    break

# ------------ APP WINDOW CAPTURE (macOS) ------------
def get_window_image(app_name):
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    for win in window_list:
        owner_name = win.get('kCGWindowOwnerName', '')
        if app_name.lower() in owner_name.lower():
            window_id = win['kCGWindowNumber']
            bounds = win['kCGWindowBounds']
            img = Quartz.CGWindowListCreateImage(
                Quartz.CGRectMake(bounds['X'], bounds['Y'], bounds['Width'], bounds['Height']),
                Quartz.kCGWindowListOptionIncludingWindow,
                window_id,
                Quartz.kCGWindowImageDefault
            )
            if img:
                width = Quartz.CGImageGetWidth(img)
                height = Quartz.CGImageGetHeight(img)
                bytes_per_row = Quartz.CGImageGetBytesPerRow(img)
                data_provider = Quartz.CGImageGetDataProvider(img)
                data = Quartz.CGDataProviderCopyData(data_provider)
                arr = np.frombuffer(data, dtype=np.uint8).reshape((height, bytes_per_row // 4, 4))
                return Image.fromarray(arr[:, :width, :3], 'RGB')
    return None

def capture_app_window(ip, app_name, port=9999):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((ip, port))
        except Exception as e:
            print(f"Connection failed: {e}")
            return

        print(f"🪟 Sharing window: {app_name}")
        while True:
            img = get_window_image(app_name)
            if img is None:
                print("⚠️ App not found or minimized!")
                time.sleep(1)
                continue

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()
            buffer.close()

            size = len(img_bytes).to_bytes(4, byteorder='little')
            try:
                sock.sendall(size + img_bytes)
                time.sleep(0.05)
            except Exception as e:
                print("...Disconnected...")
                break

# ------------ GET ACTIVE APP NAMES ------------
def get_active_app_names():
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
    app_names = set()
    for win in window_list:
        name = win.get('kCGWindowOwnerName', '')
        if name:
            app_names.add(name)
    return sorted(app_names)

# ------------ GUI SELECTOR ------------
def show_gui():
    root = tk.Tk()
    root.title("Screen Share Options")
    root.geometry("460x300")

    tk.Label(root, text="Enter IP address (IP of the machine ur streaming to da shadee):").place(x=30, y=15)
    ip_entry = tk.Entry(root, width=45)
    ip_entry.place(x=30, y=40)

    mode = tk.StringVar(value="full")
    tk.Radiobutton(root, text="Share Entire Screen", variable=mode, value="full", command=lambda: toggle_app_input()).place(x=30, y=80)
    tk.Radiobutton(root, text="Share Specific App Window", variable=mode, value="window", command=lambda: toggle_app_input()).place(x=30, y=110)

    app_label = tk.Label(root, text="Select app to share:")
    app_combobox = ttk.Combobox(root, width=42, state='readonly')
    app_combobox['values'] = get_active_app_names()

    def toggle_app_input():
        if mode.get() == "window":
            app_label.place(x=30, y=160)
            app_combobox.place(x=30, y=185)
        else:
            app_label.place_forget()
            app_combobox.place_forget()

    def submit():
        selected_mode = mode.get()
        ip = ip_entry.get().strip()
        app_name = app_combobox.get().strip()
        root.quit()
        root.destroy()
        if selected_mode == "full":
            threading.Thread(target=capture_full_screen, args=(ip,)).start()
        else:
            threading.Thread(target=capture_app_window, args=(ip, app_name)).start()

    tk.Button(root, text="Start Sharing", command=submit).place(x=180, y=240)

    root.mainloop()

# ------------ RUN ------------
if __name__ == "__main__":
    show_gui()
