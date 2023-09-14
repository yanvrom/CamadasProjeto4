#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
import random
import datetime

EOP = b"\xfb\xfb\xfb"

MENSAGEM_SUCESSO = b'\x00\x00\00\00\00\00\00\00\00\00\00\00' + EOP

MENSAGEM_HANDSHAKE = b'\x00\x00\00\00\00\00\00\00\00\00\00\01' + EOP

MENSAGEM_ERRO = b'\00\00\00\00\00\00\00\00\00\00\00\02' + EOP

MENSAGEM_ENCERRADA = b'\00\00\00\00\00\00\00\00\00\00\00\03' + EOP

MENSAGEM_VOLTA = b'\00\00\00\00\00\00\00\00\00\00\00\04' + EOP

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

quantidade = random.randint(50,70)

def sorteia_comandos():
    random_commands = []
    i = 1
    while i <= quantidade:
        sorteado = random.randint(0,8)
        random_commands.append(commands[sorteado])
        i+=1
    return random_commands

def constroi_mensagem(informacao):
    mensagem = bytearray([])
    for command in informacao:
        mensagem += command
        mensagem += b'\xFB'
    return mensagem    

def constroi_head(posicao, total_pacotes, tamanho_payload, handshake):
    if not (0 <= posicao <= 255 and 0 <= total_pacotes <= 255 and 0 <= tamanho_payload <= 255 and 0 <= handshake <= 255):
        raise ValueError("Os valores devem estar no intervalo de 0 a 255.")
    print(f'posicao {posicao} totalpacotes {total_pacotes} tamanho payload: {tamanho_payload}')
    byte_array = bytearray()
    byte_array += int.to_bytes(posicao,1,byteorder='little')
    byte_array += int.to_bytes(total_pacotes,1, byteorder='little')
    byte_array += int.to_bytes(tamanho_payload, 1, byteorder='little')
    
    byte_array += bytearray([0]*8)
    
    byte_array += int.to_bytes(handshake,1, byteorder='little')

    return byte_array



def constroi_datagramas(lista_payloads):
    datagramas = []
    posicao = 1
    total_pacotes = len(lista_payloads)
    for payload in lista_payloads:
        tamanho_payload = len(payload)
        head = constroi_head(posicao, total_pacotes, tamanho_payload, 0)
        datagrama = head + payload
        datagrama = datagrama + EOP
        
        datagramas.append(datagrama)
        posicao += 1
    return datagramas
        
    
def constroi_pacotes(mensagem):
    print(type(mensagem))
    pacotes = []
    i = 0
    while i < len(mensagem):
        pacote = bytearray([])
        while len(pacote) < 50 and i < len(mensagem):
            pacote.append(mensagem[i])
            i += 1
        pacotes.append(pacote)
    return pacotes

def split_message(message):
    head = message[0:12]
    eop = message[-3:]
    message = message[12:]
    message = message[:-3]
    payload = message

    return head, payload, eop

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM7"                  # Windows(variacao de)


def main():
    try:
        
        print("Iniciou o main")
        

        com1 = enlace(serialName)
        com1.enable()
        time.sleep(.2)
        com1.sendData(b'00')
        time.sleep(1)
        
        print("Abriu a comunicação")

        #imageR = "kakakakaka.jpeg"
        imageR = "testes.jpeg"
        imagemBytes = open(imageR, 'rb').read()
        pacotes = constroi_pacotes(imagemBytes)
        datagramas = constroi_datagramas(pacotes)

        # print("Sorteando comandos e construíndo mensagens")
        # comandos = sorteia_comandos()
        # print(f"Serão enviados {len(comandos)} comandos")
        # print(comandos)
        # conteudo = constroi_mensagem(comandos)
        # lista = constroi_pacotes(conteudo)
        # #print(lista)
        # datagramas = constroi_datagramas(lista)

        handshake = False
        mensagem_hs = bytearray()

        tempo_handshake = datetime.datetime.now()
        
        com1.sendData(MENSAGEM_HANDSHAKE)
        while com1.tx.getIsBussy():
            pass
        
        while not handshake:
            
            if (datetime.datetime.now() - tempo_handshake > datetime.timedelta(seconds=5)):
                print("Reenviando HANDSHAKE, NÃO HOUVE RESPOSTA")
                com1.sendData(MENSAGEM_HANDSHAKE)
                while com1.tx.getIsBussy():
                    pass
                tempo_handshake = datetime.datetime.now()
            
            
            if com1.rx.getBufferLen() > 0:
                rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
                mensagem_hs += rxBuffer

                if com1.rx.getBufferLen() == 0:
                    head, payload, eop = split_message(mensagem_hs)
                    
                    if eop != b'\xfb\xfb\xfb':
                        print("Erro no EOP!")
                        break
                
                    if len(payload) != int(head[2]):
                        print("Tamanho do payload não condiz com o head!")
                        break
                    print(mensagem_hs)
                    if mensagem_hs == MENSAGEM_HANDSHAKE:
                        handshake = True
                        print("HANDSHAKE FEITO COM SUCESSO")
                    
                        
                        
    
    
        tempo_inicio = datetime.datetime.now()
        pacote_number = 1
        i = 0
        flag_erro = True
        while i < len(datagramas):
            datagrama = datagramas[i]
            mensagem = bytearray()
            
            # SIMULAÇÃO DE ERRO 
            if i == 2 and flag_erro:
                #datagrama = datagrama[:-1]  #OPÇÃO 1
                datagrama = int.to_bytes(4, 1, 'little') + datagrama[1:] # OPÇÃO 2, erro no número do pacote
                #datagrama = datagrama[0:1] + datagrama[1:2] + int.to_bytes(51, 1, 'little') + datagrama[3:] #OPÇÃO 3, tamanho do payload errado
                flag_erro = False
            
            print(datagrama)
            recebeu_pacote = False
            
            txBuffer = datagrama
            
            com1.sendData(np.asarray(txBuffer))
            while com1.tx.getIsBussy():
                pass
            
            while not recebeu_pacote:
                if (datetime.datetime.now() - tempo_inicio > datetime.timedelta(seconds=5)):
                    print("Servidor não deu resposta há 5 segundos")
                    tempo_inicio = datetime.datetime.now()
                    print("Esperando...")
                    
                
                if com1.rx.getBufferLen() > 0:
                    recebeu_pacote = True
                    rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
                    mensagem += rxBuffer
                    if mensagem == MENSAGEM_SUCESSO:
                        print(f"Pacote {pacote_number} recebido pelo cliente")
                        pacote_number += 1
                        i += 1
                        tempo_inicio = datetime.datetime.now()
                    elif mensagem == MENSAGEM_ENCERRADA:
                        print(f"Pacote {pacote_number} recebido pelo cliente")
                        print("Finalizando...")
                        i += 1
                        tempo_inicio = datetime.datetime.now()
                    elif mensagem_hs == MENSAGEM_VOLTA:
                        i -= 1
                        pacote_number -= 1
                        print("PASSEI DO PROBLEMA")
                    else:
                        print("Erro na mensagem de confirmação de recebimento do pacote.")
                        print(mensagem)
        
        
        #as array apenas como boa pratica para casos de ter uma outra forma de dados
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        while com1.tx.getIsBussy():
            pass
            
            #print(mensagem)

            
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
