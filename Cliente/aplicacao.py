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
import os

servidor = 218

EOP = b"\xaa\xbb\xcc\xdd"

        
def constroi_pacotes(mensagem):
    pacotes = []
    i = 0
    while i < len(mensagem):
        pacote = bytearray([])
        while len(pacote) < 114 and i < len(mensagem):
            pacote.append(mensagem[i])
            i += 1
        pacotes.append(pacote)
    return pacotes

def split_message(message):
    head = message[0:10]
    eop = message[-4:]
    message = message[10:]
    message = message[:-4]
    payload = message

    return head, payload, eop

def gera_t1(servidor, total_pacotes, id_arquivo):
    return  b'\x01' + int.to_bytes(servidor, 1, 'little') + b'\x00' + int.to_bytes(total_pacotes, 1, 'little') + int.to_bytes(id_arquivo, 1, 'little') + b'\x00\x00\x00\x00\x00' + EOP

def gera_t3(numero_do_pacote, conteudo, total_pacotes):
    head = b'\x03\x00\x00' + int.to_bytes(total_pacotes, 1, 'little') + int.to_bytes(numero_do_pacote, 1, 'little') + int.to_bytes(len(conteudo), 1, 'little') + b'\x00\x00\x00\x00'
    return head + conteudo + EOP

def gera_t5():
    return b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00' + EOP


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
        total_pacotes = len(pacotes)
        print("Serão enviados " + str(total_pacotes) + "pacotes")
        id_arquivo = 0
        while os.path.exists(f"{id_arquivo}.txt"):
            id_arquivo += 1
        
        with open(f"{id_arquivo}.txt" , 'w') as arquivo:
        # Escreva o conteúdo que desejar no arquivo
            arquivo.write("Começando transmissão\n")
            arquivo.write("....\n")
        
        handshake = False
        mensagem_hs = bytearray()

        tempo_handshake = datetime.datetime.now()
        
        com1.sendData(gera_t1(servidor, total_pacotes, id_arquivo))
        time.sleep(0.1)
        while com1.tx.getIsBussy():
            pass
        
        while not handshake:
            
            if (datetime.datetime.now() - tempo_handshake > datetime.timedelta(seconds=5)):
                print("Reenviando HANDSHAKE, NÃO HOUVE RESPOSTA")
                com1.sendData(gera_t1(servidor, total_pacotes, id_arquivo))
                time.sleep(0.1)
                tempo_handshake = datetime.datetime.now()
            
            
            if com1.rx.getBufferLen() > 0:
                rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
                mensagem_hs += rxBuffer

                if com1.rx.getBufferLen() == 0:
                    head, payload, eop = split_message(mensagem_hs)
                    
                    if eop != EOP:
                        print("Erro no EOP!")
                        break
                
                    if len(payload) != int(head[5]):
                        print("Tamanho do payload não condiz com o head!")
                        break
                    
                    if int(head[0]) == 2:
                        handshake = True
                        print("HANDSHAKE FEITO COM SUCESSO")
                    
                        
        
        i = 0 #pacote que está sendo enviado
        flag_timeout = False
        cont = 1 #contagem de quantos pacotes foram recebidos com sucesso pelo servidor
        
        
        while cont <= total_pacotes and flag_timeout == False:
            mensagem = bytearray()
            
            txBuffer = gera_t3(cont, pacotes[i], total_pacotes)
            recebeu_t4 = False
            com1.sendData(np.asarray(txBuffer))
            time.sleep(0.1)
            timer1 = datetime.datetime.now()
            timer2 = datetime.datetime.now()
            
            while com1.tx.getIsBussy():
                pass
            while not recebeu_t4:
                if (datetime.datetime.now() - timer1 > datetime.timedelta(seconds=5)):
                    print("Servidor não deu resposta há 5 segundos, reenviando...")
                    timer1 = datetime.datetime.now()
                    txBuffer = gera_t3(cont, pacotes[i], total_pacotes)
                    com1.sendData(np.asarray(txBuffer))
                    time.sleep(0.1)
                elif (datetime.datetime.now() - timer2 > datetime.timedelta(seconds=20)):
                    txBuffer = gera_t5()
                    com1.sendData(np.asanyarray(txBuffer))
                    time.sleep(0.1)
                    flag_timeout = True
                    print("Time out! Encerrando...")
                    break
                elif com1.rx.getBufferLen() > 0:
                    timer1 = datetime.datetime.now()
                    rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
                    mensagem += rxBuffer
                    
                    if com1.rx.getBufferLen() == 0:
                        head, payload, eop = split_message(mensagem)
                        
                        if eop != EOP:
                            print("EOP errado")
                        elif int(mensagem[0]) == 6:
                            pacote_esperado = int(head[6])
                            if pacote_esperado != i+1:
                                i = pacote_esperado - 1
                            txBuffer = gera_t3(cont, pacotes[i], total_pacotes)
                            com1.sendData(np.asarray(txBuffer))
                            timer1 = datetime.datetime.now()
                            timer2 = datetime.datetime.now()
                            time.sleep(0.1)
                        
                        elif int(mensagem[0]) == 4:
                            print(head)
                            pacote_recebido = int(head[7])
                            print("O pacote enviado foi " + str(cont))
                            print("O cliente falou que recebeu" + str(pacote_recebido))
                            if pacote_recebido == cont:
                                print(f"Pacote {cont} recebido com sucesso pelo servidor.")
                            recebeu_t4 = True
                    
            i += 1
            cont += 1
    
            
    
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
