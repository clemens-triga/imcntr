import imcntr as cntr
import serial

def print_response(data):
    print(f"<< {str(data)}")

def print_task(data):
    print(f">> {str(data)}")

if __name__ == '__main__':
    port = input("Port: ")
    with cntr.DeviceConntection(port) as connection:
        connection.send_callback = print_task
        connection.receive_callback = print_response
        connection.connect()
        shutter = cntr.Shutter(connection)
        shutter.open(timeout = 5)
        shutter.close(timeout = 5)
