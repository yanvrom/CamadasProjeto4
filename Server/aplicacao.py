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
import datetime

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM5"                  # Windows(variacao de)

imageW = 'copia.png'

EOP = b'\xfb\xfb\xfb'

MENSAGEM_SUCESSO = b'\00\00\00\00\00\00\00\00\00\00\00\00' + EOP
MENSAGEM_HANDSHAKE = b'\00\00\00\00\00\00\00\00\00\00\00\01' + EOP
MENSAGEM_ERRO = b'\00\00\00\00\00\00\00\00\00\00\00\02' + EOP
MENSAGEM_ENCERRADA = b'\00\00\00\00\00\00\00\00\00\00\00\03' + EOP
MENSAGEM_VOLTA = b'\00\00\00\00\00\00\00\00\00\00\00\04' + EOP

def split_message(message):
    head = message[0:12]
    eop = message[-3:]
    message = message[12:]
    message = message[:-3]
    payload = message

    return head, payload, eop

def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        print("esperando 1 byte de sacrifício")

        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(.1)

        handshake = False
        mensagem_hs = bytearray()

        while not handshake:
            if com1.rx.getBufferLen() > 0:
                rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
                mensagem_hs += rxBuffer

                if com1.rx.getBufferLen() == 0:
                    print(mensagem_hs)
                    head, payload, eop = split_message(mensagem_hs)
                    print(head)
                    
                    if eop != b'\xfb\xfb\xfb':
                        print("Erro no EOP!")
                        break
                
                    if len(payload) != int(head[2]):
                        print(len(payload))
                        print(int(head[2]))
                        print("Tamanho do payload não condiz com o head!")
                        break
                    
                    if mensagem_hs == MENSAGEM_HANDSHAKE:
                        handshake = True
                        com1.sendData(MENSAGEM_HANDSHAKE)
                        print('enviei handshake')

        print("Handshake feito!")

        num_msg = 0
        mensagem = bytearray()
        mensagens = []
        finalizado = False
        tempo_inicio = datetime.datetime.now()
        last_mensagem = bytearray([0])

        while not finalizado:
            if com1.rx.getBufferLen() > 0:
                time.sleep(0.2)
                while com1.tx.getIsBussy():
                    pass
                rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
                #print("tenho {} bytes" .format(com1.rx.getBufferLen()))
                mensagem += rxBuffer
                print(f"Número da mensagem recebida {num_msg+1}")
                print(f"Mensagem atual: {mensagem[0]} {mensagem}")
                print(f"Last message:   {last_mensagem[0]} {last_mensagem}")
                print(f'Recebi {len(mensagem)} bytes')
                #print("aaa"*50)

                if com1.rx.getBufferLen() == 0:
                    head, payload, eop = split_message(mensagem)
                    num_msg += 1

                    print(f"len mensagens: {len(mensagens)}")
                    print(f'num_msg: {num_msg}')

                    if mensagem == last_mensagem:
                        print("mensagem atual igual a ultima")
                        com1.sendData(MENSAGEM_SUCESSO)
                        print("Mensagem recebida! Enviando mensagem de sucesso 1")
                        num_msg -= 1

                    elif num_msg == mensagem[0] - 1:
                        com1.sendData(MENSAGEM_VOLTA)
                        num_msg -= 1
                        print("VEIO UM A MAIS VOLTA AI MANOS")
                    
                    # Checando se EOP veio errado
                    elif eop != b'\xfb\xfb\xfb':
                        print(eop)
                        print("Erro no EOP!")
                        num_msg -= 1
                        com1.sendData(MENSAGEM_ERRO)
                    
                    # Checando se tamanho do payload veio errado
                    elif len(payload) != int(head[2]):
                        print("Tamanho do payload não condiz com o head!")
                        print(f'Tamannho do payload recebido {len(payload)}')
                        print(f'Tamanho do payload no head {head[2]}')
                        num_msg -= 1
                        com1.sendData(MENSAGEM_ERRO)
                    
                    # Checando se o número da mensagem veio errado
                    elif num_msg != int(mensagem[0]):
                        print("Número do pacote não condiz!")
                        print(f'Número da mensagem recebida {mensagem[0]}')
                        print(f'Número da mensagem interna {num_msg}')
                        num_msg -= 1
                        com1.sendData(MENSAGEM_ERRO)

                    # Checando se o tamanho da mensagem é menor ou igual a 65
                    elif len(mensagem) > 65:
                        print(f"Tamanho da mensagem inesperado! {len(mensagem)}")
                        num_msg -= 1
                        com1.sendData(MENSAGEM_ERRO)
                    
                    # Se o número da mensagem for igual ao total de pacotes, acaba a comunicação
                    elif num_msg == int(mensagem[1]):
                        print("Comunicação encerrada.")
                        mensagens.append(mensagem)
                        com1.sendData(MENSAGEM_ENCERRADA)
                        finalizado = True
                    else:
                        # Adicionando mensagem na lista de mensagens e enviando a mensagem de sucesso
                        mensagens.append(mensagem)
                        com1.sendData(MENSAGEM_SUCESSO)
                        last_mensagem = mensagens[-1]
                        print("Mensagem recebida! Enviando mensagem de sucesso 2")

                    mensagem = bytearray()
                    tempo_inicio = datetime.datetime.now()
            
            if (datetime.datetime.now() - tempo_inicio > datetime.timedelta(seconds=5)):
                    print("Não recebo nada já faz 5 segundos")
                    tempo_inicio = datetime.datetime.now()
                    print('enviando mensagem de erro...')
                    com1.sendData(MENSAGEM_ERRO)                   
                    

        if finalizado == False:
            print("Aconteceu algum erro...")
        else:
            # Encerra comunicação
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")
            com1.disable()

        print(mensagens)

        imagem = bytearray()
        for mensagem in mensagens:
            head, payload, eop = split_message(mensagem)
            imagem += payload

        print("Salvando dados de arquivo")
        print(" {} ".format(imageW))
        f = open(imageW, 'wb')
        f.write(imagem)

        f.close()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
