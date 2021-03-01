import subprocess, requests, time, traceback
import SocketServer, HTTPServer


class NgrokServer:
    def __init__(self, command):
        self._startCommand = command
        self._process = None

    def start(self):
        self._process = subprocess.Popen(self._startCommand, shell=True, stdout=subprocess.PIPE)

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






# server = NgrokServer("ngrok start --config=ngrok.yml --all")

# server.start()
# time.sleep(2)
# server.getTunnels()
# time.sleep(4)
# server.stop()




server = SocketServer.Server()
server.start()

while True:
    try:
        userInput = input()

        # stops the server
        if userInput == "quit":
            server.stop()
            break

        # restarts the server
        elif userInput == "restart":
            server.stop()
            server.start()

        # prints player information
        elif userInput == "players":
            server.listPlayers()

        # prints lobby information
        elif userInput == "lobbies":
            server.listLobbies()

        # # reloads the server if any code is changed
        # elif userInput == "reload":
        #     server.stop()
        #     reload(Objects)
        #     server = Objects.Server()
        #     server.start()

        else:
            print("Unknown command \"%s\"" % userInput)

    except KeyboardInterrupt:
        server.stop()
        break

    except Exception as e:
        print(" ----------- SERVER EXCEPTION ----------- ")
        print(traceback.format_exc())
        print(" ---------------------------------------- ")








