=============
ITC503Control
=============
Version 1.0.0

ITC503Control provides a GUI for remote control of the ITC503 temperature controller in the Siwick Lab. The following features are included:

* Live tracking of temperature, heater output and needle valve parameters in costum time steps

* Plotting of these key values over time

* creating a log file of the key values over time

* setting a temperature set point and starting automatic PID control

* manually controlling the needle valve

It shows a live view of the temperature at sensor 1, the heater output and the motorized needle valve as well as a plot over time of these values. 


Intented usage would be opening the UI control from the command line as: 

        python -m itc503.itc503

The itc503 module contains a 'main()' function which is run when itc503 is run as __main__ starting the even loop of the QTPY applicaton amd the UI. 
The programm is intended to be use with uedinst (Siwick Lab) and requires 'itc503gpib.py' to be located there. This module takes care of the GPIB communication with the controller device. See 'Dependencies and Adaptation' for further information. 

The GPIB address is hardcoded to be '::24'


Control Elements
================

This section gives an overview of the different control elements of the GUI and their functionality. 

ITC 503 Parameters
------------------

If the live view has been started this section shows the current 

* temperature in Kelvin 

* heater output in Volts

* needle valve opened in Percent

Live View
---------

If the live view has been started this section shows plots of the temperature, the heater output and the needle valve opening over time from top to bottom, respectively. The start point t=0 is defined by the time the 'Live' button has been pressed the last time. 

If a temperature set point has been set, it is inidcated as a horizontal line in the temperature plot. 

Temperature Control
-------------------

Enabling and Stopping of the automatic PID temperature control. Enter a temperature set point as a target temperature for the controller and transmit it to the controller via the 'Set' button. The 'Engage' button starts the automatic temperature control. 

If the automatic temperature control has been enabled the 'Engage' button becomes a 'Stop' button. Pressing this button stops the automatic temperature control at returns the controller to the manual control state. 

Valve Control
-------------

Manual Control of the motorized needle valve. The horizontal slider can be used to set a certain percentage of needle valve opening. 
ATTENTION: To avoid overloading the GPIB interface with queries the query to change the opening of the needle valve is only triggered after RELEASING the slider, not upon update. clicking on the slider to change the value does not work, the slider needs to be dragged.

The 'open' and 'close' button fully open and close the needle valve, respectively. 

Lock Frontpanel
---------------

The frontpanel of the controler device is locked preventing local control of the device. The standard value is switched of. 
ATTENTION: If the frontpanel is locked and remote control crashes, the controler is left in an 'uncontrolable' state and can only be retrieved by reestablishing remote control. 

Live View control
-----------------

Read-out time/s give sets the update time interval of the live view values. The standard value is 2 seconds. 
ATTENTION: Setting this value to low, can lead to an overload of queries for GPIB interface. 

The buttons 'Live' and 'Stop' respectively start and stop the live view. The time interval is only changed by pressing the 'Live' button.
ATTENTION: The clicking of the 'Live' button leads to overwriting the current log file with a new file starting at the current time stamp 

Log file path
-------------

Specifies the path of the log file. If left empty no log file will be created.

Emergency Stop
--------------

This button immediately stops the remote control triggering the following events:

* The Live View of any parameters is ended

* The heater output is set to zero

* The needle valve is closed 

* The controller device is set to LOCAL control and the front panel is unlocked

ATTENTION: Pay close attention to the colant dewer as a closed needle valve can lead to pressure built up! 

Closing the Application
=======================

Upon closing the application the following steps are performed: 

* the live view loop is stopped

* the heater power is set to zero 

* the controler device is put into LOCAL&UNLOCKED control module

After that the application is closed. 

Dependencies and Adaptation
===========================

uedinst Dependency
------------------

The module 'itc503gpib' introduces the 'ITC503' class which contains the functions necessary to communicate with the ITC503 device. The communication relies on the 'GPIBBase' class which is located in the 'base' module of uedinst. This class is based upon the PyVisa resource manager. 
Furthermore, the IntrumentException Error is introduced by the uedinst __init__ which is used to raise errors during the communication with the ITC503 device. 

GPIB address
------------
The GPIB address of the ITC503 device is defined in 'itc503gpib' as a global variable in line 23

23 gpib_address = 24

which opens the connection on GPIB port '::24'.
If the GPIB address of the controler changes, change the address by changing the varibale 'gpib_address' in line 23 of 'itc503gpib' in the uedinst package. 