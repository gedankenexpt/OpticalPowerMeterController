######################################################################################
######### Python code to control the optical powermeter 1830-C from Newport  #########
################### via the GPIB-USB controller from Prologix. #######################
######################################################################################
################# Consult the user manuals 1830-R_Manual_RevA.pdf #################### 
################## and PrologixGpibUsbManual-6.0.pdf for more info ################### 
######################################################################################

import sys
import numpy as np
import math
import serial
import time

####################################################################################
  ######################### ESSENTIAL LIBRARY FUNCTIONS ##########################
####################################################################################

#l is wavelength (nm), u is units of measurement (W=1, dB=2, dBm=3, Rel=4), a is attenuator off (0) or on (1)
def setPM(l,u,a):
	if ((l > 1000) or (l < 780)):
		print 'Valid wavelength range is from 780 to 999 nm, Defaulting to 780 nm now.'
		l = 780
	if ((u > 4) or (u < 1)):
		print 'Valid unit range is 1 to 4 with Watt=1, dB=2, dBm=3, Rel=4. Defaulting to Watt now.'
		u = 1
	if (a > 1):
		print 'Valid attenuator setting is on (1) or off (0). Setting off now.'
		a = 0

	ser.write("++auto 0\n")
	ser.write("W"+str(l)+"\n")
	ser.write("U"+str(u)+"\n")
	ser.write("A"+str(a)+"\n")

def readPM(d):
	time.sleep(d)
	rdn = 0
	mav = 0
	mask = 128 #bit position 7 indicating READ_DONE in status byte register (SBR)
	mask2 = 16 #bit position 4 indicating MESSAGE_AVAILABLE in SBR

	ss = 0
	ser.write("++auto 0\n")
	ser.write("C\n") #The command C clears the SBR which may be needed before reading

	while (ss & mask != mask):
		ser.write("++spoll\n")
		ser.write("++auto 1\n")
		rdn = ser.readline()
		if (len(rdn) > 0):
			ss=int(float(rdn))

		if (ss & mask == mask):
			break

	ser.write("++auto 0\n")
	ser.write("D?\n")
	
	ss = 0	
	while (ss & mask2 != mask2):
		ser.write("++spoll\n")
		ser.write("++auto 1\n")
		mav = ser.readline()		
		if (len(mav) > 0):
			ss=int(float(mav))

		if (ss & mask2 == mask2):
			break

	ser.write("++auto 1\n")
	rsp = ser.readline()
	ser.write("++auto 0\n")
	if len(rsp) > 0:
		return rsp

def queryPM(self,comm):
	mask2 = 16 #bit position 4 indicating MESSAGE_AVAILABLE in SBR
	ss = 0
	mav = 0

	ser.write("++auto 0\n")
	ser.write(comm+"\n")

	while (ss & mask2 != mask2):
		ser.write("++spoll\n")
		ser.write("++auto 1\n")
		mav = ser.readline()
		if (len(mav) > 0):
			ss=int(float(mav)) 

		if (ss & mask2 == mask2):
			break

	ser.write("++auto 1\n")
	rsp = ser.readline()
	ser.write("++auto 0\n")
	if len(rsp) > 0:
		print 'command response = ', rsp


####################################################################################
########################### INITIALIZATION & MAIN LOOP #############################
####################################################################################

pi=math.pi

#number of power measurements to later evaluate the fluctuations
nPowMsmnts = 5 #choose higher value to get a better average powers
timeDelPowMet=2 #time delay between succsessive calls to read the powermeter (in secs).

######## Initializing and setting of the powermeter (check 1830-R_Manual_RevA.pdf for more) ########
lSFG=790 #wavelength in nm. 
uMeas=1 #for measurements in Watt scale
att=0 #built-in attenuator off

powNew=[]
pow0=[]

comport = "COM5" #If using linux, this would be something like /dev/ttyUSB0 
addr = 4 #Check the instrument rear panel and pg 52 of 1830-R_Manual_RevA for the address and baud rate settings
ser = serial.Serial(comport,9600,timeout=10)

ser.write("++mode 1\n")
ser.write("++addr " + str(addr) + "\n")
#++auto 0 addresses the instrument to LISTEN (read-after-write is disabled) and ++auto 1 addresses the instrument to TALK
ser.write("++auto 0\n")
#Commands and queries sent to the 1830-R-GPIB through the GPIB bus should be terminated by sending an <NL><EOI> (<NL> is new line). 
ser.write("++eoi 1\n")
#eos 3: Do not append anything to instrument commands	
ser.write("++eos 3\n")

#Set the wavelength, units, and attenuator. Can be put inside the loop if one or more of these parameters may need to be changed dynamically. 
setPM(lSFG,uMeas,att)
i = 0

while True:
        try:                
                print '\n Power measurement in round ', i+1
                j = 0
                while j < nPowMsmnts:
			powrd=str(readPM(timeDelPowMet)).rstrip()
			#print powrd
			pow0.append(float(powrd))
			j = j + 1

                powNew.append(np.mean(pow0))#,dtype=np.float64				
                i = i + 1

        except serial.SerialException:
                print '\n COMPORT ERROR HANDLED \n'
                continue

        except KeyboardInterrupt:
                print '\nPausing...\n 1. Continue \n 2. Exit \n'
                try:
                        response = raw_input()
                        if response == '1':
				print 'Resuming now... '
				continue
                        elif response == '2':
				fname1 = "powerList.txt"
				f1 = open(fname1,"w") 
				f1.write("PowNew \n")
				j=0
				while j < i:
					f1.write('%10.5f \n' %(powNew[j]))
					j=j+1

				f1.close() #close the file
				ser.close() #close the serial port
				break

                except KeyboardInterrupt:
                        print 'Resuming...'
                        continue

        except :
                print '\n UNKNOWN ERROR HANDLED \n'
                ser.close()
                break
