from PyQt5 import QtWidgets
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
import sys


class Tela(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        
        self.app = QtGui.QApplication(sys.argv)
        
        super(QtWidgets.QMainWindow, self).__init__(*args, **kwargs)
        
        self.range = 1280
        
        self.area = DockArea()
        self.dock_AF3 = Dock("AF3")
        self.dock_T7 = Dock("T7")
        self.dock_Pz = Dock("Pz")
        self.dock_T8 = Dock("T8")
        self.dock_AF4 = Dock("AF4")


        self.area.addDock(self.dock_AF3, 'bottom')
        self.area.addDock(self.dock_T7, 'bottom')
        self.area.addDock(self.dock_Pz, 'bottom')
        self.area.addDock(self.dock_T8, 'bottom')
        self.area.addDock(self.dock_AF4, 'bottom')


        self.canalAF3 = []
        self.penAF3 = pg.mkPen(color=(255, 0, 0))
        self.widget_AF3 = pg.PlotWidget()
        
        
        self.canalT7 = []
        self.penT7 = pg.mkPen(color=(0, 0, 255))
        self.widget_T7 = pg.PlotWidget()
        
        self.canalPz = []
        self.penPz = pg.mkPen(color=(0, 128, 0))
        self.widget_Pz = pg.PlotWidget()
        
        
        self.canalT8 = []
        self.penT8 = pg.mkPen(color=(128, 0, 128))
        self.widget_T8 = pg.PlotWidget()
        
        
        self.canalAF4 = []
        self.penAF4 = pg.mkPen(color=(255, 125, 0))
        self.widget_AF4 = pg.PlotWidget()
        
        
        self.tempo = []
        self.t = []
        
        self.read_file()
        
        self.linha_AF3 = self.widget_AF3.plot(y = self.canalAF3, pen=self.penAF3)
        self.widget_AF3.setYRange(min(self.canalAF3) - 100, max(self.canalAF3) + 100, padding=0.5)
        self.widget_AF3.plotItem.showGrid(y = True)
        self.widget_AF3.setBackground('w')
        self.widget_AF3.setMouseEnabled(x=False, y=True)
        self.dock_AF3.addWidget(self.widget_AF3)
        
        
        self.linha_T7 = self.widget_T7.plot(y = self.canalT7, pen=self.penT7)
        self.widget_T7.setYRange(min(self.canalT7) - 100, max(self.canalT7) + 100, padding=0.5)
        self.widget_T7.plotItem.showGrid(y = True)
        self.widget_T7.setBackground('w')
        self.widget_T7.setMouseEnabled(x=False)
        self.dock_T7.addWidget(self.widget_T7)
        
        
        self.linha_Pz = self.widget_Pz.plot(y = self.canalPz, pen=self.penPz)
        self.widget_Pz.setYRange(min(self.canalPz) - 100, max(self.canalPz) + 100, padding=0.5)
        self.widget_Pz.plotItem.showGrid(y = True)
        self.widget_Pz.setBackground('w')
        self.widget_Pz.setMouseEnabled(x=False)
        self.dock_Pz.addWidget(self.widget_Pz)
        
        
        self.linha_T8 = self.widget_T8.plot(y = self.canalT8, pen=self.penT8)
        self.widget_T8.setYRange(min(self.canalT8) - 100, max(self.canalT8) + 100, padding=0.5)
        self.widget_T8.plotItem.showGrid(y = True)
        self.widget_T8.setBackground('w')
        self.widget_T8.setMouseEnabled(x=False)
        self.dock_T8.addWidget(self.widget_T8)
        
        
        self.linha_AF4 = self.widget_AF4.plot(y = self.canalAF4, pen=self.penAF4)
        self.widget_AF4.setYRange(min(self.canalAF4) - 100, max(self.canalAF4) + 100, padding=0.5)
        self.widget_AF4.plotItem.showGrid(y = True)
        self.widget_AF4.setBackground('w')
        self.widget_AF4.setMouseEnabled(x=False)
        self.dock_AF4.addWidget(self.widget_AF4)
    
    def read_file(self):
        with open('TEST2.log', 'r') as f:

            data_log = f.readlines() #Lista com todas as linhas do log
            data_log.pop(0) #Remove cabeçalho "af3;tz;...;af4"

            for linha in data_log:

                eletrodos = linha.split(';') #Organiza os dados em uma lista a partir do delimitador ;

                #Listas dos dados de cada canal
                self.canalAF3.append(float(eletrodos[0]))
                self.canalT7.append(float(eletrodos[1]))
                self.canalPz.append(float(eletrodos[2]))
                self.canalT8.append(float(eletrodos[3]))
                self.canalAF4.append(float(eletrodos[4]))

    
    def graph_timer(self):
        
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start()
        
    def update_graph(self):
        
        # Remover primeiro elemento
        self.canalAF3.pop(0)
        self.canalT7.pop(0)
        self.canalPz.pop(0)
        self.canalT8.pop(0)
        self.canalAF4.pop(0) 
     
        # Atualizar linhas
        self.linha_AF3.setData(self.canalAF3[0:self.range])
        self.linha_T7.setData(self.canalT7[0:self.range])
        self.linha_Pz.setData(self.canalPz[0:self.range])
        self.linha_T8.setData(self.canalT8[0:self.range])
        self.linha_AF4.setData(self.canalAF4[0:self.range])   

    def execute(self):
        
        sys.exit(self.app.exec_())


win_eeg = Tela()
win_eeg.setCentralWidget(win_eeg.area)
win_eeg.resize(1000, 1000)
win_eeg.setWindowTitle('EEG')
win_eeg.graph_timer()
win_eeg.show()
win_eeg.execute()
