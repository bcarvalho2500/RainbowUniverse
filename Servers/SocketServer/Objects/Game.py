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

        if move["from"][0] < 0 or move["from"][0] >= 8: return {"success":False, "message":"Invalid move"}
        if move["from"][1] < 0 or move["from"][1] >= 8: return {"success":False, "message":"Invalid move"}
        if move["to"][0]   < 0 or move["to"][0]   >= 8: return {"success":False, "message":"Invalid move"}
        if move["to"][1]   < 0 or move["to"][1]   >= 8: return {"success":False, "message":"Invalid move"}

        if abs(move["from"][0]-move["to"][0]) != 1 or abs(move["from"][1]-move["to"][1]) != 1:
            if abs(move["from"][0]-move["to"][0]) != 2 or abs(move["from"][1]-move["to"][1]) != 2:
                return {"success":False, "message":"Invalid move"}

            xDir = -1 if move["from"][0]>move["to"][0] else 1;
            yDir = -1 if move["from"][1]>move["to"][1] else 1;

            if self._board[move["from"][0]+xDir][move["from"][1]+yDir] != (not pieceIndex):
                return {"success":False, "message":"Cant capture your own piece"}
            else:
                self._board[move["from"][0]+xDir][move["from"][1]+yDir] = ' '

        self._board[move["to"][0]][move["to"][1]] = self._board[move["from"][0]][move["from"][1]];
        self._board[move["from"][0]][move["from"][1]] = ' ';

        return {"success":True}

    def setLoser(self, player):
        loser = self._players.indexOf(player)
        if loser > 1: return {"success":False, "message":"Player was not player"}

        self._winner = not loser

        return {"success":True}

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

