import imcntr as cntr
import serial

def print_response(data):
    print(f"<< {str(data)}")

def print_task(data):
    print(f">> {str(data)}")

if __name__ == '__main__':
    #port = input("Port: ")
    port = "/dev/ttyACM0"
    """serial_connection = serial.Serial(port)
    print(serial_connection.is_open)
    serial_connection.close()"""
    connection = cntr.DeviceConnection(port)
    connection.send_callback = print_task
    connection.receive_callback = print_response
    print(connection.port)
    connection.connect()
    print(connection.port)
    shutter = cntr.Shutter(connection)
    shutter.open(timeout = 5)
    shutter.close(timeout = 5)
    connection.disconnect()
