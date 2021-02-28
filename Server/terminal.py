# from importlib import reload
import traceback
from Objects import Server

server = Server()
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