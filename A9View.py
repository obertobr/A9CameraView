import socket, pygame, io, threading, time

cont = 0
tempo = time.time()
resto = b""

IP = "192.168.169.1"
PORT = 6123

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

pygame.init()
display = pygame.display.set_mode((640, 480))
pygame.display.set_caption("View A9 Cam")

s.send(bytes.fromhex("0000000073000000000000000000000000000000"))

print(s.recv(20).hex())

s.send(bytes.fromhex("58000000000000003030303030303030000000007b22636f6465223a3530312c22746172676574223a22303830306330303146373345222c22746f6b656e223a2254686973206973205445535420746f6b656e222c22756e697854696d6572223a313637373630313034347d"))

print(s.recv(200).decode("utf-8"))

s.send(bytes.fromhex("53000000000000003030303030303030000000007b22636f6465223a3530322c22636f6e74656e74223a7b22636f6465223a342c22646576546172676574223a22303830306330303146373345222c22756e697854696d6572223a313637373630313034347d7d"))

print(s.recv(350).decode("utf-8"))

s.send(bytes.fromhex("3c000000000000003030303030303030000000007b22636f6465223a3530322c22636f6e74656e74223a7b22636f6465223a332c22646576546172676574223a22303830306330303146373345227d7d"))

print(s.recv(80).decode("utf-8"))

def corrigir(img):
    p = img.find(bytes.fromhex("2003000004"))
    if(p != -1):
        p2 = img[p:].find(bytes.fromhex("EC03000001"))
        if(p2 != -1):
            return corrigir(img[:p] + img[p+p2+20:])
    p = img.find(bytes.fromhex("EC03000001"))
    if(p != -1):
        return corrigir(img[:p] + img[p+20:])

    p = img.find(bytes.fromhex('000000010000'))
    if(p != -1):
        return corrigir(img[:p-1] + img[p+19:])
    p = img.find(bytes.fromhex('01000001'))
    if(p != -1):
        return corrigir(img[:p-1] + img[p+19:])
    p = img.find(bytes.fromhex('02000001'))
    if(p != -1):
        return corrigir(img[:p-1] + img[p+19:])
    p = img.find(bytes.fromhex('03000001'))
    if(p != -1):
        return corrigir(img[:p-1] + img[p+19:])
    return img

def exbir():
    arqfoto = pygame.image.load(io.BytesIO(corrigir(img)))
    display.blit(arqfoto, (0, 0))
    pygame.display.flip()

def fps():
    global tempo
    print("fps: ", round(1/(time.time() - tempo))," Numero de frames: ", cont)
    tempo = time.time()

while True:
    pygame.event.get()
    s.send(b"")
    texto = resto + s.recv(1400)
    if(texto.find(bytes.fromhex("FFD8FFE000104A464946")) != -1):
        img = texto[texto.find(bytes.fromhex("FFD8")):]
        while True:
            s.send(b"")
            texto = s.recv(1400)
            if(texto.find(bytes.fromhex("FFD9")) != -1):
                img += texto[:texto.find(bytes.fromhex("FFD9"))+2]
                resto = texto[(texto.find(bytes.fromhex('FFD9')))+2:]
                threading.Thread(target=exbir).start()
                threading.Thread(target=fps).start()
                cont += 1
                break
            img += texto