import random

class Game:
    def __init__(self, players):
        self._players = players
        self._spectators = []
        self._currentTurn = random.randint(0, 1)
        self._winner = None
        self._board = [[" bbb  rrr"[(i+1)*(((i+j)%2) == 0)] for j in range(8)] for i in range(8)]
        if self._currentTurn == 1:
            self._board = self._board[::-1]

    def makeMove(self, player, move):
        playerIndex = self._players.indexOf(player)
        if playerIndex == -1:
            return {"success":False, "message":"You are not part of the game!"}

        if playerIndex != self._currentTurn:
            return {"success":False, "message":"It isnt your turn"}

        pieceIndex = "br".indexOf(self._board[move["from"][0]][move["from"][1]])
        if pieceIndex != playerIndex: return {"success":False, "message":"That is not your piece"}

        if abs(move["from"][0]-move["to"][0]) != 1 or abs(move["from"][1]-move["to"][1]) != 1:
            if abs(move["from"][0]-move["to"][0]) != 2 or abs(move["from"][1]-move["to"][1]) != 2:
                return {"success":False, "message":"Invalid move"}

            # if 

        if self._board[move["to"][0]][move["to"][1]]

        self._board[move["to"][0]][move["to"][1]] = self._board[move["from"][0]][move["from"][1]];
        self._board[move["from"][0]][move["from"][1]] = ' ';

        return {"success":True}

    def setLoser(self, player):
        loser = self._players.indexOf(player)
        if loser > 1: return {"success":False, "message":"Player was not player"}

    def getCurrentTurn(self):
        return self._currentTurn

    def getPlayerBoard(self, playerIndex):
        return self._board if not playerIndex else [r[::-1] for r in self._board[::-1]]

    def getPlayerSide(self, player):
        return self._players.indexOf(player)

    def addSpectator(self, spectator):
        spectator.inGame = self
        self._spectators.push(spectator)

    def removeSpectator(self, spectator):
        spectator.inGame = None
        self.spectator.remove(spectator)

