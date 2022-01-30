from PyQt5 import QtWidgets
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
import sys, numpy as np
import time


class Tela(QtWidgets.QMainWindow):
    
    def __init__(self, opc, filename, timing, *args, **kwargs):
        
        self.app = QtGui.QApplication(sys.argv)
        
        super(QtWidgets.QMainWindow, self).__init__(*args, **kwargs)

        self.range = 1280
        self.count = 0
        self.filename = filename
        self.opc = opc
        self.timing = timing
        
            
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

        self.t = []
        
        if self.opc == 2:
            self.read_file()
        
        
        self.linha_AF3 = self.widget_AF3.plot(y=self.canalAF3, pen=self.penAF3)
        self.widget_AF3.plotItem.showGrid(y=True)
        self.widget_AF3.setBackground('w')
        self.widget_AF3.setScale(1)
        self.widget_AF3.setMouseEnabled(x=False)
        self.dock_AF3.addWidget(self.widget_AF3)

        self.linha_T7 = self.widget_T7.plot(y=self.canalT7, pen=self.penT7)
        
        self.widget_T7.plotItem.showGrid(y=True)
        self.widget_T7.setBackground('w')
        self.widget_T7.setScale(1)
        self.widget_T7.setMouseEnabled(x=False)
        self.dock_T7.addWidget(self.widget_T7)

        self.linha_Pz = self.widget_Pz.plot(y=self.canalPz, pen=self.penPz)
        
        self.widget_Pz.plotItem.showGrid(y=True)
        self.widget_Pz.setBackground('w')
        self.widget_Pz.setScale(1)
        self.widget_Pz.setMouseEnabled(x=False)
        self.dock_Pz.addWidget(self.widget_Pz)

        self.linha_T8 = self.widget_T8.plot(y=self.canalT8, pen=self.penT8)
        
        self.widget_T8.plotItem.showGrid(y=True)
        self.widget_T8.setBackground('w')
        self.widget_T8.setScale(1)
        self.widget_T8.setMouseEnabled(x=False)
        self.dock_T8.addWidget(self.widget_T8)

        self.linha_AF4 = self.widget_AF4.plot(y=self.canalAF4, pen=self.penAF4)
        
        self.widget_AF4.plotItem.showGrid(y=True)
        self.widget_AF4.setBackground('w')
        self.widget_AF4.setScale(1)
        self.widget_AF4.setMouseEnabled(x=False)
        self.dock_AF4.addWidget(self.widget_AF4)
        
        if self.opc == 1 or self.opc == 3:
            self.widget_AF3.setYRange(3900, 4600, padding=0.5)
            self.widget_T7.setYRange(3900, 4600, padding=0.5)
            self.widget_Pz.setYRange(4000, 4300, padding=0.5)
            self.widget_T8.setYRange(3900, 4400, padding=0.5)
            self.widget_AF4.setYRange(3900, 4600, padding=0.5)
        
        if self.opc == 2:
            self.widget_AF3.setYRange(min(self.canalAF3) - 100, max(self.canalAF3) + 100, padding=0.5)
            self.widget_T7.setYRange(min(self.canalT7) - 100, max(self.canalT7) + 100, padding=0.5)
            self.widget_Pz.setYRange(min(self.canalPz) - 100, max(self.canalPz) + 100, padding=0.5)
            self.widget_T8.setYRange(min(self.canalT8) - 100, max(self.canalT8) + 100, padding=0.5)
            self.widget_AF4.setYRange(min(self.canalAF4) - 100, max(self.canalAF4) + 100, padding=0.5)
        
        self.setCentralWidget(self.area)
        self.resize(1000, 1000)
        self.setWindowTitle('EEG bruto')
        self.graph_timer()
        self.show()
        
    def graph_timer(self):

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(1)
        self.timer.setInterval(1)
        
    def update_graph(self):
        
        # Remover primeiro elemento
        if len(self.canalAF3) > self.range or self.opc == 2:
            
            self.canalAF3.pop(0)
            self.canalT7.pop(0)
            self.canalPz.pop(0)
            self.canalT8.pop(0)
            self.canalAF4.pop(0)
            
            if len(self.canalAF4) == (128 * self.timing):
                
                self.close_graph()

        # Atualizar linhas
        self.linha_AF3.setData(self.canalAF3[0:self.range])
        self.linha_T7.setData(self.canalT7[0:self.range])
        self.linha_Pz.setData(self.canalPz[0:self.range])
        self.linha_T8.setData(self.canalT8[0:self.range])
        self.linha_AF4.setData(self.canalAF4[0:self.range])
        
        
        
    def execute_graph(self):
        
        sys.exit(self.app.exec_())
        
    def close_graph(self):
        
        self.app.closeAllWindows()
        
    def read_file(self):
        
        if ".csv" not in self.filename:
            
            self.filename += ".csv"
        
        with open("csv/" + self.filename, 'r') as f:

            data_csv = f.readlines()  # Lista com todas as linhas do csv
            data_csv.pop(0)  # Remove cabeçalho "af3;tz;...;af4"

            for linha in data_csv:

                # Organiza os dados em uma lista a partir do delimitador ;
                eletrodos = linha.split(';')

                self.count += 1
                
                # Listas dos dados de cada canal
                self.canalAF3.append(float(eletrodos[0]))
                self.canalT7.append(float(eletrodos[1]))
                self.canalPz.append(float(eletrodos[2]))
                self.canalT8.append(float(eletrodos[3]))
                self.canalAF4.append(float(eletrodos[4]))

    