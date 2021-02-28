import json

LOBBY_MAX_SIZE = 10

class Lobby:
    def __init__(self, lobbyId, leader):
        self.players = []
        self.bannedPlayers = []

        self.searching = False
        self.inGame = False
        self.lobbyId = lobbyId

        self.addPlayer(leader)

    # adds a player to this lobby
    def addPlayer(self, player):
        if player in self.bannedPlayers: return {"success":False, "message":"You are banned from joining this lobby"}
        if len(self.players) == LOBBY_MAX_SIZE: return {"success":False, "message":"This lobby is full"}
        if player in self.players: return {"success":False, "message":"You are already in this lobby"}
    
        player.inLobby = self
        self.players.append(player)

        return {"success":True}

    def banPlayer(self, player):
        self.bannedPlayers.append(player)
        return {"success":True}

    # removes a player from this lobby
    def removePlayer(self, player):
        for i in range(len(self.players)):
            if self.players[i] == player:
                self.players[i].inLobby = None
                self.players.pop(i)
                return {"success":True}

        return {"success":False, "message":"Player is not in lobby"}

    # kicks a player from the lobby
    def kickPlayer(self, requestingPlayer, player):
        if not self.isLeader(requestingPlayer): return {"success":False, "message":"Only the lobby leader can kick players"}
        if requestingPlayer == player: return {"success":False, "message":"You can not kick the lobby leader"}
        if player not in self.players: return {"success":False, "message":"Player is not in lobby"}
        if self.inGame: return {"success":False, "message":"You can not kick a player mid-game"}

        # remove the kicked player from the lobby
        self.removePlayer(player)

        return {"success":True}

    # bans a player from the lobby
    def banPlayer(self, requestingPlayer, player):
        if not self.isLeader(requestingPlayer): return {"success":False, "message":"Only the lobby leader can ban players"}
        if requestingPlayer == player: return {"success":False, "message":"You can not ban the lobby leader"}
        if self.inGame: return {"success":False, "message":"You can not ban a player mid-game"}

        # remove the kicked player from the lobby
        self.removePlayer(player)

        # add the player to the ban list so they can not reconnect
        self.bannedPlayers.append(player)

        return {"success":True}

    # returns whether the player is the leader of this lobby
    def isLeader(self, player):
        return self.players[0] == player

    def isEmpty(self):
        return len(self.players) == 0

    def __iter__(self):
        return (player for player in self.players)

    def __contains__(self, player):
        return player in self.players

