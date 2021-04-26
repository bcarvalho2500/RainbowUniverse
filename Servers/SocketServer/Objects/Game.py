import random

class Game:
    def __init__(self, players):
        self._players = players
        self._turnCounter = 0
        self._currentTurn = self._getColorFromIndex(self._turnCounter)
        self._winner = None
        self._board = [[" bbb  rrr"[(i+1)*(((i+j)%2) == 0)] for j in range(8)] for i in range(8)]
        self._pieceCount = {"b":12, "r":12}

        for player in self._players:
            player.inGame = self

    def _getColorFromIndex(self, index):
        return "br"[index]

    def getPlayerIndex(self, player):
        try: return self._players.index(player)
        except: -1

    def getPlayerColor(self, player):
        playerIndex = self.getPlayerIndex(player)
        if playerIndex >= 2 or playerIndex < 0: return " "
        return self._getColorFromIndex(playerIndex)

    def makeMove(self, player, move):
        playerColor = self.getPlayerColor(player)

        if playerColor == " ":
            return {"success":False, "message":"You are not part of the game!"}

        if playerColor != self._currentTurn:
            return {"success":False, "message":"It isnt your turn"}

        if playerColor == "b":
            move["from"]["x"] = 7-move["from"]["x"]
            move["from"]["y"] = 7-move["from"]["y"]
            move["to"]["x"]   = 7-move["to"]["x"]
            move["to"]["y"]   = 7-move["to"]["y"]

        pieceColor = self._board[move["from"]["y"]][move["from"]["x"]].lower()
        if pieceColor == " ": return {"success":False, "message":"There is no piece here"}
        if pieceColor != playerColor: return {"success":False, "message":"That is not your piece"}

        if move["from"]["y"] < 0 or move["from"]["y"] >= 8: return {"success":False, "message":"Invalid move"}
        if move["from"]["x"] < 0 or move["from"]["x"] >= 8: return {"success":False, "message":"Invalid move"}
        if move["to"]["y"]   < 0 or move["to"]["y"]   >= 8: return {"success":False, "message":"Invalid move"}
        if move["to"]["x"]   < 0 or move["to"]["x"]   >= 8: return {"success":False, "message":"Invalid move"}

        isKing = self._board[move["from"]["y"]][move["from"]["x"]].isupper()

        newPiece = self._board[move["from"]["y"]][move["from"]["x"]]
        if move["to"]["y"] == 7 or move["to"]["y"] == 0: newPiece = newPiece.upper()

        # doesnt fully validate player moves. oh well

        if abs(move["from"]["x"]-move["to"]["x"]) != 1 or abs(move["from"]["y"]-move["to"]["y"]) != 1:
            if abs(move["from"]["x"]-move["to"]["x"]) != 2 or abs(move["from"]["y"]-move["to"]["y"]) != 2:
                return {"success":False, "message":"Invalid move"}

            xDir = -1 if move["from"]["x"]>move["to"]["x"] else 1;
            yDir = -1 if move["from"]["y"]>move["to"]["y"] else 1;

            betweenColor = self._board[move["from"]["y"]+yDir][move["from"]["x"]+xDir].lower()
            if betweenColor == playerColor:
                return {"success":False, "message":"Cant capture your own piece"}
            else:
                self._pieceCount[betweenColor] -= 1
                if self._pieceCount[betweenColor] == 0: self.setWinner(player)
                self._board[move["from"]["y"]+yDir][move["from"]["x"]+xDir] = ' '

        self._board[move["to"]["y"]][move["to"]["x"]] = newPiece;
        self._board[move["from"]["y"]][move["from"]["x"]] = " ";

        self._turnCounter += 1
        self._currentTurn = self._getColorFromIndex(self._turnCounter%2)

        return {"success":True}

    def setLoser(self, player):
        playerColor = self.getPlayerColor(player)
        if playerColor == " ": return {"success":False, "message":"Player was not player"}

        self._winner = "rb"["br".find(playerColor)]

        return {"success":True}

    def setWinner(self, player):
        playerColor = self.getPlayerColor(player)
        if playerColor == " ": return {"success":False, "message":"Player was not player"}

        self._winner = playerColor

        return {"success":True}

    def getWinner(self):
        return self._winner

    def getCurrentTurn(self):
        return self._currentTurn

    def getPlayerBoard(self, player):
        playerColor = self.getPlayerColor(player)
        return self._board if playerColor == "r" else [r[::-1] for r in self._board[::-1]]

    def removeSpectator(self, spectator):
        spectator.inGame = None
        self.spectator.remove(spectator)

