import socket
import types
import selectors
sel = selectors.DefaultSelector()

host = "localhost"
port = 4444
flag = "LGVSDCV{hello_from_the_other_side}"
magic_word = "lgvsdcvdn\n"

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    def request_handler(data):
        # Answer if request data is a particular string
        if data.outb == bytes(magic_word, "utf-8"):
            print('send flag to', data.addr)
            sent = sock.send(bytes(flag, "utf-8"))  # Should be ready to write
            data.outb = data.outb[sent:]
            sel.unregister(sock)
            sock.close()
        else:
            sent = sock.send(b"You say " + data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            request_handler(data)


if __name__ == "__main__":
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen()
    print('listening on', (host, port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)


