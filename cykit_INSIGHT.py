import time, signal, queue, sys, os, time, threading
from cyCrypto import Random
from cyCrypto.Cipher import AES
from datetime import datetime
from ifkit_GRAPH import Tela
import cyPyWinUSB as hid
import numpy as np


sys.path.insert(0, '..//py3//cyUSB//cyPyWinUSB')
sys.path.insert(0, '..//py3')


tasks = queue.Queue()

EEG_name = {"AF3": 3, "T7": 5, "Pz": 7, "T8": 12, "AF4": 14}


class EEG_insight(object):

    def __init__(self):
        
        """
        1- Cria as principais variáveis da classe;
        2- Escaneia as portas USB's e procura pelo Insight, acessa o número de serial e descriptografa os dados 
        """

        self.hid = None
        devicesUsed = 0
        self.delimiter = ";"
        self.canal_AF3 = []
        self.canal_T7 = []
        self.canal_Pz = []
        self.canal_T8 = []
        self.canal_AF4 = []
        self.data = []
        self.tempo = []
        self.start = 0
        self.tela = None
          
        self.interface_eeg()
        
        signal.signal(signal.SIGINT, self.signal_handler)

        self.cipher = None
        for device in hid.find_all_hid_devices():
            if device.product_name == 'EEG Signals':
                devicesUsed += 1
                self.hid = device
                self.hid.open()
                self.serial_number = device.serial_number
                device.set_raw_data_handler(self.dataHandler)
        if devicesUsed == 0:
            os._exit(0)

        sn = bytearray()
        for i in range(0, len(self.serial_number)):
            sn += bytearray([ord(self.serial_number[i])])

        # Insight Keymodel.
        k = ['\0'] * 16
        k = [sn[-1], 00, sn[-2], 21, sn[-3], 00, sn[-4], 12, sn[-3], 00, sn[-2], 68, sn[-1], 00, sn[-2], 88]

        self.key = bytes(bytearray(k))
        self.cipher = AES.new(self.key, AES.MODE_ECB)
        
    def interface_eeg(self):
        
        print("\n" + " " * 17 + "\033[1;32mIFKit\033[m"  
            "\n\n"
            "\n\033[7;32mPRESSIONE 'Ctrl+C' PARA ENCERRAR O PROGRAMA\033[m\n"
            "\n\033[0;32m[1] - EEG bruto em tempo real\033[m"
            "\n\033[0;32m[2] - EEG bruto lido em arquivo .csv\033[m"
            "\n\033[0;32m[3] - Plotagem personalizada\033[m")
    
        self.opc = int(input('\033[1;32mOpção: \033[m'))
        
        if self.opc == 1:
            
            self.save = str(input("\033[1;32mVocê deseja salvar os dados em um arquivo .csv [S/N]?\033[m "))
            
            if self.save == 'S':
                
                self.filename = str(input('\033[1;32mInforme o nome do arquivo:\033[m '))
            
            elif self.save == 'N':
                
                self.filename = ''
        
        elif self.opc == 2:
            
            self.filename = str(input('\033[1;32mInforme o nome do arquivo a ser lido:\033[m '))
            
        elif self.opc == 3:
            
            self.timing = int(input("\033[1;32mInforme a duração da gravação (segundos):\033[m "))
            self.save = str(input("\033[1;32mVocê deseja salvar os dados em um arquivo .csv [S/N]?\033[m "))            
            
            if self.save == 'S':
                
                self.filename = str(input('\033[1;32mInforme o nome do arquivo:\033[m '))
            
            elif self.save == 'N':
                
                self.filename = ''
        
        else:
            print("\nERRO")
            sys.exit(0)
        
    def signal_handler(self, signal, frame):
        
        """
        Função manipuladora de sinal
        É acionada no método __init__ quando o usuário pressiona Ctrl+C
        Assim, fica responsável por encerrar a execução do código mostrando:
        Início; Duração; Fim. 
        Além de gravar os dados adquiridos no arquivo .csv bem como fechar o gráfico.
        """
        self.tela.close_graph()
        
        if self.opc == 1:
            
            #Marcação do fim do programa
            self.end = time.time()
            
            #Duração da execução do programa;
            self.dur = self.end - self.start
            
            #Formatação da string do tempo de início
            self.s = time.gmtime(self.start)
            self.s = time.strftime("%d/%m/%Y %H:%M:%S", self.s)
            
            #Formatação da string do tempo de encerramento
            self.e = time.gmtime(self.end)
            self.e = time.strftime("%d/%m/%Y %H:%M:%S", self.e)
            
            
            print(f'\n\033[1;32mInicío:\033[m {self.s}'
                f'\n\033[1;32mDuração:\033[m {self.dur:.2f} segundos'
                f'\n\033[1;32mFim:\033[m {self.e}')

        
        if self.opc == 1 and self.save == 'S':
            
            self.gen_file(self.filename, self.save)
            
        elif self.opc == 1 and self.save == 'N':
            
            print("\nArquivo não salvo")
        
        elif self.opc == 2:
            
            print("\nArquivo lido com sucesso.")
        
        elif self.opc == 3:
            
            print('\nPlotagem interrompida...')

        print("\n\033[7;32mPROGRAMA ENCERRADO\n\033[m")
        #self.do_fft()
        
            
    def dataHandler(self, data):

        """
        Função manipuladora de dados
        Realiza a descriptografia da cifra dos dados do headset 
        """
        
        if self.cipher == None:
            
            return
        1
        join_data = ''.join(map(chr, data[1:]))
        data = self.cipher.decrypt(bytes(join_data, 'latin-1')[0:32])
        tasks.put(data)

    def convert_v2(self, value_1, value_2):
        
        """
        Converte os dados adquiridos para o formato de tensão 
        """
        
        edk_value = "%.8f" % (((int(value_1) - 128) * 32.82051289) + ((int(value_2) * .128205128205129) + 4201.02564096001))
        
        return edk_value

    def get_data(self):
        
        """
        Aquisição dos dados
        """

        try:
            data = tasks.get()

            packet_data = [data[0]]
            z = ''
            for i in range(1, len(data)):
                z = z + format(data[i], '08b')

            i_1 = -14
            for i in range(0, 18):
                i_1 += 14
                v_1 = '0b' + z[(i_1):(i_1 + 8)]
                v_2 = '0b' + z[(i_1 + 8):(i_1 + 14)]
                packet_data.append(
                    str(self.convert_v2(str(eval(v_1)), str(eval(v_2)))))
            return packet_data

        except Exception as exception2:

            print(str(exception2))

    def data_list(self):
        
        """
        Função responsável por adicionar os dados de cada canal em sua respectiva lista
        No total, são 10 listas: 
        5 com dados em float para plotagem em tempo real
        5 com dados em str para salvar no arquivo .csv
        """
        
        if self.opc == 1 or self.opc == 3:
            
            self.start = time.time()
            
            print('\nCapturando os dados...')
        
            while 1:

                eeg_data = cyHeadset.get_data()
                
                # Aquisição dos dados de cada canal para plotagem em tempo real
                self.tela.canalAF3.append(float(eeg_data[EEG_name["AF3"]]))
                self.tela.canalT7.append(float(eeg_data[EEG_name["T7"]]))
                self.tela.canalPz.append(float(eeg_data[EEG_name["Pz"]]))
                self.tela.canalT8.append(float(eeg_data[EEG_name["T8"]]))
                self.tela.canalAF4.append(float(eeg_data[EEG_name["AF4"]]))
                

                # Aquisição dos dados de cada canal para salvar no arquivo .csv
                self.canal_AF3.append(str(eeg_data[EEG_name["AF3"]]))
                self.canal_T7.append(str(eeg_data[EEG_name["T7"]]))
                self.canal_Pz.append(str(eeg_data[EEG_name["Pz"]]))
                self.canal_T8.append(str(eeg_data[EEG_name["T8"]]))
                self.canal_AF4.append(str(eeg_data[EEG_name["AF4"]]))
                
                # Lista com instantes de aquisição de cada dado - Exemplo: '2021-10-13 10:53:48.813976'
                self.data.append(datetime.now())
                                      
    def do_fft(self):
        
        """
        Calcula a FFT para cada canal
        Entrada: lista composta com os dados de cada canal canais
        """
        
        self.fft_AF3 = list(map(lambda x: abs(np.fft.fft(x)), self.canal_AF3))
        self.fft_T7 = list(map(lambda x: abs(np.fft.fft(x)), self.canal_T7))
        self.fft_Pz = list(map(lambda x: abs(np.fft.fft(x)), self.canal_Pz))
        self.fft_T8 = list(map(lambda x: abs(np.fft.fft(x)), self.canal_T8))
        self.fft_AF4 = list(map(lambda x: abs(np.fft.fft(x)), self.canal_AF4))
        
        
        print(self.fft_AF4)

    
    def get_fft(self, all_channel_data):
        
        #Taxa de amostragem em Hertz (128 amostras por segundo)
        Fs = 128 
        
        #Comprimento do sinal  ou número total de amostras
        L = len(all_channel_data[0])

    def gen_file(self, filename, save):
        
        """
        A partir do nome do arquivo informado pelo usuário, adiciona no nome do arquivo ".csv" e salva os dados adquiridos na pasta .csv
        """
        self.save = save
        
        if self.save == 'S':
            
            if ".csv" not in filename:
                print('\nInserindo .csv no nome do arquivo...')
                time.sleep(1)
                filename += ".csv"
            

            with open("csv/" + filename, "w+") as f:

                f.write(f"AF3; T7; Pz; T8; AF4; Tempo; Início: {self.s};Fim: {self.e}; Duração: {self.dur}\n")

                for c in range(len(self.canal_AF3)):

                    linha = self.canal_AF3[c] + self.delimiter + self.canal_T7[c] + self.delimiter + self.canal_Pz[c] + \
                        self.delimiter + self.canal_T8[c] + self.delimiter + \
                        self.canal_AF4[c] + self.delimiter + \
                        str(self.data[c]) + "\n"
                        
                    f.write(linha)
                    
            print('\nArquivo gerado.')
        
        elif self.save == 'N':
            
            print('\nArquivo não foi gerado.')
            
            
            
            
if os.name == 'nt':
    os.system("mode con:cols=80 lines=14")  # Resize screen (for Windows)


cyHeadset = EEG_insight()
eeg_data = []
data_thread = threading.Thread(name=" Update_EEG_Headset", target=cyHeadset.data_list, daemon=False)
init = True


while 1:

    if init == True:
            
            cyHeadset.tela = Tela(opc=cyHeadset.opc, filename=cyHeadset.filename, timing=cyHeadset.timing)
            
            if cyHeadset.opc == 1 or cyHeadset.opc == 3:
                
                data_thread.start()

            cyHeadset.tela.execute_graph()
            init = False

    time.sleep(0)
    
    while tasks.empty():
        time.sleep(0)
        pass