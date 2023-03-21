import serial
import sys
from serial import SerialException
import json
import requests

serialCOMport = 'COM5'

def getSensorData():
    try:
        getSensorData.arduinoBoard.isOpen()
    except (NameError, AttributeError):
        getSensorData.arduinoBoard = None

    if not getSensorData.arduinoBoard:
        try:
            getSensorData.arduinoBoard = serial.Serial(serialCOMport, 9600)
            getSensorData.arduinoConnected = True
        except SerialException:
            getSensorData.arduinoConnected = False
            return "Error al comunicarse con la tarjeta arduino en el puerto: ", serialCOMport

    try:
        sensorsReadingFromArduino = getSensorData.arduinoBoard.readline().decode('utf-8')

        jsonSend = json.loads(sensorsReadingFromArduino)
        postUrl = "https://api-dragonfly.fly.dev/postSensorData"
        headers = {'Content-type': 'application/json'}
        response = requests.post(postUrl, json=jsonSend, headers=headers)
        if response.status_code == 200:
            print("Petición exitosa!")
        else:
            print("Error en la petición")

        return sensorsReadingFromArduino
    except serial.SerialException:
        getSensorData.arduinoBoard = None
        print("Error al leer datos de la tarjeta arduino en el puerto: ", serialCOMport, sys.exc_info())
        return "Error al leer datos de la tarjeta arduino en el puerto: ", serialCOMport
