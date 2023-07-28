import asyncio
import json
import logging
import os
from azure.iot.device.aio import IoTHubModuleClient

# Logger'ı yapılandırın
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IoT Hub bağlantısı için ModuleClient oluşturun
client = IoTHubModuleClient.create_from_edge_environment()

# Yeni klasör adını tanımlayın
output_folder = "output_data_folder"

# Set the message handler
async def message_handler(message):
    try:
        data = json.loads(message.data.decode("utf-8"))
        logger.info("Received data from ModbusClientModule: %s", data)

        # Konsola veriyi yazdır
        print("Received data from ModbusClientModule:", data)

        # Yeni klasörü oluşturun
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Dosyanın tam yolunu belirleyin
        file_path = os.path.join(output_folder, "output_data.json")

        # Veriyi yeni dosyaya kaydedin
        with open(file_path, "w") as file:
            file.write(json.dumps(data))

        # Mesajı IoT Hub'a gönder
        response = await client.send_message_to_output(json.dumps(data), "output1")
        logger.info("Message sent to IoT Hub. response: %s", response)

    except Exception as ex:
        logger.error("Error while processing the message: %s", ex)

async def main():
    try:
        # Connect to IoT Edge
        await client.connect()

        logger.info("Analytic module connected to IoT Edge.")

        # Set the message handler
        client.on_message_received = message_handler

        # Keep the module alive
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Analytic module stopped by the user.")
    except Exception as ex:
        logger.error("Error: %s", ex)

if __name__ == "__main__":
    asyncio.run(main())
