import imcntr as cntr
import serial.tools.list_ports


class Communication(cntr.SerialCommunication):

    def receive(self, message):
        print(f"<< {str(message)}")

    def send(self, message):
        print(f">> {str(message)}")
        super().send(message)


if __name__== '__main__':
        com = Communication()
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        if ports:
            for p in ports:
                print("[", ports.index(p),"] =",p)
        else:
            print("No serial port found!")
            exit(0)
        while True:
            try:
                port = int(input("Port [number]: "))
                if port >= len(ports):
                    print("That's not a valid port!")
                else:
                    break
            except:
                exit(0)
        com.connection = str(ports[int(port)])
        com.connect()
        if com.connected:
            print("connected")
        else:
            print("Connection not possible.")
            exit(0)
        print("Type in 'help' for further information or 'quit' to exit.")
        while True:
            command = input()
            if command == 'quit':
                break
            elif command == 'help':
                print("Controller commands:\n 'move_out'\tmove sample out\n 'move_in'\tmove sample in\n 'rot_cw+[STEP]'\trotate sample clockwise for [STEP]\n 'rot_ccw+[STEP]'\trotate sample counterclockwise for [STEP]\n 'open_shutter'\topen shutter\n 'close_shutter'\tclose shutter\n 'stop_lin'\tstop linear movement\n 'stop_rot'\tstop rotational movement\n 'stop_all'\tstop all movement\n 'exit'\tquit program")
            else:
                com.send(command)
        com.disconnect()
        if not com.connected:
            print("disconnected")
        else:
            print("Quit ungraceful without disconnecting!")
        exit(0)
