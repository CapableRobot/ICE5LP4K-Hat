EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 2 4
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text Notes 4950 5100 0    60   Italic 0
Thru-Hole Connector
Text GLabel 5500 3500 2    60   Input ~ 0
GPIO23_CDN
Text GLabel 5500 3600 2    60   Input ~ 0
GPIO24_CRS
Text GLabel 5500 3800 2    60   Input ~ 0
GPIO25_SS
$Comp
L power:GND #PWR01
U 1 1 57F6FA86
P 5400 4125
F 0 "#PWR01" H 5400 3875 50  0001 C CNN
F 1 "GND" H 5400 3975 50  0000 C CNN
F 2 "" H 5400 4125 50  0000 C CNN
F 3 "" H 5400 4125 50  0000 C CNN
	1    5400 4125
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR02
U 1 1 57F6FA9C
P 4675 4100
F 0 "#PWR02" H 4675 3850 50  0001 C CNN
F 1 "GND" H 4675 3950 50  0000 C CNN
F 2 "" H 4675 4100 50  0000 C CNN
F 3 "" H 4675 4100 50  0000 C CNN
	1    4675 4100
	1    0    0    -1  
$EndComp
Text GLabel 5500 3900 2    60   Input ~ 0
SPI_CE0
Text GLabel 4000 3700 0    60   Input ~ 0
SPI_MOSI
Text GLabel 4000 3800 0    60   Input ~ 0
SPI_MISO
Text GLabel 4000 3900 0    60   Input ~ 0
SPI_CLK
$Comp
L Connector_Generic:Conn_02x06_Odd_Even J1
U 1 1 60BEA30D
P 5000 3700
F 0 "J1" H 5050 4117 50  0000 C CNN
F 1 "Conn_02x06_Odd_Even" H 5050 4026 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical" H 5000 3700 50  0001 C CNN
F 3 "~" H 5000 3700 50  0001 C CNN
	1    5000 3700
	1    0    0    -1  
$EndComp
Wire Wire Line
	4675 4000 4800 4000
Wire Wire Line
	4000 3900 4800 3900
Wire Wire Line
	4000 3800 4800 3800
Wire Wire Line
	4000 3700 4800 3700
Wire Wire Line
	5300 3900 5500 3900
Wire Wire Line
	5300 3800 5500 3800
Wire Wire Line
	5300 3700 5400 3700
Wire Wire Line
	5300 3600 5500 3600
Wire Wire Line
	5300 3500 5500 3500
$Comp
L power:+3V3 #PWR0109
U 1 1 60BEEDC1
P 4675 3250
F 0 "#PWR0109" H 4675 3100 50  0001 C CNN
F 1 "+3V3" H 4690 3423 50  0000 C CNN
F 2 "" H 4675 3250 50  0001 C CNN
F 3 "" H 4675 3250 50  0001 C CNN
	1    4675 3250
	1    0    0    -1  
$EndComp
Wire Wire Line
	4800 3600 4675 3600
Wire Wire Line
	4675 3600 4675 3250
Wire Wire Line
	5400 3700 5400 4125
Wire Wire Line
	4675 4000 4675 4100
Wire Wire Line
	4000 3500 4800 3500
Text GLabel 4000 3500 0    60   Input ~ 0
GPIO22
Wire Wire Line
	5500 4000 5300 4000
Text GLabel 5500 4000 2    60   Input ~ 0
GPIO07
$EndSCHEMATC
