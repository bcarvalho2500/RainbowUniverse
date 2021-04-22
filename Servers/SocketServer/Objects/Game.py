import random

class Game:
    def __init__(self, players):
        self._players = players
        self._spectators = []
        self._currentTurn = random.randint(0, 1)
        self._board = [[" www  rrr"[(i+1)*((i+j)%2)] for j in range(8)] for i in range(8)]
        if self._currentTurn == 1:
            self._board = self._board[::-1]

    def makeMove(self, player, move):
        playerIndex = self._players.indexOf(player)
        if playerIndex == -1:
            return {"success":False, "message":"You are not part of the game!"}

        if playerIndex != self._currentTurn:
            return {"success":False, "message":"It isnt your turn!"}

        # update the board

        return {"success":True}

    def getCurrentTurn(self):
        return self._currentTurn

    def getPlayerBoard(self, playerIndex):
        return self._board if not playerIndex else self._board[::-1]

    def addSpectator(self, spectator):
        spectator.inGame = self
        self._spectators.push(spectator)

    def removeSpectator(self, spectator):
        spectator.inGame = None
        self.spectator.remove(spectator)

