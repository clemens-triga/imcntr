import imcntr as cntr

class Communication(cntr.MessageExchange):

    def receive(self, message):
        print(f"<< {str(message)}")
        super().receive(message)

    def send(self, message):
        print(f">> {str(message)}")
        super().send(message)

if __name__ == '__main__':
    port = input("Port: ")
    with Communication(port) as com:
        controller = cntr.Controller(com,timeout =10)
        shutter = cntr.Shutter(com,timeout = 10)
        controller.ready.wait()
        shutter.open()
        shutter.open.wait()
        shutter.close()
        shutter.close.wait()
