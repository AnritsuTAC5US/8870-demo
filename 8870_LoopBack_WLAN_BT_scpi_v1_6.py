#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  8870_LoopBack_WLAN_BT_scpi_v1_6.py
#  
#  Copyright 2015 Sagar Chandawale <sagar.chandawale@anritsu.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#   

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This (self-guided) script is for demonstration purposes only		#
# Description: Continuous Packet Transmission from the VSG			#
# and then loops back to the VSA to perform measurements on the 	#
# received packets for both WLAN & Bluetooth using TCP/IP interface	#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Running Instructions:													#
#																		#
# Interactive:															#
#>python file_name.py													#
# Non-Interactive:														#
#>python file_name.py arg1 arg2 arg3 arg4 arg5 arg6 arg7 arg8 arg9 arg10#
#																		#
#		arg1 -> IP Address e.g. 192.168.1.10							#
#		arg2 -> Socket Port# e.g. 56001									#
#		arg3 -> WLAN or BT e.g. 1 or 2									#
#		arg4 -> RF Mode (Normal or RF Semaphore) e.g. 1 or 2			#
#		arg5 -> Full Calibration ON or OFF e.g. 1 or 0					#
#		arg6 -> Band Calibration ON or OFF e.g. 1 or 0					#
#		arg7 -> Path Loss Load ON or OFF e.g. 1 or 0					#
#		arg8 -> RF Input Test Port# e.g. 1 or 2 or 3 or 4 (restricted)	#
#		arg9 -> RF Output Test Port# e.g. 1 or 2 or 3 or 4 (restricted)	#
#		arg10 -> No. of Test Loops e.g. 10								#
#																		#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import socket
import csv
import time
import os
import sys

start_time = time.time()

class MT8870A(object):
	
	def __init__(self, socketInst, SRWtype, RFModeType):
		# initialize socket instance and SRW type
		self.s = socketInst
		self.SRWstd = SRWtype
		self.RFMode = RFModeType
		
	def ConnectMT8870A(self):
		if(len(sys.argv) >= 2):
			specifiedIP = sys.argv[1]
			HOST = specifiedIP
		else:
			print "No IP address issued in argument, using default IP address 192.168.1.1"
			HOST = "192.168.1.1"    # MT8870A TRX module IP address
			
		if(len(sys.argv) >= 3):
			specifiedPORT = int(sys.argv[2])
			PORT = specifiedPORT
		else:
			print "No Socket Port# issued in argument, using default Socket Port# 56001"
			PORT = 56001            # MT8870A TRX module Raw socket Port No.
			
		ret = -1
		while (ret != 0):
			ret = os.system("ping -n 1 " + HOST + " | find \"TTL=\"")
			if ret == 0:
				if (self.s.connect((HOST, PORT)) == 0):
					print 'Connection Error!' + " Socket Address: " 
					+ HOST + '@' + str(PORT)
				else:
					print '\nConnecting to [IP Address: ' + HOST + '] [Raw Socket Port: ' + str(PORT) + ']'
					print 'Connected to MT8870A, now sending commands...\n'
			else:
				print "Error Code :" + str(ret)
				print "HOST IP '" + HOST + "' Not Found.\n"
				HOST = raw_input("Enter new valid IP address: ") 
	
	def SetRFParameters(self):
		# common frequency & power values for all wireless standards
		self.Frequency = '2412000000'
		self.PowerLevel = '-25'
		# hard-coded default waveforms names
		if self.SRWstd == 1: self.Waveform = "'MV887030A_n_MCS7_20_1024L'"
		elif self.SRWstd == 2: self.Waveform = "'MV887040A_BLE'"
		
	def InitializeMT8870A(self):
		#standards MT8870A initialization sequence
		self.s.sendall('*RST\n')
		self.s.sendall('*IDN?\n')
		data = self.s.recv(1024)
		print 'Instrument ID: ' + str(data)
	
		print 'Instrument Setup...\n'
		
		self.s.sendall('SYST:LANG?\n')
		data = self.s.recv(1024)
		#print repr(data)
		if str(data) != "SCPI\r\n":
			self.s.sendall('SYST:LANG SCPI\n')
			
		self.s.sendall('INST?\n')
		data = self.s.recv(1024)
		#print repr(data)
		if str(data) != "SRW\r\n":			
			self.s.sendall('INST SRW\n')
			
		self.s.sendall('*RST\n')
		
		if self.RFMode == 1:
				self.s.sendall('SYST:RF:MODE NORMAL\n')
		elif self.RFMode == 2:
				self.s.sendall('SYST:RF:MODE RFSEMAPHORE\n')
				self.s.sendall('SYST:RF:PORT NONFIXED\n')
				self.s.sendall('SYST:RF:UNLOCK\n')
				#self.s.sendall('SYST:RF:LOCK:COMB NON\n')
					
		self.s.sendall('SYST:RF:MODE?\n')
		data = self.s.recv(1024)
		print 'Confirm RF Mode Selected: ' + data + '\n'
		self.inPort = 0
		self.outPort = 0
		
		if(len(sys.argv) >= 10):
			if (int(sys.argv[8]) >= 1) and (int(sys.argv[9]) >= 1):
				self.inPort = sys.argv[8]
				self.outPort = sys.argv[9]
		else:
			while (int(self.inPort) == int(self.outPort)):
				while ((int(self.inPort) > 4) or (int(self.inPort) < 1)):
					self.inPort = raw_input("Enter VSA RF Test Port <1,2,3,4>: ")
					if ((int(self.inPort) > 4) or (int(self.inPort) < 1)): 
						print "\nInvalid Port!\n"
				while ((int(self.outPort) > 4) or (int(self.outPort) < 1)):
					self.outPort = raw_input("\nEnter VSG RF Test Port <1,2,3,4>: ")
					if ((int(self.outPort) > 4) or (int(self.outPort) < 1)): 
						print "\nInvalid Port!\n"
				if (int(self.inPort) > 2):
					if (int(self.inPort) == int(self.outPort)):
						print "\n** VSA & VSG cannot share Port 3 or Port 4 **\n"
						print "Check RF Connections and Try again"
						exit()
				else:
						break
	
	def BandCalibration(self):
		
		if self.RFMode == 2:
			self.s.sendall('SYST:RF:STAT?\n')
			data = self.s.recv(1024)
			while int(data) != 0:
				print "Waiting for release...\n"
			self.s.sendall('SYST:RF:LOCK\n')

		print 'Running Band Calibration...\n'
		self.s.sendall('CALC:CAL:BAND:STAR:TEMP 2.0\n')
		self.s.sendall('CALC:CAL:BAND:RES?\n')
		data = self.s.recv(1024)
		if 'P' in data: print str(data)
		
		if self.RFMode == 2:
			self.s.sendall('SYST:RF:UNLOCK\n')
	
	def FullCalibration(self):
		
		if self.RFMode == 2:
			self.s.sendall('SYST:RF:STAT?\n')
			data = self.s.recv(1024)
			while int(data) != 0:
				print "Waiting for release...\n"
			self.s.sendall('SYST:RF:LOCK\n')
				
		print 'Running Full Calibration...\n'
		self.s.sendall('CALC:CAL:FULL:STAR\n')
		self.s.sendall('CALC:CAL:FULL:RES?\n')
		data = self.s.recv(1024)
		if 'P' in data: print str(data)
		
		if self.RFMode == 2:
			self.s.sendall('SYST:RF:UNLOCK\n')
		
	def LoadMT8870APathLoss(self):
		# Load Path Loss data from CSV file in MT8870A format to Table#1
		if self.RFMode == 2:
			self.s.sendall('SYST:RF:STAT?\n')
			data = self.s.recv(1024)
			while int(data) != 0:
				print "Waiting for release...\n"
			self.s.sendall('SYST:RF:LOCK\n')
		
		self.s.sendall('CALC:EXTL:TABL:DEL\n')
		self.s.sendall('ROUT:EXTL:TABL:SWIT ON\n')
		self.s.sendall('CALC:EXTL:TABL:SETT 1\n')
		
		Path_Loss_File = '8870_PathLossTable_1.csv'
		with open(Path_Loss_File, 'rb') as path_loss_test_file:
			path_loss_csv_reader = csv.reader(path_loss_test_file, delimiter = ',')
			import pdb; pdb.set_trace()
			data = list(path_loss_csv_reader)
			
			row_count = sum(1 for row in data)
			print "Number of path loss frequency entries : " + str(row_count - 1)
			print '\nLoading Path Loss Data from ' + Path_Loss_File + '...\n'
			for i in range(1, (row_count)):
				self.s.sendall("CALC:EXTL:TABL:VAL:ALL " + str(data[i][0]) + "MHZ"
												+ "," + str(data[i][1])
												+ "," + str(data[i][2])
												+ "," + str(data[i][3])
												+ "," + str(data[i][4])
												+ "," + str(data[i][5])
												+ "," + str(data[i][6])
												+ "," + str(data[i][7])
												+ "," + str(data[i][8]) + "\n")
		
		self.s.sendall('CALC:EXTL:TABL:COUN? 1\n')
		loaded_path_loss_count_query = int(self.s.recv(1024))
		
		if loaded_path_loss_count_query == (row_count-1):						
			print "Path Loss Table Load Successful"
		else:
			print "Path Loss Table Load NOT Successful"
		
		if self.RFMode == 2:
			self.s.sendall('SYST:RF:UNLOCK\n')
				
	def VSGSetup(self):
		# Standard VSG Sequence for sending continuous packets
		print 'Initializing VSG\n'
		self.s.sendall('ROUT:PORT:CONN:DIR PORT'+self.inPort+',PORT'+self.outPort+'\n')
		self.s.sendall('SOUR:GPRF:GEN:MODE NORMAL\n')
		self.s.sendall('SOUR:GPRF:GEN:BBM ARB \n')
		
		
		if self.RFMode == 2:
			self.s.sendall('SYST:RF:STAT?\n')
			data = self.s.recv(1024)
			while int(data) != 0:
				print "Waiting for release...\n"
			self.s.sendall('SYST:RF:LOCK\n')
		
		print 'Loading waveform '+self.Waveform+'...\n'
		self.s.sendall("SOUR:GPRF:GEN:ARB:FILE:LOAD "+self.Waveform+"\n")
		self.s.sendall('*WAI\n')
		self.s.sendall('SOUR:GPRF:GEN:ARB:FILE:LOAD? '+self.Waveform+'\n')
		data = self.s.recv(1024)
		if '0' in data: print "Waveform Loaded!\n"
		else: print "Waveform " + self.Waveform + " NOT FOUND!\nCheck MT8870A waveform name and Try again"; exit()
		
		
		self.s.sendall('SOUR:GPRF:GEN:RFS:LEV -100\n')
		
		self.s.sendall("SOUR:GPRF:GEN:ARB:WAV:PATT:SEL "+self.Waveform+",1,1\n")
		self.s.sendall('*WAI\n')
		
		print 'Configuring VSG on Port'+self.outPort+'...\n'
		self.s.sendall('SOUR:GPRF:GEN:RFS:FREQ '+self.Frequency+'\n')
		self.s.sendall('SOUR:GPRF:GEN:RFS:LEV '+self.PowerLevel+'\n')
		
		if self.RFMode == 2:
			self.s.sendall('SYST:RF:UNLOCK\n')
		
	def VSASetup(self):
		# Standards VSA sequence based on selected wireless standard
		if self.SRWstd == 1:
			print 'Configuring VSA on Port'+self.inPort+'...\n'
			self.s.sendall('CONF:SRW:SEGM:CLE\n')
			self.s.sendall('CONF:SRW:SEGM:APP AUTOOFDM\n')
			self.s.sendall('CONF:SRW:TRIG IMMEDIATE\n')
			self.s.sendall('CONF:SRW:PACK 10\n')
			self.s.sendall('CONF:SRW:OFDM:CEST FULLPACKET\n')
			self.s.sendall('CONF:SRW:SEL:WLAN:POW ON\n')
			self.s.sendall('CONF:SRW:SEL:WLAN:EVM ON\n')
			self.s.sendall('CONF:SRW:SEL:WLAN:SPEC:NUM ON\n')
			self.s.sendall('CONF:SRW:ALEV:TIME 0.005\n')
			self.s.sendall('CONF:SRW:FREQ '+self.Frequency+'\n')
		elif self.SRWstd == 2:
			print 'Start VSA on Port'+self.inPort+'...\n'
			self.s.sendall('CONF:SRW:SEGM:CLE\n')
			self.s.sendall('CONF:SRW:SEGM:APP AUTOBT\n')
			self.s.sendall('CONF:SRW:TRIG IMMEDIATE\n')
			self.s.sendall('CONF:SRW:PACK 10\n')
			self.s.sendall('CONF:SRW:BT:MODE SPEED\n')
			self.s.sendall('CONF:SRW:SEL:BLE:CDR ON\n')
			self.s.sendall('CONF:SRW:SEL:BLE:POW ON\n')
			self.s.sendall('CONF:SRW:SEL:BLE:MOD ON\n')
			self.s.sendall('CONF:SRW:ALEV:TIME 0.005\n')
			self.s.sendall('CONF:SRW:FREQ '+self.Frequency+'\n')		
	
	def MeasureAndLog(self):
		Log_File = '8870_ResultLog.csv'
		with open(Log_File, 'wb') as log_test_file:
			csv_writer = csv.writer(log_test_file)
			if self.SRWstd == 1: 
				csv_writer.writerow(['Power avg (dBm)', 
				'EVM (dB)', 
				'SPECTRAL MASK (PASS/FAIL = 1/0)'])
			elif self.SRWstd == 2:
				csv_writer.writerow(['Power avg (dBm)', 
				'Modulation deltaf2 avg (Hz)', 
				'Frequency Drift avg (Hz)'])
		
		# Loop setup to run analysis multiple times (repeatability test)
		if(len(sys.argv) >= 11):
			if(int(sys.argv[10]) >= 1):
				Loops = int(sys.argv[10])
		else:
			Loops = int(raw_input("Enter number of test runs: "))
			
		for x in range(1, (Loops+1)):
			print '\n********************Test Run %d********************\n' % (x)
			self.s.sendall('*WAI\n')
			
			if self.RFMode == 2:
				self.s.sendall('SYST:RF:STAT?\n')
				data = self.s.recv(1024)
				while int(data) != 0:
					print "Waiting for release...\n"
				self.s.sendall('SYST:RF:LOCK\n')
			
			# VSG ON
			self.s.sendall('SOUR:GPRF:GEN:STAT ON\n')
			
			self.s.sendall('INIT:SRW:ALEV\n')
			self.s.sendall('*WAI\n')
			self.s.sendall('CONF:SRW:POW?\n')
			data = self.s.recv(1024)
			print '\nAuto Detected Power Measured: ', str(data)
			self.s.sendall('INIT:SRW\n')
			self.s.sendall('*WAI\n')
			data = 0
			while data == 0:
				self.s.sendall('STAT:SRW:MEAS?\n')
				data = int(self.s.recv(1024))
				
			# VSG OFF
			self.s.sendall('SOUR:GPRF:GEN:STAT OFF\n')
			
			if self.RFMode == 2:
				self.s.sendall('SYST:RF:UNLOCK\n')
				
			print 'Packet Identified as: '
			self.s.sendall('FETC:SRW:SEGM:IDEN? 1, 0\n')
			iden1 = self.s.recv(1024)
			print str(iden1)
			self.s.sendall('FETC:SRW:CINF?\n')
			segment = self.s.recv(1024)
			seg_list = segment.split(",")
			print "Received Packet Count = " + str(seg_list[6])
			if self.SRWstd == 1:
				#print 'Power Measurement: '
				self.s.sendall('FETC:SRW:SUMM:WLAN:POW? 1,1\n')
				data1 = self.s.recv(1024)
				#print str(data1)
				list1 = data1.split(",")
				print "Avg. Power (dBm) = " + str(list1[6])
				#print 'EVM Measurement: '
				self.s.sendall('FETC:SRW:SUMM:WLAN:OFDM:EVM? 1\n')
				data2 = self.s.recv(1024)
				#print str(data2)
				list2 = data2.split(",")
				print "Avg. EVM (dB) = " + str(list2[8])
				#print 'Spectral Mask: '
				self.s.sendall('FETC:SRW:SUMM:WLAN:SPEC:NUM? 1,1\n')
				data3 = self.s.recv(1024)
				#print str(data3)
				list3 = data3.split(",")
				print "Spectral Mask (PASS/FAIL) = " + ("PASS" if list3[42] == 1 else "FAIL")
			elif self.SRWstd == 2:
				#print 'Power Measurement: '
				self.s.sendall('FETC:SRW:SUMM:BLE:POW? 1\n')
				data1 = self.s.recv(1024)
				#print str(data1)
				list1 = data1.split(",")
				print "Power (dBm) = " + str(list1[2])
				#print 'Modulation Measurement: '
				self.s.sendall('FETC:SRW:SUMM:BLE:MOD? 1\n')
				data2 = self.s.recv(1024)
				#print str(data2)
				list2 = data2.split(",")
				print "deltaF2avg (Hz)= " + str(list2[2]) + "\tdeltaF1avg (Hz)= " + str(list2[4])
				#print 'Frequency Drift Measurement (Avg): '
				self.s.sendall('FETC:SRW:SUMM:BLE:CDR? 1\n')
				data3 = self.s.recv(1024)
				#print str(data2)
				list3 = data3.split(",")
				print "Avg Drift (Hz) = " + str(list3[3])
			if (len(list1) < 6):
				print "\n\nNO MEASUREMENT RECORDED!!!\n"
				exit()
			with open(Log_File, 'a') as log_test_file:
				csv_writer = csv.writer(log_test_file)
				if self.SRWstd == 1:
					csv_writer.writerow([list1[6], list2[8], list3[42]])
				elif self.SRWstd == 2:
					csv_writer.writerow([list1[2], list2[2], list3[3]])
						
			time.sleep(0.5)
		 
		print '\n**************************************************\n\n'
		print '\n\nResult Logged in %s...\n\n' % (Log_File)

		self.s.close()
		#print 'Received', repr(data)
		print("--- %s seconds ---" % (time.time() - start_time))
		
def main():

	print '\n\n\t\t\t===MT8870A Loop Back Test===\n\n'
	
	# Wireless Standard Type
	std = 0
	if(len(sys.argv) >= 4):
		if(int(sys.argv[3]) == 1):
			std = 1
			print "(WLAN Standard Selected)\n"
		elif(int(sys.argv[3]) == 2):
			std = 2
			print "(Bluetooth Standard Selected)\n"
	else:
		while ((std < 1) or (std > 2)):
			std = int(raw_input("\nSelect Wireless Standard:\n1. WLAN\n2. Bluetooth\n>> "))
			if std == 1: 
				print "(WLAN Standard Selected)\n"
			elif std == 2: 
				print "(Bluetooth Standard Selected)\n"
			else: 
				print "Invalid option!" 
				print "Script doesn't support other Wireless Standards yet."
				print "Select valid option"
		
	# RF Mode
	semaphore = 0
	if(len(sys.argv) >= 5):
		if(int(sys.argv[4]) == 1):
			semaphore = 1
			print "(Normal Mode Selected)\n"
		elif(int(sys.argv[4]) == 2):
			semaphore = 2
			print "(RF Semaphore Mode Selected)\n"
	else:
		while ((semaphore < 1) or (semaphore > 2)):
			semaphore = int(raw_input("\nSelect MT8870A Mode:\n1. NORMAL\n2. RF Semaphore (Needs Multi-DUT Scheduler License Installed)\n>> "))
			if semaphore == 1: 
				print "(Normal Mode Selected)\n"
			elif semaphore == 2: 
				print "(RF Semaphore Mode Selected)\n"
			else: 
				print "Invalid option!" 
				print "Script doesn't support other Modes."
				print "Select valid option"
					
	# Create Socket Instance
	createSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	# Create 8870 instance
	_8870inst = MT8870A(createSocket, std, semaphore)
	
	# Connect MT8870A
	_8870inst.ConnectMT8870A()
	
	# Initilize MT8870A
	_8870inst.InitializeMT8870A()

	# Full Calibration option
	if(len(sys.argv) >= 6):
		if(int(sys.argv[5]) == 1):
			_8870inst.FullCalibration()
		elif(int(sys.argv[5]) == 0):
			print "Full Calibration Skipped!\n"
	else:
		con = raw_input("\nDo you wish to perform Full Calibration? (Recommended only for the 1st time operation) ")
		if con.lower().startswith("n"): print "Full Calibration Skipped!\n"
		else: _8870inst.FullCalibration()
	
	# Band Calibration option
	if(len(sys.argv) >= 7):
		if(int(sys.argv[6]) == 1):
			_8870inst.BandCalibration()
		elif(int(sys.argv[6]) == 0):
			print "Band Calibration Skipped!\n"
	else:
		con = raw_input("\nDo you wish to perform Band Calibration? ")
		if con.lower().startswith("n"): print "Band Calibration Skipped!\n"
		else: _8870inst.BandCalibration()
		
	# Apply Path Loss to MT8870A
	if(len(sys.argv) >= 8):
		if(int(sys.argv[7]) == 1):
			_8870inst.LoadMT8870APathLoss()
		elif(int(sys.argv[7]) == 0):
			print "Path Loss Load Skipped!\n"
	else:
		con = raw_input("\nDo you wish to load Path Loss Table? ")
		if con.lower().startswith("n"): print "Path Loss Load Skipped!\n"
		else: _8870inst.LoadMT8870APathLoss()
	
	# Set RF Parameters for loopback test
	_8870inst.SetRFParameters()
	
	# Setup VSG for Continuous Packet transmission mode
	_8870inst.VSGSetup()
	
	# Setup VSA based on wireless standard
	_8870inst.VSASetup()
	
	# Measure and Log data in CSV
	_8870inst.MeasureAndLog()
	
	print '\n\n\t\t\t===MT8870A Loop Back Test ENDS===\n\n'
	
	exit()

if (__name__ == "__main__"):
    main()
    
	
