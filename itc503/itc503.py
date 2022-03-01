# -*- coding: utf-8 -*-
"""
GUI for ITC503 remote control 
Version: 1.0
Author: Sebastian Hammer


needs PyQt5
"""
import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow 
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from lib.remotectrl import ctrl_ui_ITC503

class ControlITC503(QMainWindow):
    """
    Main Window of ITC503 Temperature Controller
    """    

    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__) ,'ui\\ITC503UI.ui'), self)
        self.statusConnection.showMessage('Connecting...')
        self.read_loop = QTimer()
        self.read_loop.stop()
        self.defineLiveViewLayout()

        # controler_instance
        self.ITC503 = None
    
    def defineLiveViewLayout(self):
        ### set live view properties
        self.liveViewTemp = self.liveView.addPlot(0,0)
        self.liveViewTemp.getAxis('left').setWidth(50)
        self.liveViewHeater = self.liveView.addPlot(1,0)
        self.liveViewHeater.getAxis('left').setWidth(50)
        self.liveViewValve = self.liveView.addPlot(2,0)
        self.liveViewValve.getAxis('left').setWidth(50)
        # Temperature plot
        self.liveViewTemp.setLabel('left', 'Temp. [K]')
        self.liveViewTemp.setXLink(self.liveViewValve)
        self.liveViewTemp.showGrid(x = True, y = True, alpha = 0.5)
        tempXAxis = self.liveViewTemp.getAxis('bottom')
        tempXAxis.setPen(255,255,255,0)
        tempXAxis.setStyle(showValues = False)
        # Heater power plot
        self.liveViewHeater.setLabel('left', 'Heater [V]')
        self.liveViewHeater.setLimits(yMin=-0.05)
        self.liveViewHeater.setXLink(self.liveViewValve)
        tempXHeater = self.liveViewHeater.getAxis('bottom')
        tempXHeater.setStyle(showValues = False)
        tempXHeater.setPen(255,255,255,0)
        self.liveViewHeater.showGrid(x = True, y = True, alpha = 0.5)
        # Valve opening plot
        self.liveViewValve.setLabel('left', 'Valve [%]')
        self.liveViewValve.setLabel('bottom', 'Time [s]')
        self.liveViewValve.setLimits(yMin=-0.05)
        tempXValve = self.liveViewValve.getAxis('bottom')
        tempXValve.setPen(255,255,255,0)
        self.liveViewValve.showGrid(x = True, y = True, alpha = 0.5)

    def closeEvent(self, event):
        """
        When MainWindow is closed stop time loop and set ITC503 controler to LOCAL&UNLOCKED
                
        """
        if self.read_loop.isActive() == True:
            # Do not exit application before closing read out loop
            event.ignore()
            self.read_loop.stop()
        
        while self.ITC503.control_state.value != 2 or self.ITC503.heater_power != 0:
            # Do not exit application before making sure that the heater is switched off and the control is set back to LOCAL&UNLOCKED
            event.ignore()
            self.ITC503.set_heater_and_gas_flow(0) #Set heater and gas flow mode control to manual!
            self.ITC503.set_heater_power(0)
            self.ITC503.set_control(2)
        
        event.accept()
            

    
def main():
    ITC503 = QApplication(sys.argv)
    gui = ControlITC503()
    gui.show()
    ctrl_ui_ITC503(gui)
    sys.exit(ITC503.exec_())


"""Run GUI on its own"""
if __name__ == "__main__":
    main()
    