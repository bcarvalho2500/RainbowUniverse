from threading import Thread
import os, random

from Objects.Game import Game
from Objects.Lobby import Lobby
from Objects.Player import Player

import websocket_server


LOBBY_MAX_SIZE = 5
LOBBY_ID_LENGTH = 8

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9995


class Server:
    def __init__(self):
        self._server = None
        self._lobbies = {}
        self._games = {}

        self._connections = {}
        self._players = {}

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
            self._server = websocket_server.WebsocketServer(port=SERVER_PORT, host=SERVER_HOST)

            self._server.set_fn_new_client(lambda client, server: self._onConnect(client))
            self._server.set_fn_client_left(lambda client, server: self._onDisconnect(client))
            self._server.set_fn_message_received(lambda client, server, message: self._onMessage(client, message))

            Thread(target=self._server.run_forever).start()

    def stop(self):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()

            self.__init__()

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
            }).get(messageData[0], lambda m:m)(messageData[1])

        if not response["success"]:
            self._sendPlayerMessage(player, "sv_error|%s" % response["message"])
            return response
        
        return {"success":True}

    def _onConnect(self, client):
        client["id"] = "%s_%d" % ("".join(random.sample("0123456789ABCDEF", 16)), client["id"])
        player = Player(client)
        self._players[client["id"]] = player

        with open("Animals.txt") as f:
            animal = random.choice(f.readlines())[:-1]
        with open("Adjectives.txt") as f:
            adjective = random.choice(f.readlines())[:-1]
        alias = "%s %s" % (adjective, animal)

        self._sendPlayerMessage(player, "cl_init|%s:%s" % (alias, client["id"]))

        return {"success":True}

    def _onDisconnect(self, client):
        player = self._getPlayerFromClient(client)
        if player is None: return {"success":False, "message":"Player was not connected"}

        if not player.inGame:
            self.leaveLobby(player)

        # remove them from the lobby?

        # allow them to reconnect to a game?
        
        return {"success":True}

    # sends a player a single message
    def _sendPlayerMessage(self, player, message):
        self._server._unicast_(player.client, message)
        return {"success":True}

    def setPlayerAlias(self, player, alias):
        player.alias = alias

        if player.inLobby is not None:
            for lobbyPlayer in player.inLobby:
                self._sendPlayerMessage(lobbyPlayer, "lb_updated|")

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

        return {"success":True}

    # a player is trying to join a lobby using the lobby id
    def joinLobby(self, player, lobbyId):

        # check if the lobby exists
        if lobbyId not in self._lobbies: return {"success":False, "message":"Invalid lobby ID"}

        lobby = self._lobbies[lobbyId]
        response = lobby.addPlayer(player)
        if not response["success"]: return response

        lobbyPlayers = ",".join(["%s:%s"%(player.alias, player.getClientId()) for player in lobby.players])

        self._sendPlayerMessage(player, "lb_joined|%s" % lobbyPlayers)
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
                for lobbyPlayer in lobby:
                    self._sendPlayerMessage(lobbyPlayer, "lb_updated|")

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
        for lobbyPlayer in player.inLobby:
            self._sendPlayerMessage(lobbyPlayer, "lb_updated|")

        return {"success":True}

    def banFromLobby(self, player, otherPlayer):
        if    otherPlayer    is None: response = {"success":False, "message":"Player is not connected"}
        elif  player.inLobby is None: response = {"success":False, "message":"You are not in a lobby"}
        else:                         response = player.inLobby.banPlayer(player, otherPlayer)

        if not response["success"]: return response

        # tell the player they were kicked
        self._sendPlayerMessage(otherPlayer, "lb_banned|")

        # tell all other clients in the lobby to update the lobby
        for lobbyPlayer in player.inLobby:
            self._sendPlayerMessage(lobbyPlayer, "lb_updated|")

        return {"success":True}

    # print info about players currently connected
    def listPlayers(self):
        print("Showing %d players" % len(self._players))
        for clientId, player in self._players.items():
            print(" --------- %s --------- " % (clientId))
            print(" In Game: %s" % str(player.inGame))
            print(" Alias:   %s" % player.alias)
            if player.inGame:
                print(" Position: x=%d, y=%d" % (player.pos["x"], player.pos["y"]))
                print(" Velocity: x=%d, y=%d" % (player.vel["x"], player.vel["y"]))
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
