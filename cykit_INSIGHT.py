from datetime import datetime
import time
import signal
from cyCrypto import Random
from cyCrypto.Cipher import AES
import queue
import cyPyWinUSB as hid
import sys
import os
import time
import threading

from ifkit_GRAPH import Tela

sys.path.insert(0, '..//py3//cyUSB//cyPyWinUSB')
sys.path.insert(0, '..//py3')


tasks = queue.Queue()

EEG_name = {"AF3": 3, "T7": 5, "Pz": 7, "T8": 12, "AF4": 14}


class EEG_insight(object):

    def __init__(self):  # Escaneia as portas USB's e procura pelo Insight, acessa o número de serial e descriptografa os dados

        self.hid = None
        devicesUsed = 0
        self.delimiter = ";"
        self.canal_AF3 = []
        self.canal_T7 = []
        self.canal_Pz = []
        self.canal_T8 = []
        self.canal_AF4 = []
        self.data = []  # para arquivo.log
        self.tempo = []  # para gráfico
        self.start = 0
        self.tela = None
        self.filename = str(
            input('\nInforme um nome para o arquivo de gravação: '))

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
        k = [sn[-1], 00, sn[-2], 21, sn[-3], 00, sn[-4], 12,
             sn[-3], 00, sn[-2], 68, sn[-1], 00, sn[-2], 88]

        self.key = bytes(bytearray(k))
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    def signal_handler(self, signal, frame):

        dur = time.time() - self.start
        print(f'Inicío: {self.start}\nDuração: {dur}\nFim: {datetime.now()}')
        self.gen_file(self.filename)
        sys.exit(0)

    def dataHandler(self, data):

        if self.cipher == None:
            return
        join_data = ''.join(map(chr, data[1:]))
        data = self.cipher.decrypt(bytes(join_data, 'latin-1')[0:32])
        tasks.put(data)

    # Converte os dados adquiridos para o formato de tensão
    def convert_v2(self, value_1, value_2):
        edk_value = "%.8f" % (((int(value_1) - 128) * 32.82051289) +
                              ((int(value_2) * .128205128205129) + 4201.02564096001))
        return edk_value

    def get_data(self):  # Aquisição dos dados

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

        self.start = time.time()

        while 1:

            eeg_data = cyHeadset.get_data()

            # Aquisição dos dados de cada canal para plotagem em tempo real
            self.tela.canalAF3.append(float(eeg_data[EEG_name["AF3"]]))
            self.tela.canalT7.append(float(eeg_data[EEG_name["T7"]]))
            self.tela.canalPz.append(float(eeg_data[EEG_name["Pz"]]))
            self.tela.canalT8.append(float(eeg_data[EEG_name["T8"]]))
            self.tela.canalAF4.append(float(eeg_data[EEG_name["AF4"]]))

            # Aquisição dos dados de cada canal para salvar no arquivo .log
            self.canal_AF3.append(str(eeg_data[EEG_name["AF3"]]))
            self.canal_T7.append(str(eeg_data[EEG_name["T7"]]))
            self.canal_Pz.append(str(eeg_data[EEG_name["Pz"]]))
            self.canal_T8.append(str(eeg_data[EEG_name["T8"]]))
            self.canal_AF4.append(str(eeg_data[EEG_name["AF4"]]))
            # Lista com instantes de aquisição de cada dado - Exemplo: '2021-10-13 10:53:48.813976'
            self.data.append(datetime.now())

    def gen_file(self, filename):  # Gera arquivo de gravação e salva os dados adquiridos

        if ".log" not in filename:
            filename += ".log"

        with open("logs/" + filename, "w+") as f:

            f.write("AF3; T7; Pz; T8; AF4; Tempo\n")

            for c in range(len(self.canal_AF3)):

                linha = self.canal_AF3[c] + self.delimiter + self.canal_T7[c] + self.delimiter + self.canal_Pz[c] + \
                    self.delimiter + self.canal_T8[c] + self.delimiter + \
                    self.canal_AF4[c] + self.delimiter + \
                    str(self.data[c]) + "\n"
                f.write(linha)


if os.name == 'nt':
    os.system("mode con:cols=80 lines=14")  # Resize screen (for Windows)

cyHeadset = EEG_insight()
eeg_data = []
data_thread = threading.Thread(name=" Update_EEG_Headset", target=cyHeadset.data_list, daemon=False)
init = True


while 1:

    if init == True:
        cyHeadset.tela = Tela(filename= cyHeadset.filename)
        data_thread.start()
        cyHeadset.tela.execute()
        init = False

    time.sleep(0)
    while tasks.empty():
        time.sleep(0)
        pass
