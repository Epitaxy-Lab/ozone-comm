# Ozone Control Device

This project aimed to provide steady and reproducible ozone pressures in the Falson Group's MBE
chamber. By implementing custom PID control, the ozone leak valve is adjusted to reach and 
maintain the desired pressure, based on ion gauge readings.

This code is intended to run on a Raspberry Pi 4, with serial connections made to the relevant
leak valve and ion gauge.

To run, simply make the Serial connections (through USB), and run `python ozone_control.py`. Users may need to specify `python3` depending on their previous installations.

Once the connections are selected, and successfully made, the control GUI will pop up. Shown below is the working version of the device, rack mounted in the Falson Lab at Caltech.

![](img/working_ozcomm.jpg)
