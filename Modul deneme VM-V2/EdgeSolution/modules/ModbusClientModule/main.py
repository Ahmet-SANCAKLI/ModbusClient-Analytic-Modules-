import asyncio
import json
import os
import time
import logging
from azure.iot.device.aio import IoTHubModuleClient
from pyModbusTCP.client import ModbusClient

# IoT Hub bağlantısı için ModuleClient oluşturun
client = IoTHubModuleClient.create_from_edge_environment()

# Logger'ı yapılandırın
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modbus Sunucu IP adresini ve Port numarasını burada yapılandırın
modbus_server_ip = "185.141.34.129"
modbus_server_port = 1502

# Modbus Sunucu holding register adreslerini burada yapılandırın
timestamp_register = 0    # Örnek olarak zaman damgası için 0. holding register
temperature_register = 1  # Örnek olarak sıcaklık için 1. holding register
humidity_register = 2     # Örnek olarak nem için 2. holding register

async def main():
    try:
        # ModuleClient'ı başlatın
        await client.connect()

        # Modbus Client oluşturun ve Modbus sunucusuna bağlanın
        modbus_client = ModbusClient()
        modbus_client.host = modbus_server_ip
        modbus_client.port = modbus_server_port
        if not modbus_client.open():
            logger.error("Unable to connect Modbus Server!")
            return

        while True:
            try:
                # Holding register adreslerinden verileri alın
                timestamp_data = modbus_client.read_holding_registers(timestamp_register)
                temperature_data = modbus_client.read_holding_registers(temperature_register)
                humidity_data = modbus_client.read_holding_registers(humidity_register)

                # Verileri okuyup, JSON formatında düzenleyin
                if timestamp_data and temperature_data and humidity_data:  # Veriler başarıyla alındıysa
                    timestamp = int(timestamp_data[0])
                    temperature = temperature_data[0] / 100.0
                    humidity = humidity_data[0] / 100.0

                    data = {
                        "timestamp": timestamp,
                        "temperature": temperature,
                        "humidity": humidity
                    }
                    message = {
                        "deviceId": "ModbusClientModule",
                        "data": data,
                        "timestamp": int(time.time())
                    }

                    # Veriyi JSON formatına çevirin
                    message_json = json.dumps(message)

                    # IoT Edge Hub üzerindeki Analytics Modülüne gönderin
                    response = await client.send_message_to_output(message_json, "output1")
                    logger.info("Message has been sent to Analytic Module. response: %s", response)

                    # Log verisini görüntüleyin
                    logger.info("Message sent: %s", message_json)

            except Exception as ex:
                logger.error("Error on Modbus Connection: %s", ex)

            # Mesaj gönderdikten sonra belirli bir süre bekleyin
            await asyncio.sleep(5)  # Örnek olarak 5 saniye bekleyin

    except Exception as ex:
        logger.error("An error occured on Modbus Client Module: %s", ex)

if __name__ == "__main__":
    asyncio.run(main())
