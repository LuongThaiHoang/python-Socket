# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 00:31:26 2025
@author: ADMIN - Gemini modified
"""

import socket
import threading
import sys

# Cấu hình client
HOST = "127.0.0.1"  # Địa chỉ server
PORT = 12345        # Cổng server

nickname = input("Nhập nickname của bạn: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
except ConnectionRefusedError:
    print("Không thể kết nối đến server. Vui lòng kiểm tra lại.")
    sys.exit()


# Nhận tin nhắn từ server
def receive():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message == "NICK":
                client.send(nickname.encode("utf-8"))
            elif "Nickname đã tồn tại" in message:
                print(message)
                client.close()
                break
            else:
                # Xóa dòng hiện tại, in tin nhắn và in lại prompt
                sys.stdout.write('\r' + ' ' * 60 + '\r') # Xóa dòng
                sys.stdout.write(message + '\n')
                sys.stdout.write('> ') # In lại prompt
                sys.stdout.flush()
        except:
            print("Mất kết nối với server!")
            client.close()
            break

# Gửi tin nhắn đến server
def write():
    while True:
        try:
            message = input('> ')
            if message.strip(): # Chỉ gửi nếu có nội dung
                client.send(message.encode("utf-8"))
                if message in ['{quit}', '{close}']:
                    client.close()
                    break
        except:
            break

# Chạy các luồng
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

# Chờ write_thread kết thúc (khi người dùng gõ lệnh thoát)
write_thread.join()
print("Đã ngắt kết nối.")