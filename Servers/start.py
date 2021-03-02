import subprocess, requests, time, traceback
import NgrokServer, SocketServer, WebServer



SOCKET_SERVER_NAME = "socketServer"
HTTP_SERVER_NAME = "httpServer"

SOCKET_SERVER_PORT = 0
HTTP_SERVER_PORT = 0

SOCKET_SERVER_ADDR = ""
HTTP_SERVER_ADDR = ""



ngrokServer = NgrokServer.Server("ngrok.yml")
ngrokServer.start()

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
    if tunnel["name"] == SOCKET_SERVER_NAME:
        SOCKET_SERVER_ADDR = tunnel["public_url"]
        SOCKET_SERVER_PORT = int(tunnel["config"]["addr"][tunnel["config"]["addr"].rfind(":")+1:])
    elif tunnel["name"] == HTTP_SERVER_NAME:
        HTTP_SERVER_ADDR = tunnel["public_url"]
        HTTP_SERVER_PORT = int(tunnel["config"]["addr"][tunnel["config"]["addr"].rfind(":")+1:])


print("Website hosted at :", HTTP_SERVER_ADDR)


socketServer = SocketServer.Server(SOCKET_SERVER_PORT)
socketServer.start()

WebServer.Server.addRouter("home.html", lambda route, content: content.replace("{{SOCKET_SERVER_ADDR}}", SOCKET_SERVER_ADDR.replace("https", "wss")))
httpServer = WebServer.Server(HTTP_SERVER_PORT)
httpServer.start()

while True:
    try:
        userInput = input()
    except KeyboardInterrupt:
        userInput = "quit"
    except Exception as e:
        print(" ----------- SERVER EXCEPTION ----------- ")
        print(traceback.format_exc())
        print(" ---------------------------------------- ")
        continue

    # stops the server
    if userInput == "quit":
        socketServer.stop()
        httpServer.stop()
        ngrokServer.stop()
        break

    # prints player information
    elif userInput == "players":
        socketServer.listPlayers()

    # prints lobby information
    elif userInput == "lobbies":
        socketServer.listLobbies()

    # # restarts the server
    # elif userInput == "restart":
    #     socketServer.stop()
    #     socketServer.start()

    # # reloads the server if any code is changed
    # elif userInput == "reload":
    #     server.stop()
    #     reload(Objects)
    #     server = Objects.Server()
    #     server.start()

    else:
        print("Unknown command \"%s\"" % userInput)

