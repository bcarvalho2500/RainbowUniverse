from threading import Thread
import os, random, json

from SocketServer.Objects.Game import Game
from SocketServer.Objects.Lobby import Lobby
from SocketServer.Objects.Player import Player

import SocketServer.socketServer


LOBBY_MAX_SIZE = 5
LOBBY_ID_LENGTH = 8

class Server:
    def __init__(self, port):
        self._port = port
        self._server = None
        self._lobbies = {}
        self._games = []

        self._players = {}

        path = os.path.join(os.path.dirname(os.path.realpath(__file__)).replace(__file__, ""), "..")
        with open(os.path.join(path, "Animals.txt"), "r") as f:
            self._animals = [line[:-1] for line in f.readlines()]

        with open(os.path.join(path, "Adjectives.txt"), "r") as f:
            self._adjectives = [line[:-1] for line in f.readlines()]

    # returns the player object associated with a specific client id
    def _getPlayerFromClientId(self, clientId):
        return self._players.get(clientId, None)

    # returns the player object associated with a specific client
    def _getPlayerFromClient(self, client):
        return self._getPlayerFromClientId(client["id"])

    # generates a unique id for a new lobby
    def _createLobbyId(self):
        while True:
            lobbyId = "".join(random.sample("0123456789ABCDEF", LOBBY_ID_LENGTH))
            if lobbyId not in self._lobbies:
                return lobbyId

    def start(self):
        if self._server is None:
            self._server = SocketServer.socketServer.WebsocketServer(port=self._port, host="localhost")

            self._server.set_fn_new_client(lambda client, server: self._onConnect(client))
            self._server.set_fn_client_left(lambda client, server: self._onDisconnect(client))
            self._server.set_fn_message_received(lambda client, server, message: self._onMessage(client, message))

            Thread(target=self._server.run_forever).start()

    def stop(self):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()

            self.__init__(self._port)

    def _onMessage(self, client, message):
        player = self._getPlayerFromClient(client)
        if player is None:
            response = {"success":False,  "message":"Client is not connected"}
        else:
            messageData = message.split("|")
            response = ({
                "cl_alias":  lambda m: self.setPlayerAlias(player, m),
                "lb_create": lambda m: self.createLobby(player),
                "lb_join":   lambda m: self.joinLobby(player, m),
                "lb_leave":  lambda m: self.leaveLobby(player),
                "lb_kick":   lambda m: self.kickFromLobby(player, self._getPlayerFromClientId(m)),
                "lb_ban":    lambda m: self.banFromLobby(player, self._getPlayerFromClientId(m)),
                "lb_start":  lambda m: self.startMatch(player.inLobby),
                "gm_move":   lambda m: self.madeMove(player, json.loads(m)),
            }).get(messageData[0], lambda m:{"success":False, "message":"Invalid message"})(messageData[1])

        if not response["success"]:
            self._sendPlayerMessage(player, "sv_error|%s" % response["message"])
            return response
        
        return {"success":True}

    def _onConnect(self, client):
        client["id"] = "%s_%d" % ("".join(random.sample("0123456789ABCDEF", 16)), client["id"])
        player = Player(client)
        self._players[client["id"]] = player

        player.alias = "%s %s" % (random.choice(self._adjectives), random.choice(self._animals))

        self._sendPlayerMessage(player, "cl_init|%s:%s" % (player.alias, client["id"]))

        return {"success":True}

    def _onDisconnect(self, client):
        player = self._getPlayerFromClient(client)

        if player is None: return {"success":False, "message":"Player was not connected"}
            
        # remove them from the lobby?
        if player.inGame:
            player.inGame.setLoser(player)
            self.leaveLobby(player)
            self.completeGame(player.inGame)

        # allow them to reconnect to a game?


        del self._players[player.getClientId()]
        
        return {"success":True}

    # sends a player a single message
    def _sendPlayerMessage(self, player, message):
        self._server._unicast_(player.client, message)
        return {"success":True}

    def setPlayerAlias(self, player, alias):
        player.alias = alias

        if player.inLobby is not None:
            self.updateLobby(player.inLobby)

        return {"success":True}

    # a player is attempting to create a new lobby with them as the host
    def createLobby(self, player):

        # if the player is already in a lobby, leave that lobby to make a new one
        if player.inLobby is not None:
            self.leaveLobby(player)

        lobbyId = self._createLobbyId()
        self._lobbies[lobbyId] = Lobby(lobbyId, player)

        # tell the player that the lobby was created and give them the ID of the lobby
        self._sendPlayerMessage(player, "lb_init|%s" % lobbyId)
        self.updateLobby(self._lobbies[lobbyId])

        return {"success":True}

    # a player is trying to join a lobby using the lobby id
    def joinLobby(self, player, lobbyId):

        # check if the lobby exists
        if lobbyId not in self._lobbies: return {"success":False, "message":"Invalid lobby ID"}

        lobby = self._lobbies[lobbyId]
        response = lobby.addPlayer(player)
        if not response["success"]: return response

        self._sendPlayerMessage(player, "lb_joined|")
        self.updateLobby(lobby)
        return {"success":True}

    # a player is trying to leave the lobby they are in
    def leaveLobby(self, player):

        # remove the player from the lobby
        lobby = player.inLobby
        if lobby is not None:
            lobby.removePlayer(player)

            # destroy the lobby if it is empty
            if lobby.isEmpty():
                del self._lobbies[lobby.lobbyId]

            # if it is not emtpy, then a new player was promoted to leader
            # the lobby should be updated for all connected players
            else:
                self.updateLobby(lobby)

        return {"success":True}
        
    # the host is trying to kick a player from the lobby
    def kickFromLobby(self, player, otherPlayer):
        if    player.inLobby is None: response = {"success":False, "message":"You are not in a lobby"}
        elif  otherPlayer    is None: response = {"success":False, "message":"Player is not connected"}
        else:                         response = player.inLobby.kickPlayer(player, otherPlayer)

        if not response["success"]: return response

       # tell the player they were kicked
        self._sendPlayerMessage(otherPlayer, "lb_kicked|") 

        # tell all other clients in the lobby to update the lobby
        self.updateLobby(player.inLobby)

        return {"success":True}

    def banFromLobby(self, player, otherPlayer):
        if    otherPlayer    is None: response = {"success":False, "message":"Player is not connected"}
        elif  player.inLobby is None: response = {"success":False, "message":"You are not in a lobby"}
        else:                         response = player.inLobby.banPlayer(player, otherPlayer)

        if not response["success"]: return response

        # tell the player they were kicked
        self._sendPlayerMessage(otherPlayer, "lb_banned|")

        # tell all other clients in the lobby to update the lobby
        self.updateLobby(player.inLobby)

        return {"success":True}

    def updateLobby(self, lobby):
        lobbyPlayers = ",".join(["%s:%s"%(player.alias, player.getClientId()) for player in lobby.players])
        for lobbyPlayer in lobby:
            self._sendPlayerMessage(lobbyPlayer, "lb_updated|%s" % lobbyPlayers)

    def startMatch(self, lobby):
        if len(lobby.players) < 2:
            return {"success":False, "message":"Can't start a game with only one player!"}

        newGame = Game(lobby.players)
        self._games.append(newGame)

        for player in newGame._players:
            playerInfo = {
                "board":newGame.getPlayerBoard(player),
                "color":player.inGame.getPlayerColor(player),
                "turn":newGame.getCurrentTurn()
            }

            self._sendPlayerMessage(player, "gm_started|%s" % json.dumps(playerInfo))

        return {"success":True}

    def madeMove(self, player, move):
        currentGame = player.inGame
        if currentGame == None: return {"success":False, "message":"You are not playing a game"}

        response = currentGame.makeMove(player, move)
        if not response["success"]: return response

        if currentGame.getWinner() != None:
            return self.completeGame(currentGame)

        for player in currentGame._players:
            playerInfo = {
                "board":currentGame.getPlayerBoard(player),
                "turn":currentGame.getCurrentTurn(),
                "color":currentGame.getPlayerColor(player),
            }
            self._sendPlayerMessage(player, "gm_updated|%s" % json.dumps(playerInfo))

        return {"success":True}

    def completeGame(self, game):
        for player in game._players:
            player.inGame = None
            self._sendPlayerMessage(player, "gm_ended|%s" % game.getWinner())
        self._games.remove(game)

        return {"success":True}


    # print info about players currently connected
    def listPlayers(self):
        print("Showing %d players" % len(self._players))
        for clientId, player in self._players.items():
            print(" --------- %s --------- " % (clientId))
            print(" In Game: %s" % str(player.inGame))
            print(" Alias:   %s" % player.alias)
            print("")

    # print info about lobbies that are created
    def listLobbies(self):
        print("Showing %d lobbies" % len(self._lobbies))
        for lobbyId, lobby in self._lobbies.items():
            print(" --------- %s --------- " % (lobbyId))
            print(" * %s" % lobby.players[0].client["id"])
            for player in lobby.players[1:]:
                print("   %s" % player.client["id"])
            print(" In Game:   %s" % str(lobby.inGame))
            print(" Searching: %s" % str(lobby.searching))
