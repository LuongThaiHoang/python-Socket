# -*- coding: utf-8 -*-
# client_b1_fixed.py
import socket
import threading
import time

HOST = '127.0.0.1'
PORT = 5055

def now():
    return time.strftime('%H:%M:%S')

def receiver(sock: socket.socket):
    """Nhận dữ liệu liên tục, tách theo dòng và in ra."""
    buf = b''
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                print('\n[Server đã đóng kết nối]')
                break
            buf += data
            while b'\n' in buf:
                line, buf = buf.split(b'\n', 1)
                text = line.decode('utf-8', errors='replace')
                print(f'\r{text}\n> ', end='', flush=True)
    except OSError:
        pass

def main():
    name = input('Nhập chatname của bạn: ').strip() or 'me'

    try:
        s = socket.create_connection((HOST, PORT), timeout=5)
    except (ConnectionRefusedError, TimeoutError) as e:
        print(f'Không kết nối được tới server tại {HOST}:{PORT} ({e}). '
              f'Bạn đã chạy server chưa?')
        return

    with s:
        print(f'[{now()}] Đã kết nối tới {HOST}:{PORT}')
        s.sendall(f'/name {name}\n'.encode('utf-8'))

        threading.Thread(target=receiver, args=(s,), daemon=True).start()

        print('Hướng dẫn: gõ tin nhắn rồi Enter để gửi.')
        print('Lệnh: /name <ten>, /list, {quit} hoặc {close} để thoát.')
        try:
            while True:
                msg = input('> ')
                if not msg:
                    continue
                s.sendall((msg + '\n').encode('utf-8'))
                if msg in ('{quit}', '{close}'):
                    break
        except (KeyboardInterrupt, EOFError):
            try:
                s.sendall(b'{quit}\n')
            except OSError:
                pass

if __name__ == '__main__':
    main()
