import json
from azure.iot.device import IoTHubModuleClient

def save_data_to_file(data):
    try:
        # Open the file in append mode and write the data
        with open("modbus_data.json", "a") as file:
            file.write(data + "\n")
        print("Data saved to file.")
    except Exception as ex:
        print("Error saving data to file:", ex)

def message_handler(message):
    if message.input_name == "input1":
        data = message.data.decode("utf-8")
        print("Received data from ModbusClientModule:", data)

        # Save data to file
        save_data_to_file(data)

def main():
    # Azure IoT Edge configuration
    iothub_connection_string = "HostName=vmhub.azure-devices.net;DeviceId=myEdgeDevice;SharedAccessKey=E7RyiRP3cqdQs0QTI9Fm7cbHu9z/Lq+Vx4Ft8g9hRIw="
    module_id = "AnalyticModule"

    # Initialize Azure IoT Edge client
    client = IoTHubModuleClient.create_from_connection_string(iothub_connection_string)
    client.connect()

    try:
        # Set the message handler
        client.on_message_received = message_handler

        # Keep the module alive
        while True:
            pass

    except KeyboardInterrupt:
        print("Analytic module stopped by the user.")
    except Exception as ex:
        print("Error:", ex)
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
