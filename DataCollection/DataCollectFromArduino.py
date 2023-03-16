import serial

serialCOMport = 'COM5'
arduinoBoard = serial.Serial(serialCOMport, 9600)


def getSensorData():
    sensorsReadingFromArduino = arduinoBoard.readline().decode('utf-8')
    return sensorsReadingFromArduino

