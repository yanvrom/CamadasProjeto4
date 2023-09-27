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

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM5"                  # Windows(variacao de)

imageW = 'copia.png'

EOP = b'\xaa\xbb\xcc\xdd'

# h0    h1      h2   h3     h4      h5        h6         h7         h8   h9
# tipo server livre total pacote id/tamanho reenvio ultimo_recebido CRC CRC
# h0 - tipo de mensagem (fixo)
# h1 - número do server (fixo)
# h2 - byte livre (00)
# h3 - total de pacotes (depende do cliente)
# h4 - número do pacote
# h5 - id/tamanho (id do pacote do handshake / tamanho do payload sendo enviado pelo cliente)
# h6 - número do pacote para reenvio (se não tem reenvio, 00)
# h7 - último pacote recebido com sucesso
# h8 - CRC (00)
# h9 - CRC (00)

server = 218

MENSAGEM_T2 = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00' + EOP #                       -- MENSAGEM DE OCIOSO - PRONTO PARA RECEBER
#MENSAGEM_T4 = b'\04\00\00\00' + int.to_bytes(255, 1, 'little') + b'\00\00\00\00' + EOP -- MENSAGEM DE SUCESSO
MENSAGEM_T5 = b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00' + EOP #                       -- MENSAGEM DE CHECAR TIME OUT
#MENSAGEM_T6 = b'\06\00\00\00\00' + int.to_bytes(255, 1, 'little') + b'\00\00\00' + EOP -- MENSAGEM DE ERRO

def gera_mensagem_t4(num_pacote_confirmado):
    return b'\x04\x00\x00\x00\x00\x00\x00' + int.to_bytes(num_pacote_confirmado, 1, 'little') + b'\x00\x00' + EOP

def gera_mensagem_t6(num_pacote_esperado):
    return b'\x06\x00\x00\x00\x00\x00' + int.to_bytes(num_pacote_esperado, 1, 'little') + b'\x00\x00\x00' + EOP

def split_message(message):
    head = message[0:10]
    eop = message[-4:]
    message = message[10:]
    message = message[:-4]
    payload = message

    return head, payload, eop

def checa_crc(polinomio_input, teste):
    pass

def escreve_report(entrada, id):
    with open(f"Server{id},txt", 'w') as arquivo:
        arquivo.write(entrada)
    arquivo.close()

def main():
    try:

        id = 0
        while os.path.exists(f"{id}.txt"):
            id += 1

        tempo = datetime.datetime.now()
        escreve_report('teste', id)
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        

        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        tempo = datetime.datetime.now()
        print(tempo,end=' ')
        print("Abriu a comunicação")
        print("esperando 1 byte de sacrifício")

        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(.1)

        ocioso = True

        while ocioso:
            if com1.rx.getBufferLen() >= 10:
                rxBuffer, _ = com1.getData(10)
                head = rxBuffer
                tempo = datetime.datetime.now()
                
                print(tempo,end=' ')
                print(head)
                
                time.sleep(0.1)
                if head[0] == 1:
                    rxBuffer, _ = com1.getData(4)
                    eop = rxBuffer
                    tempo = datetime.datetime.now()
                    
                    print(tempo,end=' ')
                    print(eop)

                    if eop != EOP:
                        print("Erro no EOP!")
                        head = bytearray()
                        time.sleep(1)
                    
                    if head[0] == 1 and head[1] == server:
                        num_pckg = head[3]
                        id_arquivo = head[5]
                        ocioso = False
                        com1.sendData(MENSAGEM_T2)
                        print('enviei mensagem T2')
                else:
                    pass
                    
        tempo = datetime.datetime.now()
        print(tempo,end=' ')
        print("Handshake feito!")

        cont = 1
        mensagem = bytearray()
        mensagem_finalizada = bytearray()

        timer1 = datetime.datetime.now()
        timer2 = datetime.datetime.now()
        flag_timeout = False
        
        while cont <= num_pckg:
            
            tempo = datetime.datetime.now()

            # CHECANDO SE CHEGOU ALGUMA MENSAGEM
            if com1.rx.getBufferLen() >= 14:
                time.sleep(0.5)
                timer1 = datetime.datetime.now()
                timer2 = datetime.datetime.now() 
                rxBuffer, _ = com1.getData(com1.rx.getBufferLen())
                mensagem = rxBuffer

                head, payload, eop = split_message(mensagem)

                print(head, payload, eop)

                flag_erro = False

                print(tempo,end=' ')
                
                # CHECANDO SE EOP VEIO CERTO
                if eop != EOP:
                    erro_msg = "Erro no EOP!"
                    flag_erro = True

                # CHECANDO SE PAYLOAD CONDIZ COM HEAD
                elif len(payload) != head[5]:
                    erro_msg = f"Payload de tamanho {len(payload)}, mas head diz {head[5]}"
                    flag_erro = True

                # CHECANDO SE NUMERO DA MENSAGEM RECEBIDA E O ESPERADO
                elif cont != head[4]:
                    erro_msg = f"Esperando mensagem {cont}, mas head diz {head[4]}"
                    flag_erro = True

                # CHECANDO SE A MENSAGEM PASSA DO LIMITE DE 128 BYTES
                elif len(mensagem) > 128:
                    erro_msg = f"Recebida uma mensagem de tamanho {len(mensagem)}, mas o máximo é 128"
                    flag_erro = True

                # SE NÃO HOUVE ERRO, ENVIA SUCESSO. CASO CONTRÁRIO, ENVIA ERRO
                if not flag_erro:
                    print('sucesso')
                    mensagem_finalizada += payload
                    com1.sendData(gera_mensagem_t4(cont))
                    cont += 1
                else:
                    print(erro_msg)
                    com1.sendData(gera_mensagem_t6(cont))

            else:
                if datetime.datetime.now() - timer2 > datetime.timedelta(seconds=20):
                    print(tempo,end=' ')
                    print('Comunicação finalizada por timeout.')
                    ocioso = True
                    flag_timeout = True
                    com1.sendData(MENSAGEM_T5)
                    break
                
                elif datetime.datetime.now() - timer1 > datetime.timedelta(seconds=2):
                    print(tempo,end=' ')
                    print('Não recebo nada há 2 segundos, enviando alô...')
                    print(gera_mensagem_t4(cont-1))
                    com1.sendData(gera_mensagem_t4(cont-1))
                    timer1 = datetime.datetime.now()
                    mensagem = bytearray()
        
        ocioso = True

        if not flag_timeout:
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")
        else:
            print("Timeout!")

        com1.disable()

        print(mensagem_finalizada)

        print("Salvando dados de arquivo")
        print(" {} ".format(imageW))
        f = open(imageW, 'wb')
        f.write(mensagem_finalizada)

        f.close()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
