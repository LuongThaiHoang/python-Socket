# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 00:30:00 2025
@author: ADMIN - Gemini modified
"""

import socket
import threading

# Cấu hình server
HOST = "127.0.0.1"  # Địa chỉ localhost
PORT = 12345        # Cổng để giao tiếp

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

# Gửi tin nhắn đến tất cả client, trừ người gửi
def broadcast(message, sender_client=None):
    for client in clients:
        if client != sender_client:
            try:
                client.send(message)
            except:
                # Nếu gửi lỗi, xóa client này đi
                remove_client(client)

# Xóa client khỏi danh sách khi họ thoát
def remove_client(client):
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        nickname = nicknames[index]
        nicknames.remove(nickname)
        broadcast(f"--- {nickname} đã rời khỏi phòng chat! ---".encode("utf-8"))
        print(f"{nickname} đã ngắt kết nối.")

# Xử lý tin nhắn từ một client
def handle(client):
    while True:
        try:
            message_str = client.recv(1024).decode('utf-8')
            
            # Xử lý lệnh thoát
            if message_str in ['{quit}', '{close}']:
                remove_client(client)
                client.close()
                break
            
            # Lấy nickname của người gửi
            index = clients.index(client)
            nickname = nicknames[index]
            
            # Định dạng và quảng bá tin nhắn
            formatted_message = f"[{nickname}]: {message_str}".encode('utf-8')
            broadcast(formatted_message, client)

        except:
            # Xử lý khi client ngắt kết nối đột ngột
            remove_client(client)
            client.close()
            break

# Chấp nhận kết nối từ các client mới
def receive():
    print(f"Server đang lắng nghe trên {HOST}:{PORT}...")
    while True:
        client, address = server.accept()
        print(f"Kết nối mới từ {str(address)}")

        client.send("NICK".encode("utf-8"))
        nickname = client.recv(1024).decode("utf-8")

        # Kiểm tra nickname có bị trùng không
        if nickname in nicknames:
            client.send("--- Nickname đã tồn tại. Vui lòng kết nối lại với tên khác. ---".encode("utf-8"))
            client.close()
            continue

        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname của client là {nickname}")
        broadcast(f"--- {nickname} đã tham gia phòng chat! ---".encode("utf-8"))
        client.send("--- Chào mừng đến với phòng chat! ---".encode("utf-8"))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()