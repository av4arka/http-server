import socket
import sys
import threading
import os
import select
import signal
import configparser
import datetime
import magic
from time import gmtime, strftime
from numpy.core.defchararray import rstrip


class HttpServer:

    def __init__(self):
        config = create_config()

        self._address = config.get('Settings', 'address')
        self._port = int(config.get('Settings', 'port'))
        self._root_dir = config.get('Settings', 'root_dir')
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self._sock.bind((self._address, self._port))
        self._sock.listen(5)
        threading.Thread(target=self.listen_to_client).start()

    def listen_to_client(self):
        input = [self._sock, ]

        while True:
            input_ready, output_ready, exept_ready = select.select(input, [], [])

            for client in input_ready:
                try:
                    if client == self._sock:
                        conn, addr = self._sock.accept()
                        input.append(conn)
                        print(f'user - {addr} connected')
                    else:
                        self.handle_client(client)
                except (ConnectionResetError, UnicodeDecodeError, Exception):
                    print(f'user - {addr} disconnected')
                    client.close()
                    input.remove(client)

    def handle_client(self, client):
        status_code = '200 OK'
        path_to_file = ''
        message_body = b''
        request = client.recv(1024).decode('utf-8').split(' ')
        method = request[0]
        file_requested = request[1]
        http_version = str(rstrip(request[2]))

        client.send(b'Host: localhost\n')
        if method == 'GET':
            if file_requested == '/' or file_requested[-1] == '/':
                file_requested += 'index.html'
            path_to_file = self._root_dir + file_requested
            try:
                file = open(path_to_file, 'rb')
                message_body = file.read()
                file.close()
            except Exception:
                status_code = '404 Not Found'
        else:
            status_code = '405 Method Not Allowed'

        headers = self.get_headers(path_to_file)
        response = f'{http_version} {status_code}\nConnection: {headers["Connection"]}\nContent-Length: {headers["Content-Length"]}\n' \
                   f'Content-Type: {headers["Content-Type"]}\nDate: {headers["Date"]}\n\n'

        if http_version == 'HTTP/0.9' or http_version == 'HTTP/1.0':
            if http_version == 'HTTP/1.0':
                client.send(response.encode('utf-8'))
                print(f'{status_code.split(" ")[0]} {file_requested}')
            client.send(message_body)
            raise ConnectionResetError()
        elif http_version == 'HTTP/1.1':
            client.send(response.encode('utf-8'))
            client.send(message_body)
        else:
            raise Exception

        if status_code == '404 Not Found':
            file_requested = '/some-strange-url.notfound'
        print(f'{status_code.split(" ")[0]} {file_requested}')

    def get_headers(self, path):
        connection = 'close'
        date = f'{datetime.datetime.strftime(datetime.datetime.today(), "%a, %d %b %Y %H:%M:%S ")}' \
               f'{strftime("%Z", gmtime())}'
        mime = magic.Magic(mime=True)
        try:
            content_length = os.path.getsize(path)
            content_type = mime.from_file(path)
        except FileNotFoundError:
            content_type = 'application/octet-stream'
            content_length = 0

        return {'Connection': connection, 'Content-Length': content_length,
                'Content-Type': content_type, 'Date': date}

    def server_stop(self):
        open('http.conf', 'w').close()
        self._sock.close()

def create_config():
    file_config = 'http.conf'
    path = f'{os.getcwd()}/server_files/'
    config = configparser.ConfigParser()
    config.add_section('Settings')
    config.set('Settings', 'address', '127.0.0.1')
    config.set('Settings', 'port', '8081')
    config.set('Settings', 'root_dir', path)

    with open(file_config, 'w') as config_file:
        config.write(config_file)
    return config

def shutdown(sig, unused):
    server.server_stop()
    sys.exit('Server stoped')

if __name__ == '__main__':
    signal.signal(signal.SIGINT, shutdown)
    server = HttpServer()
    server.start()
    print(f'Server started with port {create_config().get("Settings", "port")}')
    print('Press ctrl+c to stop the server')
