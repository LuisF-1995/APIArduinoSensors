import json
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import DataCollection.DataCollectFromArduino
from typing import Dict, List, Union
from pydantic import BaseModel
import uvicorn


app = FastAPI()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True, workers=1)


RootPageHtml = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DragonFlyAPI</title>
</head>
<body>
    <h1>DragonFly API </h1>
    <main>
        <section>
            <h3>Metodos GET:</h3>
            <p>Para usar la API, hay 2 endpoint con los siguientes metodos get:</p>
            <p>1. El home (/): Donde estás ubicado y vas a encontrar información de la API.</p>
            <p>2. /getSensorData: Endpoint para la adquisicion de las medidas. Devuelve un archivo JSON con todas las mediciones tomadas al instante de la solicitud</p>
            <p>3. /getStreamSensorData: Endpoint para visualizar los datos de la API en tiempo real con un muestreo de 1 segundo, predefinido en la programacion del arduino</p>
            <p>3. /getSensorDataFromArduino: Endpoint para visualizar los datos enviados a la API directamente desde el arduino</p>
        </section>
        <section>
            <h3>Metodos POST:</h3>
            <p>Hay un metodo POST, que usará directamente el arduino cuando esté conectado a la API, y enviando datos;
             éste metodo recibirá un archivo JSON con todas las medidas tomadas por los sensores.<br>
             
             Éste metodo POST usará el endpoint /postSensorData.
             </p>
        </section>
    </main>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(RootPageHtml)

@app.get("/getSensorData")
async def getSensorData():
    while True:
        try:
            sensorData = DataCollection.DataCollectFromArduino.getSensorData()
            return json.loads(sensorData)
        except:
            return {"ComunicationError": "No hay conexión del PC con la placa de arduino en el puerto COM5"}


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>DragonFly API</title>
    </head>
    <body>
        <h1>DragonFly API</h1>
        <div id='messages'>
        </div>
        <script>
            var ws = new WebSocket("ws://localhost:80/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                messages.innerHTML = `${event.data}`
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/getStreamSensorData")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = DataCollection.DataCollectFromArduino.getSensorData()
            await websocket.send_text(data)
        except:
            await websocket.send_text('{"ComunicationError": "No hay conexión del PC con la placa de arduino en el puerto COM5"}')


class SensorDHT11Data(BaseModel):
    PorcentajeHumedadAmbiente: float
    TemperaturaAmbienteCelsius: float
    TemperaturaAmbienteFahrenheit: float
    ÍndiceCalor: str

class JsonSensorData(BaseModel):
    SensorDHT11: SensorDHT11Data
    HumedadSueloAnalogaSensor: int
    PorcentajeHumedadSuelo: float
    LuminosidadAnalogaSensor: int
    PorcentajeLuminosidad: float
    SampleDateTime: str


sensorDataPosted = {"informationStatus": "Arduino aun no ha enviado información"}

@app.post("/postSensorData")
async def postSensorData(sensorData: JsonSensorData):
    global sensorDataPosted
    serverResponse = {"message": "Carga exitosa",
                      "status": "OK",
                      "data": sensorData}
    sensorDataPosted = serverResponse
    return serverResponse

@app.get("/getSensorDataFromArduino")
async def getDataFromArduino():
    return sensorDataPosted
