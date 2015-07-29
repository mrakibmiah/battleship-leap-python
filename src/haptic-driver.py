import serial


class Haptic(object):
    serial = None
	def __init__(self, port):
		try:
			self.serial = serial.Serial(port, 9600, timeout=1)
			self.serial.close()
			self.serial.open()
		except serial.SerialException:
			print("ERROR in Serial Init")

	#	Pulse: Pulses the vibrator one time with intensity between 1-10 and duration represented in milisec.  
	def pulse(self, int, time)
		self.serial.write('p%d%d' %(int, time))
	
	#	Set: Set the intensity of the vibrator 0-10 where 0 is off.
	def set(self, int)
		self.serial.write('s%d' %int)
	#	If ther is an error during init, try and change port using this function.	
	def setPort(self, port)
		try:
			self.serial = serial.Serial(port, 9600, timeout=1)
			self.serial.close()
			self.serial.open()
		except serial.SerialException:
			print("ERROR in Serial Init")