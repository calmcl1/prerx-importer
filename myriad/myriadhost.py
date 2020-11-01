import socket


class MyriadHost:
    # self.ip_address, self.port = None

    def __init__(self, ip_address: str, port: int = 6950):
        self.ip_address = ip_address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip_address, self.port))

    def getDataUntilNewLine(self) -> str:
        data = ""
        while data.rfind("\n") == -1:
            data += str(self.socket.recv(1), encoding="ASCII")

        return data

    def recv(self) -> str:
        reply = self.getDataUntilNewLine()
        while ("+Connected" in reply) or ("SET IC CURRENTITEM" in reply):
            reply = self.getDataUntilNewLine()

        return reply

    def send(self, command: str):
        if not command.endswith("\n"):
            command += "\n"

        self.socket.send(bytes(command, encoding="ASCII"))
        response = self.recv()
        if "+Success" in response:
            return True
        elif "+Fail" in response:
            return False
        else:
            return response
