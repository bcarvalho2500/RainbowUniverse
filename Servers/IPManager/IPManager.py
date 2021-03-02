from IPManager import NgrokServer

class IPManager:
    def __init__(self, live=False):
        self._socketAddr = "ws://127.0.0.1:9995"
        self._socketPort = 9995

        self._httpAddr = "http://127.0.0.1"
        self._httpPort = 80

        if live:
            self.start = self._startNgrok
            self.stop = lambda:None
        else:
            self.start = lambda:None
            self.stop = lambda:None

    def getSocketAddr(self):
        return self._socketAddr

    def getHttpAddr(self):
        return self._httpAddr

    def getSocketPort(self):
        return self._socketPort

    def getHttpPort(self):
        return self._httpPort

    def _startNgrok(self):
        ngrokServer = NgrokServer.Server("ngrok.yml")
        ngrokServer.start()
        self.stop = ngrokServer.stop

        attempts = 5
        while True:
            response = ngrokServer.getTunnels()
            if response["success"]: break
            attempts -= 1
            time.sleep(1)
        if attempts == 0:
            print("Failed to run ngrok server")
            exit(0)

        for tunnel in response["tunnels"]:
            if tunnel["name"] == "socketServer":
                self._socketPort = int(tunnel["config"]["addr"][tunnel["config"]["addr"].rfind(":")+1:])
                self._socketAddr = tunnel["public_url"].replace("https", "wss")
            elif tunnel["name"] == "httpServer":
                self._httpPort = int(tunnel["config"]["addr"][tunnel["config"]["addr"].rfind(":")+1:])
                self._httpAddr = tunnel["public_url"]