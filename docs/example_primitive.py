import imcntr as cntr

class Communication(cntr.SerialCommunication):

    def receive(self, message):
        print(f"<< {str(message)}")

    def send(self, message):
        print(f">> {str(message)}")
        super().send(message)

if __name__ == '__main__':
    port = input("Port: ")
    with Communication(port) as com:
        while True:
            command = input()
            com.send(command)
            if command == 'exit':
                break
    exit(0)
