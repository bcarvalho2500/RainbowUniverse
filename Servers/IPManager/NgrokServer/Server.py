import os, subprocess, requests

class Server:
    def __init__(self, configName):
        self._ngrokLocation = os.path.dirname(os.path.realpath(__file__)).replace(__file__, "")
        self._configName = configName
        self._process = None

    def start(self):
        startCommand = "%s start --config=%s --all" % (os.path.join(self._ngrokLocation, "ngrok.exe"), os.path.join(self._ngrokLocation, self._configName))
        self._process = subprocess.Popen(startCommand, shell=True, stdout=subprocess.PIPE)

    def stop(self):
        if self._process is None: return {"success":False, "message":"Process is not started"}
        self._process.terminate()

    def getTunnels(self):
        if self._process is None: return {"success":False, "message":"Process is not started"}

        try: response = requests.get("http://127.0.0.1:4040/api/tunnels")
        except: return {"success":False, "message":"Connection Failed"}
        response = response.json()

        return {"success":True, "tunnels":response["tunnels"]}

    # def getOutput(self):
    #     return process.stdout.readline()