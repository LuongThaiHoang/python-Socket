# client_gui.py

import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import simpledialog
import queue

HOST = "127.0.0.1"
PORT = 12345

class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("Chat Room")

        # Hỏi nickname ngay khi khởi tạo
        self.nickname = simpledialog.askstring("Nickname", "Vui lòng nhập nickname của bạn:", parent=master)
        if not self.nickname:
            master.destroy()
            return
            
        master.title(f"Chat Room - {self.nickname}")

        # Vùng hiển thị tin nhắn
        self.message_area = scrolledtext.Text(master, state='disabled', wrap=tk.WORD, width=50, height=20)
        self.message_area.pack(padx=10, pady=10)

        # Khung chứa ô nhập liệu và nút gửi
        input_frame = tk.Frame(master)
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        # Ô nhập liệu
        self.input_entry = tk.Entry(input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.send_message) # Gửi bằng phím Enter

        # Nút gửi
        self.send_button = tk.Button(input_frame, text="Gửi", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Hàng đợi để giao tiếp giữa luồng mạng và luồng GUI
        self.message_queue = queue.Queue()

        # Kết nối tới server và bắt đầu các luồng
        self.connect_to_server()
        
        # Bắt sự kiện đóng cửa sổ
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))

            # Bắt đầu luồng nhận tin nhắn
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()

            # Bắt đầu kiểm tra hàng đợi tin nhắn
            self.master.after(100, self.process_queue)
        except ConnectionRefusedError:
            self.display_message("--- Lỗi: Không thể kết nối đến server. ---")
            self.input_entry.config(state='disabled')
            self.send_button.config(state='disabled')

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                # Đưa tin nhắn vào hàng đợi thay vì cập nhật UI trực tiếp
                self.message_queue.put(message)
            except (ConnectionResetError, ConnectionAbortedError):
                self.message_queue.put("--- Mất kết nối với server. ---")
                break
        self.client_socket.close()

    def process_queue(self):
        try:
            # Lấy tất cả tin nhắn từ hàng đợi
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                if message == "NICK":
                    self.client_socket.send(self.nickname.encode('utf-8'))
                elif "Nickname đã tồn tại" in message:
                    self.display_message(message)
                    self.client_socket.close()
                    self.master.destroy()
                    return # Dừng hẳn
                else:
                    self.display_message(message)
        finally:
            # Lên lịch để chạy lại hàm này sau 100ms
            self.master.after(100, self.process_queue)

    def send_message(self, event=None):
        message = self.input_entry.get()
        if message:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.input_entry.delete(0, tk.END) # Xóa nội dung ô nhập liệu sau khi gửi
                if message in ['{quit}', '{close}']:
                    self.client_socket.close()
                    self.master.destroy()
            except (ConnectionResetError, BrokenPipeError):
                self.display_message("--- Lỗi: Không thể gửi tin nhắn, kết nối đã mất. ---")

    def display_message(self, message):
        self.message_area.config(state='normal')
        self.message_area.insert(tk.END, message + '\n')
        self.message_area.config(state='disabled')
        self.message_area.see(tk.END) # Tự động cuộn xuống cuối

    def on_closing(self, event=None):
        # Gửi lệnh thoát trước khi đóng
        if self.client_socket:
            try:
                self.client_socket.send("{quit}".encode('utf-8'))
                self.client_socket.close()
            except:
                pass # Bỏ qua lỗi nếu socket đã đóng
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()