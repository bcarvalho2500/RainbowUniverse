class Player:
    def __init__(self, client):
        self.client  = client
        self.alias   = "UNNAMED"
        self.inGame  = False
        self.inLobby = None

        self.pos = {"x":0, "y":0}
        self.vel = {"x":0, "y":0}

    def getClientId(self):
        return self.client["id"]

    def __eq__(self, other):
        return self.client["id"] == other.client["id"]

    def __ne__(self, other):
        return self.client["id"] != other.client["id"]

