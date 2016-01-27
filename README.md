# OpticalPowerMeterController
Computer control of an optical powermeter (Newport 1830-C) via Prologix GPIB-USB controller 

* Introduction
 
Optical powermeters are quintessential devices in an optical lab. Frequently, one needs the ability to control them via a computer. For example, consider an experiment where the measurement wavelength is continuously changed (or tuned) in a known manner, and the -- fluctuating -- power needs to be measured. The ability to set the wavelength and power units automatically via the computer (which is also controlling other parameters in the experiment) would allow a synchronized and meaningful power readout. 

The powermeter (PM) for which this Python code was written is from the 1830-C series, manufactured and sold by Newport Corp. It is probably obsolete now: at least I couldn't find the exact user manual for this but I believe the 1830-R series manual, which can be searched on the Internet, comes pretty close. The communication between the 1830-C and the computer was performed using a USB-GPIB controller from Prologix. (It should be possible to port the code with minimal changes to control other powermeters using GPIB.) The manual from Prologix can also be searched on the Internet.  

* Code-specific info:

The essential library functions to control the PM are provided. There is also a dummy 'main' program, where after the necessary initialization, power values are continuously read through the controller. The main loop runs until a keyboard break is invoked. One can easily modify it, or simply use the library functions, as per convenience. Since I myself was programming in GPIB for the first time, I have put many comments here and there for quick understanding. 

* Notes

1. The code does perform some simple checks to prevent the user from supplying wrong/out-of-range parameters but there is certainly a scope for improvement there.  
