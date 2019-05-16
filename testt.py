import RPi.GPIO as GPIO
import Adafruit_MCP3008 as ADC
import time
import sqlite3
import datetime
import os
import glob
import RPi.GPIO as GPIO
import math

# Software SPI configuration
CLK  = 20
MISO = 16
MOSI = 12
CS   = 21
mcp = ADC.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

def find_ds18b20():
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

    # find the file that was created through the setup above
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'

    return device_file

def read_temperature_celcius(sensorName):
    f = open(sensorName, 'r')
    lines = f.readlines()
    f.close()
    
    if lines[0].strip()[-3:] != 'YES':
        return None

    temperature_start_pos = lines[1].find('t=')
    
    if temperature_start_pos == -1:
        return None

    temp_string = lines[1][temperature_start_pos+2:]
    print temp_string
    temp_c = float(temp_string) / 1000.0000

    return temp_c


print('| Time Stamp          | Temp  | Battery CS | Battery VS | Peltiers CS | Peltiers VS | Battery (mAh) | Peltiers (mAh) |')

def remove():
    conn=sqlite3.connect('/home/pi/Adafruit_Python_MCP3008/Adafruit_MCP3008/Test.db')
    curs=conn.cursor()
    curs.execute('DELETE FROM Test1')
    conn.commit()
    conn.close()
def send():
    conn=sqlite3.connect('/home/pi/Adafruit_Python_MCP3008/Adafruit_MCP3008/Test.db')
    curs=conn.cursor()
    curs.execute("""INSERT INTO Test1 values(datetime(CURRENT_TIMESTAMP, 'localtime'), (?), (?), (?), (?), (?))""", (values[0],values[1],values[2],values[3],values[4]))
    conn.commit()
    conn.close()
powerBattery=0
powerPeltier=0
values = [0]*7
values[5]=0
values[6]=0
remove()


STEP=1
sensor_name = find_ds18b20()
while True:
    prev_time=time.time()
    values[0] = read_temperature_celcius(sensor_name)
    measurement=values[0]
    # The read_adc function will get the value of the specified channel (0-7).
    p.ChangeDutyCycle(100)
    values[1] = abs(mcp.read_adc(0)*5.0/1023.0-2.5+0.005)/0.1*(mcp.read_adc(0)>514)#/0.1#*0.0517-27.606
    values[2] = mcp.read_adc(1)*1.0
    values[3] = abs(mcp.read_adc(2)*5.0/1023.0-2.5+0.005)/0.1*(mcp.read_adc(2)>514)
    values[4] = mcp.read_adc(3)*5.0/1016
    values[5]=values[0]*values[1]*STEP+values[4]
    values[6]=values[2]*values[3]*STEP+values[5]
    send()
    x=datetime.datetime.now()
    
    print  '|', x.strftime("%Y-%m-%d %H:%M:%S"), '| {0:>5.5} | {1:>10.4} | {2:>10.4} | {3:>11.4} | {4:>11.4} | {5:>13.4} | {6:>14.4} |'.format(*values)

    # Pause for half a second.
    time.sleep(STEP)

   

   

