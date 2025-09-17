# -*- coding: utf-8 -*-
# server_b1_fixed.py
import socket
import threading

HOST = '127.0.0.1'
PORT = 5055

clients = {}          # dict: conn -> name
clients_lock = threading.Lock()

def send_line(conn, text: str):
    try:
        conn.sendall((text + '\n').encode('utf-8'))
    except OSError:
        pass

def broadcast(text: str, except_conn=None):
    """Gửi message tới tất cả client (trừ except_conn). Không giữ lock khi send."""
    data = (text + '\n').encode('utf-8')
    # chụp danh sách dưới lock
    with clients_lock:
        targets = [c for c in clients.keys() if c is not except_conn]

    dead = []
    for c in targets:
        try:
            c.sendall(data)
        except OSError:
            dead.append(c)

    # dọn các kết nối chết
    if dead:
        with clients_lock:
            for d in dead:
                clients.pop(d, None)

def handle_client(conn: socket.socket, addr):
    name = f'guest-{addr[1]}'
    buf = b''

    with conn:
        with clients_lock:
            clients[conn] = name
        print(f'[+] {addr} connected as {name}')
        broadcast(f'* {name} đã tham gia phòng *')
        send_line(conn, 'Chào mừng tới phòng chat!')
        send_line(conn, 'Gõ: /name <ten> để đổi tên, /list để xem danh sách.')
        send_line(conn, 'Nhập {quit} hoặc {close} để thoát.')

        try:
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buf += chunk

                while b'\n' in buf:
                    line, buf = buf.split(b'\n', 1)
                    msg = line.decode('utf-8', errors='replace').strip()
                    if not msg:
                        continue

                    # LOG mỗi khi server nhận được tin
                    print(f'[MSG] {name}: {msg}')

                    # Thoát
                    if msg in ('{quit}', '{close}'):
                        send_line(conn, 'Tạm biệt!')
                        return

                    # Đổi tên: /name <ten>
                    if msg.startswith('/name '):
                        new_name = msg[6:].strip()
                        if not new_name:
                            send_line(conn, 'Usage: /name <ten>')
                            continue
                        with clients_lock:
                            if new_name in clients.values():
                                send_line(conn, f'Tên "{new_name}" đã tồn tại. Chọn tên khác.')
                                continue
                            old = name
                            name = new_name
                            clients[conn] = name
                        broadcast(f'* {old} đổi tên thành {name} *')
                        continue

                    # Danh sách
                    if msg == '/list':
                        with clients_lock:
                            names = ', '.join(sorted(clients.values()))
                        send_line(conn, f'Đang online: {names}')
                        continue

                    # Tin thường -> broadcast
                    broadcast(f'[{name}] {msg}')
        finally:
            with clients_lock:
                left_name = clients.pop(conn, name)
            broadcast(f'* {left_name} đã rời phòng *')
            print(f'[-] {addr} closed')

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(50)
        print(f'Chat Room Server (Bài 1) đang nghe tại {HOST}:{PORT}')
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    main()
