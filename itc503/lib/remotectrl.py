"""
control for ITC503 remote control
"""
from functools import partial
from datetime import datetime
import numpy as np
from math import floor

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from uedinst.tempcontroller import ITC503
import pyqtgraph as pg


class ctrl_ui_ITC503():
    
    def __init__(self, ui):  
        self._ui = ui
        self.global_timestamp = None
        self.save_path = None  
        self.temp_setpoint = None
        
        # initalize Data Array for live view plotting size (x,4) = ( consecutive data points, 0 and 1 position is empty | 0 : timestamp, 1: temperature, 2: heater power, 3: valve) 
        self.dataArray = np.empty((2,4))
        
        self.ITC503 = ITC503()
        self._ui.ITC503 = self.ITC503
        
        self.updateStatusbar(self.ITC503)
        self._connectSignals(self.ITC503)
             
    def _connectSignals(self, controller_instance):
        # 'Read Values'
        self._ui.parameterRead.clicked.connect(self._updateLoop)
        self._ui.parameterRead.clicked.connect(self._createLogfile)
        self._ui.parameterReadStop.clicked.connect(self._stopLoop)
        self._ui.setLockFrontpanel.stateChanged.connect(partial(self._lockUnlockPanel, controller_instance))
        self._ui.setValveSlider.sliderReleased.connect(partial(self._set_gas_flow_slider, controller_instance))
        self._ui.setValveOpen.clicked.connect(partial(self._set_gas_flow_open, controller_instance))
        self._ui.setValveClosed.clicked.connect(partial(self._set_gas_flow_closed, controller_instance))
        self._ui.setSetPoint.clicked.connect(partial(self._set_temperature_setpoint,controller_instance))
        self._ui.setEngageHeater.clicked.connect(partial(self._engange_automatic_temperature_control, controller_instance))
        self._ui.EmgStop.clicked.connect(partial(self._emergency_exit,controller_instance))
        
        self._ui.read_loop.timeout.connect(partial(self._readValuesAndWrite, controller_instance))
        self._ui.read_loop.timeout.connect(self._liveView)

        
    def _updateLoop(self):
        """
        Starts the readout time loop with time interval given by ControlITC503.ui.readOutDeltaT
        
        Raises
        -------
            Exception: if entered read out time interval is not an integer
        """
        
        delta_t_input = self._ui.readOutDeltaT.text()
        try:
            delta_t = int(floor(float(delta_t_input)*1000))
        except ValueError:
            print('Read out time needs to be a float')
            return
        
        active_flag = self._ui.read_loop.isActive()
        if active_flag == False:
            self._ui.read_loop.start(delta_t)
        elif active_flag == True:
            self._ui.read_loop.setInterval(delta_t)
        else:
            print('Unknown Error: Read out loop could not be startet')
            self._ui.read_loop.stop()
        
    def _stopLoop(self):
        """
        Stops the read out loop

        """
        self._ui.read_loop.stop()
        
    
    def _createLogfile(self):
        """
        creates a logfile at path specified in ControlITC503.ui.savePath
        if line is left empty, no logfile will be created or former log file be over written 
        
        starts read out cycle
        
        Creates
        -------
            global_timestamp: timestamp marking the beginning of new read out cycle triggered by clicking of ControlITC503.ui.parameterRead 
                datetime instance
            
            save_path: path to log file specified in ControlITC503.ui.savePath

        """
        self.save_path = self._ui.savePath.text()
        self.global_timestamp = datetime.now()
        if not self.save_path:
            pass
        else:
            with open(self.save_path, 'w') as log_file:
                log_file.write('Log file ITC503 created on {}'.format(self.global_timestamp.isoformat()))
                log_file.write('\n')
                log_file.write('time stamp YYYY-MM-DDThh:mm:ss.msmsmsmsmsms \t Temperature K \t Heater output V \t Needle valve open %')
           
    def updateStatusbar(self, controller_instance):
        """
        Updates the Statursbar with ITC controler state (remote/local & locked/unlocked) and heater and gas flow controler state (manual/auto)

        Parameters
        ----------
        controller_instance : instance of ITC503 controler class from 'model' for GPIB access

        """
        self._ui.statusConnection.showMessage('Connected --- Control State is {state} --- Heater and Gas Flow Mode is {mode}'.format(state = controller_instance.control_state.name, mode = controller_instance.heater_and_gas_flow.name)) 
   
    def _readValuesAndWrite(self, controller_instance):
        """
        reads the current values of the temperature sensor 1, heater output power in Volts and gas flow from the needle valve opening
        writes values to log file located at path specified in ControlITC503.ui.savePath

        Parameters
        ----------
        controller_instance : instance of ITC503 controler class from 'model' for GPIB access 
        
        save path : path to log file
            str
        
        Returns
        -------
            time_stamp : timestmap marking last read out
                datime instance
        """
        temperature = controller_instance.temperature
        heater_power = controller_instance.heater_power
        valve_open = controller_instance.gas_flow
        time_stamp = datetime.now()
        
        # write dataArray for live View
        self.dataArray = np.vstack((self.dataArray,  
                                    np.array([(time_stamp-self.global_timestamp).total_seconds(),
                                              temperature,
                                              heater_power,
                                              valve_open
                                              ])
        ))
               
        if not self.save_path:
            pass
        else:
            with open(self.save_path, 'a') as log_file:
                log_file.write('\n')
                log_file.write('{time} \t {temp} \t {heater} \t {valve}'.format(time = time_stamp.isoformat(), temp = temperature, heater = heater_power, valve = valve_open))
              
        
        self._ui.displayTemp.setText('{}'.format(temperature))
        self._ui.displayHeater.setText('{}'.format(heater_power))
        self._ui.displayValve.setText('{}'.format(valve_open)) 
    
    def _liveView(self):
        """
        plots the live view graph of temperature and applied heater power/valve opening

        """
        time = self.dataArray[2:,0]
        temp = self.dataArray[2:,1]
        heater = self.dataArray[2:,2]
        valve = self.dataArray[2:,3]
        # self._ui.parameterGraph.clear()
        self._ui.liveViewTemp.plot(time, temp ,name = 'Temp', pen = 'r')
        if not self.temp_setpoint:
            pass
        else:    
            self._ui.liveViewTemp.plot([time.min(), time.max()], [self.temp_setpoint, self.temp_setpoint],name = 'Temp', pen = pg.mkPen('r', width=1, style=Qt.DashLine))
        self._ui.liveViewHeater.plot(time, heater, name = 'valve')
        self._ui.liveViewValve.plot(time, valve ,name = 'Temp', pen = 'b')
           
    def _lockUnlockPanel(self, controller_instance):
        """
        Locks and unlocks the front panel control of the ITC503 device specified by the controler_instance.
        Switches the control state of the ITC503 device between state 1 (REMOTE&LOCKED) and 3 (REMOTE&UNLOCKED)

        Parameters
        ----------
        controller_instance : instance of ITC503 controler class from 'model' for GPIB access 

        """
        checkbox = self._ui.setLockFrontpanel.isChecked()
        if checkbox == False:
            controller_instance.set_control(3)
            self.updateStatusbar(controller_instance)
        elif checkbox == True:
            controller_instance.set_control(1)
            self.updateStatusbar(controller_instance)
            
    def _set_temperature_setpoint(self, controller_instance):
        """
        Sets temperature set point to value given in LineEdit _ui.setSetpointValue. 
        checks for float value of temperature setpoint, otherwise exits with exception
        
        #Debug: prints temperature value to console

        Parameters
        ----------
        controller_instance : instance of ITC503 controler class from 'model' for GPIB access 

        """
        setpoint = self._ui.setSetpointValue.text()
        try:
            setpoint = round(float(setpoint),2)
        except ValueError:
            print('Temperature setpoint needs to be a float')
            return
        
        controller_instance.set_temperature(setpoint)
        #Debug 
        self.temp_setpoint = setpoint
        print('Temperature Setpoint set to {:.2f}'.format(setpoint))
        
        
    def _engange_automatic_temperature_control(self, controller_instance):
        """
        Starts/stops automatic temperature control switching heater and gas flow control to AUTO/MANUAL.
        Disables/enables manual valve control.
        
        if motorized needle valve is connected set 'auto' to 3, otherwise to 1
        
        Parameters
        ----------
        controller_instance : instance of ITC503 controler class from 'model' for GPIB access 
        
        auto: integer
            if motorized needle valve is connected set 'auto' to 3, otherwise to 1

        """
        auto = 1
        
        heat_gas_flow_state = controller_instance.heater_and_gas_flow
        if heat_gas_flow_state.value == 0:
            controller_instance.set_heater_and_gas_flow(auto)
            self._ui.setEngageHeater.setText('Stop')   
            self._ui.setValveSlider.setEnabled(False)
            self._ui.setValveOpen.setEnabled(False)
            self._ui.setValveClosed.setEnabled(False)
            self.updateStatusbar(controller_instance)
            
        elif heat_gas_flow_state.value == auto:
            controller_instance.set_heater_and_gas_flow(0)
            controller_instance.set_heater_power(0)
            self._ui.setEngageHeater.setText('Engange')           
            self._ui.setValveSlider.setEnabled(True)
            self._ui.setValveOpen.setEnabled(True)
            self._ui.setValveClosed.setEnabled(True)
            self.updateStatusbar(controller_instance)
        else:
            controller_instance.set_heater_and_gas_flow(0)
            controller_instance.set_heater_power(0)
            self._ui.setEngageHeater.setText('Engange')   
            self._ui.setValveSlider.setEnabled(True)
            self._ui.setValveOpen.setEnabled(True)
            self._ui.setValveClosed.setEnabled(True)
            self.updateStatusbar(controller_instance)
            print('heat and gas flow mode unclear, reset to manual mode')
        
        pass
    
    def _set_gas_flow_slider(self, controller_instance):
        """
        Sets gas flow to value 'flow' in percent of needle valve opening with a resolution of 1 % determined by horizontal slider widget.
        'Gas flow' value gets updated accordingly 

        Parameters
        ----------
        controller_instance : instance of ITC503 controler class from 'model' for GPIB access 

        Raises
        -------
        from model.set_gas_flow()
        Intrument Exception : If flow setpoint is not in valid range
        InstrumentException : If flow setpoint could not be changed.
        """
        flow = self._ui.setValveSlider.value()
        controller_instance.set_gas_flow(flow)
        self._ui.displayValve.setText('{}'.format(controller_instance.gas_flow))
    
    def _set_gas_flow_open(self, controller_instance):
        """
        Fully opens the needle valve.
        Parameters
        ----------
        controller_instance : instance of ITC503 controler class from 'model' for GPIB access 

        Raises
        -------
        from model.set_gas_flow()
        Intrument Exception : If flow setpoint is not in valid range
        InstrumentException : If flow setpoint could not be changed.
        """
        controller_instance.set_gas_flow(99.9)
        self._ui.displayValve.setText('{}'.format(controller_instance.gas_flow))
    
    def _set_gas_flow_closed(self, controller_instance):
        """
        Fully closes the needle valve.

        Parameters
        ----------
        controller_instance : instance of ITC503 controler class from 'model' for GPIB access 

        Raises
        -------
        from model.set_gas_flow()
        Intrument Exception : If flow setpoint is not in valid range
        InstrumentException : If flow setpoint could not be changed.
        """
        controller_instance.set_gas_flow(0)
        self._ui.displayValve.setText('{}'.format(controller_instance.gas_flow))
        
    def _emergency_exit(self, controller_instance):
        """
        - calls model.emergency_stop halting closing the gas valve, switching of the heater and setting the controller to LOCAL&UNLOCKED
        - displays a warning message concerning the dewer pressure
        - Updates Statusbar to 'Emergency Stop - check dewer pressure'
        
        Parameters
        ----------
        controller_instance : instance of ITC503 controler class from 'model' for GPIB access 

        """
        controller_instance.emergency_stop()
        
        self._ui.read_loop.stop()
        self._ui.statusConnection.showMessage('Emergency Stop - check dewer pressure')
        self._ui.setValveSlider.setEnabled(False)
        self._ui.setValveOpen.setEnabled(False)
        self._ui.setValveClosed.setEnabled(False)
        self._ui.setSetPoint.setEnabled(False)
        self._ui.setSetpointValue.setEnabled(False)
        self._ui.setEngageHeater.setEnabled(False)
        self._ui.EmgStop.setEnabled(False)
        self._ui.setLockFrontpanel.setCheckState(False)
        self._ui.setLockFrontpanel.setCheckable(False)
        self._ui.parameterReadStop.setEnabled(False)
        self._ui.parameterRead.setEnabled(False)
        
        warningMessage = QMessageBox(QMessageBox.Critical, 'Emergency Stop', ' Heater is off and Valve is closed \n ITC503 is in Local Control \n \n Check Dewer pressure and realse coolant if neccesary!')
        warningMessage.exec()
               
        