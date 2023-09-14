import random

command1 = b'\x00\x00\x00\x00'
command2 = b'\x00\x00\xBB\x00'
command3 = b'\xBB\x00\x00'
command4 = b'\x00\xBB\x00'
command5 = b'\x00\x00\xBB'
command6 = b'\x00\xAA'
command7 = b'\xBB\x00'
command8 = b'\x00'
command9 = b'\xBB'

commands = [command1,command2,command3,command4,command5,command6,command7,command8,command9]

quantidade = random.randint(10,30)

def sorteia_comandos():
    random_commands = []
    i = 1
    while i <= quantidade:
        sorteado = random.randint(0,8)
        random_commands.append(commands[sorteado])
        i+=1
    return random_commands

def constroi_mensagem(lista_comandos):
    mensagem = bytearray([])
    for command in lista_comandos:
        mensagem += command
    return mensagem    

def split_message(message):
    head = message[0:12]
    eop = message[-3:]
    message = message[12:]
    message = message[:-3]
    payload = message

    return head, payload, eop

comandos = sorteia_comandos()
message = constroi_mensagem(comandos)

print(message)

res = split_message(message)
# print(res[0])
# print(res[1])
# print(res[2])

# print(command1)
# for i in range(len(command1)):
#     print(i)

byte_array = bytearray([2,5,6])
print(byte_array)
byte_array[0:1] = int.to_bytes(99,1,'big')
byte_array[1:2] = int.to_bytes(98,1,'big')
print(byte_array)
print(int.to_bytes(2,1,'big'))
print(int.to_bytes(2,1,'little') + int.to_bytes(3,1,'big') + int.to_bytes(17,1,'big'))
print(int.to_bytes(4,1,'little') + int.to_bytes(5,1,'big') + int.to_bytes(50,1,'big'))