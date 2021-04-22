import subprocess, requests, time, traceback
import SocketServer, WebServer
from IPManager import IPManager


ipManager = IPManager(live=False)
ipManager.start()
print("Website hosted at :", ipManager.getHttpAddr())
print(ipManager.getSocketAddr())

socketServer = SocketServer.Server(ipManager.getSocketPort())
socketServer.start()

WebServer.Server.addRouter("home.html", lambda route, content: content.replace("{{SOCKET_SERVER_ADDR}}", ipManager.getSocketAddr()))
WebServer.Server.landingPage = "home.html"
httpServer = WebServer.Server(ipManager.getHttpPort())
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
        ipManager.stop()
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

