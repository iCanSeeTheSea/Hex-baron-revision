# Skeleton Program code for the AQA A Level Paper 1 Summer 2021 examination
# this code should be used in conjunction with the Preliminary Material
# written by the AQA Programmer Team
# developed in the Python 3.5 programming environment

import random
import os


class Piece:
    def __init__(self, Player1):
        self._FuelCostOfMove = 1
        self._BelongsToPlayer1 = Player1
        self._Destroyed = False
        self._PieceType = "S"
        self._VPValue = 1
        self._ConnectionsToDestroy = 2

    def GetVPs(self):
        return self._VPValue

    def GetBelongsToPlayer1(self):
        return self._BelongsToPlayer1

    def CheckMoveIsValid(self, DistanceBetweenTiles, StartTerrain, EndTerrain):
        if DistanceBetweenTiles == 1:
            if StartTerrain == "~" or EndTerrain == "~":
                return self._FuelCostOfMove * 2
            else:
                return self._FuelCostOfMove
        return -1

    def HasMethod(self, MethodName):
        return callable(getattr(self, MethodName, None))

    def GetConnectionsNeededToDestroy(self):
        return self._ConnectionsToDestroy

    def GetPieceType(self):
        if self._BelongsToPlayer1:
            return self._PieceType
        else:
            return self._PieceType.lower()

    def DestroyPiece(self):
        self._Destroyed = True


class BaronPiece(Piece):
    def __init__(self, Player1):
        super(BaronPiece, self).__init__(Player1)
        self._PieceType = "B"
        self._VPValue = 10

    def CheckMoveIsValid(self, DistanceBetweenTiles, StartTerrain, EndTerrain):
        if DistanceBetweenTiles == 1:
            return self._FuelCostOfMove
        return -1


class LESSPiece(Piece):
    def __init__(self, Player1):
        super(LESSPiece, self).__init__(Player1)
        self._PieceType = "L"
        self._VPValue = 3

    def CheckMoveIsValid(self, DistanceBetweenTiles, StartTerrain, EndTerrain):
        if DistanceBetweenTiles == 1 and StartTerrain != "#":
            if StartTerrain == "~" or EndTerrain == "~":
                return self._FuelCostOfMove * 2
            else:
                return self._FuelCostOfMove
        return -1

    def Saw(self, Terrain):
        if Terrain != "#":
            return 0
        return 1


class PBDSPiece(Piece):
    def __init__(self, Player1):
        super(PBDSPiece, self).__init__(Player1)
        self._PieceType = "P"
        self._VPValue = 2
        self._FuelCostOfMove = 2

    def CheckMoveIsValid(self, DistanceBetweenTiles, StartTerrain, EndTerrain):
        if DistanceBetweenTiles != 1 or StartTerrain == "~":
            return -1
        return self._FuelCostOfMove

    def Dig(self, Terrain):
        if Terrain != "~":
            return 0
        if random.random() < 0.9:
            return 1
        else:
            return 5


# * Mining and Spelunking serf
class MASSPiece(Piece):
    def __init__(self, Player1):
        super(MASSPiece, self).__init__(Player1)
        self._PieceType = "M"
        self._VPValue = 3
        self._FuelCostOfMove = 1

    def CheckMoveIsValid(self, DistanceBetweenTiles, StartTerrain, EndTerrain):
        if DistanceBetweenTiles != 1 or StartTerrain == "@":
            return -1
        return self._FuelCostOfMove

    def Mine(self, Terrain):
        if Terrain != "@":
            return 0
        if random.random() < 0.5:
            return 1
        else:
            return 3


class Tile:
    def __init__(self, xcoord, ycoord, zcoord):
        self._x = xcoord
        self._y = ycoord
        self._z = zcoord
        self._Terrain = " "
        self._PieceInTile = None
        self._Neighbours = []

    def GetDistanceToTileT(self, T):
        return max(max(abs(self.Getx() - T.Getx()), abs(self.Gety() - T.Gety())), abs(self.Getz() - T.Getz()))

    def AddToNeighbours(self, N):
        self._Neighbours.append(N)

    def GetNeighbours(self):
        return self._Neighbours

    def SetPiece(self, ThePiece):
        self._PieceInTile = ThePiece

    def SetTerrain(self, T):
        self._Terrain = T

    def Getx(self):
        return self._x

    def Gety(self):
        return self._y

    def Getz(self):
        return self._z

    def GetTerrain(self):
        return self._Terrain

    def GetPieceInTile(self):
        return self._PieceInTile


class HexGrid:
    def __init__(self, n):
        self._Size = n
        self._Player1Turn = True
        self._Tiles = []
        self._Pieces = []
        self.__ListPositionOfTile = 0
        self.__SetUpTiles()
        self.__SetUpNeighbours()

    def getGridSize(self):
        return self._Size

    def getTerrainListAsString(self):
        terrainString = ''
        for tile in self._Tiles:
            terrainString += f'{tile.GetTerrain()},'
        return terrainString

    def SetUpGridTerrain(self, ListOfTerrain):
        for Count in range(0, len(ListOfTerrain)-1):
            self._Tiles[Count].SetTerrain(ListOfTerrain[Count])

    def AddPiece(self, BelongsToPlayer1, TypeOfPiece, Location):
        if TypeOfPiece == "Baron":
            NewPiece = BaronPiece(BelongsToPlayer1)
        elif TypeOfPiece == "LESS":
            NewPiece = LESSPiece(BelongsToPlayer1)
        elif TypeOfPiece == "PBDS":
            NewPiece = PBDSPiece(BelongsToPlayer1)
        elif TypeOfPiece == 'MASS':
            NewPiece = MASSPiece(BelongsToPlayer1)
        else:
            NewPiece = Piece(BelongsToPlayer1)
        self._Pieces.append(NewPiece)
        self._Tiles[Location].SetPiece(NewPiece)

    def ExecuteCommand(self, Items, FuelAvailable, LumberAvailable, OreAvailable, PiecesInSupply):
        FuelChange = 0
        LumberChange = 0
        OreChange = 0
        SupplyChange = 0
        if Items[0] == "move":
            FuelCost = self.__ExecuteMoveCommand(Items, FuelAvailable)
            if FuelCost < 0:
                return "That move can't be done", FuelChange, LumberChange, OreChange, SupplyChange
            FuelChange = -FuelCost
        elif Items[0] in ["saw", "dig", "mine"]:
            Success, FuelChange, LumberChange, OreChange = self.__ExecuteCommandInTile(
                Items)
            if not Success:
                return "Couldn't do that", FuelChange, LumberChange, OreChange, SupplyChange
        elif Items[0] == "spawn":
            LumberCost = self.__ExecuteSpawnCommand(
                Items, LumberAvailable, PiecesInSupply)
            if LumberCost < 0:
                return "Spawning did not occur", FuelChange, LumberChange, OreChange, SupplyChange
            LumberChange = -LumberCost
            SupplyChange = 1
        elif Items[0] == "upgrade":
            LumberCost = self.__ExecuteUpgradeCommand(Items, LumberAvailable)
            if LumberCost < 0:
                return "Upgrade not possible", FuelChange, LumberChange, OreChange, SupplyChange
            LumberChange = -LumberCost
        return "Command executed", FuelChange, LumberChange, OreChange, SupplyChange

    def __CheckTileIndexIsValid(self, TileToCheck):
        return TileToCheck >= 0 and TileToCheck < len(self._Tiles)

    def __CheckPieceAndTileAreValid(self, TileToUse):
        if self.__CheckTileIndexIsValid(TileToUse):
            ThePiece = self._Tiles[TileToUse].GetPieceInTile()
            if ThePiece is not None:
                if ThePiece.GetBelongsToPlayer1() == self._Player1Turn:
                    return True
        return False

    def __ExecuteCommandInTile(self, Items):
        TileToUse = int(Items[1])
        Fuel = 0
        Lumber = 0
        Ore = 0
        if self.__CheckPieceAndTileAreValid(TileToUse) == False:
            return False, Fuel, Lumber
        ThePiece = self._Tiles[TileToUse].GetPieceInTile()
        Items[0] = Items[0][0].upper() + Items[0][1:]
        if ThePiece.HasMethod(Items[0]):
            Method = getattr(ThePiece, Items[0], None)
            if Items[0] == "Saw":
                Lumber += Method(self._Tiles[TileToUse].GetTerrain())
            elif Items[0] == "Dig":
                Fuel += Method(self._Tiles[TileToUse].GetTerrain())
                if abs(Fuel) > 2:
                    self._Tiles[TileToUse].SetTerrain(" ")
            elif Items[0] == "Mine":
                Ore += Method(self._Tiles[TileToUse].GetTerrain())
            return True, Fuel, Lumber, Ore
        return False, Fuel, Lumber, Ore

    def __ExecuteMoveCommand(self, Items, FuelAvailable):
        StartID = int(Items[1])
        EndID = int(Items[2])
        if not self.__CheckPieceAndTileAreValid(StartID) or not self.__CheckTileIndexIsValid(EndID):
            return -1
        ThePiece = self._Tiles[StartID].GetPieceInTile()
        if self._Tiles[EndID].GetPieceInTile() is not None:
            return -1
        Distance = self._Tiles[StartID].GetDistanceToTileT(self._Tiles[EndID])
        FuelCost = ThePiece.CheckMoveIsValid(
            Distance, self._Tiles[StartID].GetTerrain(), self._Tiles[EndID].GetTerrain())
        if FuelCost == -1 or FuelAvailable < FuelCost:
            return -1
        self.__MovePiece(EndID, StartID)
        return FuelCost

    def __ExecuteSpawnCommand(self, Items, LumberAvailable, PiecesInSupply):
        TileToUse = int(Items[1])
        if PiecesInSupply < 1 or LumberAvailable < 3 or not self.__CheckTileIndexIsValid(TileToUse):
            return -1
        ThePiece = self._Tiles[TileToUse].GetPieceInTile()
        if ThePiece is not None:
            return -1
        OwnBaronIsNeighbour = False
        ListOfNeighbours = self._Tiles[TileToUse].GetNeighbours()
        for N in ListOfNeighbours:
            ThePiece = N.GetPieceInTile()
            if ThePiece is not None:
                if self._Player1Turn and ThePiece.GetPieceType() == "B" or \
                        not self._Player1Turn and ThePiece.GetPieceType() == "b":
                    OwnBaronIsNeighbour = True
                    break
        if not OwnBaronIsNeighbour:
            return -1
        NewPiece = Piece(self._Player1Turn)
        self._Pieces.append(NewPiece)
        self._Tiles[TileToUse].SetPiece(NewPiece)
        return 3

    def __ExecuteUpgradeCommand(self, Items, LumberAvailable):
        TileToUse = int(Items[2])
        if not self.__CheckPieceAndTileAreValid(TileToUse) or LumberAvailable < 5 or \
                not (Items[1] == "pbds" or Items[1] == "less" or Items[1] == "mass"):
            return -1
        else:
            ThePiece = self._Tiles[TileToUse].GetPieceInTile()
            if ThePiece.GetPieceType().upper() != "S":
                return -1
            ThePiece.DestroyPiece()
            if Items[1] == "pbds":
                ThePiece = PBDSPiece(self._Player1Turn)
            elif Items[1] == "mass":
                ThePiece = MASSPiece(self._Player1Turn)
            else:
                ThePiece = LESSPiece(self._Player1Turn)
            self._Pieces.append(ThePiece)
            self._Tiles[TileToUse].SetPiece(ThePiece)
            return 5

    def __SetUpTiles(self):
        EvenStartY = 0
        EvenStartZ = 0
        OddStartZ = 0
        OddStartY = -1
        for count in range(1, self._Size // 2 + 1):
            y = EvenStartY
            z = EvenStartZ
            for x in range(0, self._Size - 1, 2):
                TempTile = Tile(x, y, z)
                self._Tiles.append(TempTile)
                y -= 1
                z -= 1
            EvenStartZ += 1
            EvenStartY -= 1
            y = OddStartY
            z = OddStartZ
            for x in range(1, self._Size, 2):
                TempTile = Tile(x, y, z)
                self._Tiles.append(TempTile)
                y -= 1
                z -= 1
            OddStartZ += 1
            OddStartY -= 1

    def __SetUpNeighbours(self):
        for FromTile in self._Tiles:
            for ToTile in self._Tiles:
                if FromTile.GetDistanceToTileT(ToTile) == 1:
                    FromTile.AddToNeighbours(ToTile)

    def DestroyPiecesAndCountVPs(self):
        BaronDestroyed = False
        Player1VPs = 0
        Player2VPs = 0
        ListOfTilesContainingDestroyedPieces = []
        for T in self._Tiles:
            if T.GetPieceInTile() is not None:
                ListOfNeighbours = T.GetNeighbours()
                NoOfConnections = 0
                for N in ListOfNeighbours:
                    if N.GetPieceInTile() is not None:
                        NoOfConnections += 1
                ThePiece = T.GetPieceInTile()
                if NoOfConnections >= ThePiece.GetConnectionsNeededToDestroy():
                    ThePiece.DestroyPiece()
                    if ThePiece.GetPieceType().upper() == "B":
                        BaronDestroyed = True
                    ListOfTilesContainingDestroyedPieces.append(T)
                    if ThePiece.GetBelongsToPlayer1():
                        Player2VPs += ThePiece.GetVPs()
                    else:
                        Player1VPs += ThePiece.GetVPs()
        for T in ListOfTilesContainingDestroyedPieces:
            T.SetPiece(None)
        return BaronDestroyed, Player1VPs, Player2VPs

    # * inserted function
    def drawGridWithTileNumbers(self):
        output = '  '
        lastEnd = 0
        for line in range(0, self._Size):
            for count in range(0, self._Size // 2):
                # space between numbers should be smaller when size of number increases
                split = ' ' * (6 - len(str(count + lastEnd)))
                output += f'{count + lastEnd}{split}'
            lastEnd += self._Size // 2
            # correct indentation for odd and even lines
            if line % 2 == 0:
                output += '\n    '
            else:
                output += '\n  '
        print(output)

    def GetGridAsString(self, P1Turn):
        self.__ListPositionOfTile = 0
        self._Player1Turn = P1Turn
        GridAsString = self.__CreateTopLine() + self.__CreateEvenLine(True)
        self.__ListPositionOfTile += 1
        GridAsString += self.__CreateOddLine()
        for count in range(1, self._Size - 1, 2):
            self.__ListPositionOfTile += 1
            GridAsString += self.__CreateEvenLine(False)
            self.__ListPositionOfTile += 1
            GridAsString += self.__CreateOddLine()
        return GridAsString + self.__CreateBottomLine()

    def __MovePiece(self, NewIndex, OldIndex):
        self._Tiles[NewIndex].SetPiece(self._Tiles[OldIndex].GetPieceInTile())
        self._Tiles[OldIndex].SetPiece(None)

    def GetPieceTypeInTile(self, ID):
        ThePiece = self._Tiles[ID].GetPieceInTile()
        if ThePiece is None:
            return " "
        else:
            return ThePiece.GetPieceType()

    def __CreateBottomLine(self):
        Line = "   "
        for count in range(1, self._Size // 2 + 1):
            Line += " \\__/ "
        return Line + os.linesep

    def __CreateTopLine(self):
        Line = os.linesep + "  "
        for count in range(1, self._Size // 2 + 1):
            Line += "__    "
        return Line + os.linesep

    def __CreateOddLine(self):
        Line = ""
        for count in range(1, self._Size // 2 + 1):
            if count > 1 and count < self._Size // 2:
                Line += self.GetPieceTypeInTile(
                    self.__ListPositionOfTile) + f"\\__/"
                self.__ListPositionOfTile += 1
                Line += self._Tiles[self.__ListPositionOfTile].GetTerrain()
            elif count == 1:
                Line += " \\__/" + \
                    self._Tiles[self.__ListPositionOfTile].GetTerrain()
        Line += self.GetPieceTypeInTile(self.__ListPositionOfTile) + "\\__/"
        self.__ListPositionOfTile += 1
        if self.__ListPositionOfTile < len(self._Tiles):
            Line += self._Tiles[self.__ListPositionOfTile].GetTerrain(
            ) + self.GetPieceTypeInTile(self.__ListPositionOfTile) + "\\" + os.linesep
        else:
            Line += "\\" + os.linesep
        return Line

    def __CreateEvenLine(self, FirstEvenLine):
        Line = " /" + self._Tiles[self.__ListPositionOfTile].GetTerrain()
        for count in range(1, self._Size // 2):
            Line += self.GetPieceTypeInTile(self.__ListPositionOfTile)
            self.__ListPositionOfTile += 1
            Line += "\\__/" + \
                self._Tiles[self.__ListPositionOfTile].GetTerrain()
        if FirstEvenLine:
            Line += self.GetPieceTypeInTile(
                self.__ListPositionOfTile) + "\\__" + os.linesep
        else:
            Line += self.GetPieceTypeInTile(self.__ListPositionOfTile) + \
                "\\__/" + os.linesep
        return Line


class Player:
    def __init__(self, N, V, F, L, O, T,):
        self._Name = N
        self._VPs = V
        self._Fuel = F
        self._Lumber = L
        self._Ore = O
        self._PiecesInSupply = T

    def GetStateString(self):
        return "VPs: " + str(self._VPs) + "   Pieces in supply: " + str(self._PiecesInSupply) + \
               "   Lumber: " + str(self._Lumber) + "   Fuel: " + str(self._Fuel) + "   Ore:" + str(self._Ore)

    def GetVPs(self):
        return self._VPs

    def GetFuel(self):
        return self._Fuel

    def GetLumber(self):
        return self._Lumber

    def GetOre(self):
        return self._Ore

    def GetName(self):
        return self._Name

    def AddToVPs(self, n):
        self._VPs += n

    def UpdateFuel(self, n):
        self._Fuel += n

    def UpdateLumber(self, n):
        self._Lumber += n

    def UpdateOre(self, n):
        self._Ore += n

    def GetPiecesInSupply(self):
        return self._PiecesInSupply

    def RemoveTileFromSupply(self):
        self._PiecesInSupply -= 1

    def getDataAsString(self):
        dataString = f'{self._Name}, {self._VPs}, {self._Fuel}, {self._Lumber}, {self._Ore}, {self._PiecesInSupply}'
        return dataString


def Main():
    FileLoaded = True
    Player1 = None
    Player2 = None
    Grid = None
    Choice = ""
    while Choice != "Q":
        DisplayMainMenu()
        Choice = input()
        if Choice == "1":
            Player1, Player2, Grid = SetUpDefaultGame()
            PlayGame(Player1, Player2, Grid)
        elif Choice == "2":
            FileLoaded, Player1, Player2, Grid = LoadGame()
            if FileLoaded:
                PlayGame(Player1, Player2, Grid)
        elif Choice == '3':
            Player1, Player2, Grid = setUpCustomGame()
            PlayGame(Player1, Player2, Grid)


def LoadGame():
    FileName = input("Enter the name of the file to load: ")
    Items = []
    LineFromFile = ""
    Player1 = None
    Player2 = None
    Grid = None
    try:
        with open(FileName) as f:
            LineFromFile = f.readline().rstrip()
            Items = LineFromFile.split(",")
            Player1 = Player(Items[0], int(Items[1]), int(
                Items[2]), int(Items[3]), int(Items[4]), int(Items[5]))
            LineFromFile = f.readline().rstrip()
            Items = LineFromFile.split(",")
            Player2 = Player(Items[0], int(Items[1]), int(
                Items[2]), int(Items[3]), int(Items[4]), int(Items[5]))
            GridSize = int(f.readline().rstrip())
            Grid = HexGrid(GridSize)
            T = f.readline().rstrip().split(",")
            Grid.SetUpGridTerrain(T)
            LineFromFile = f.readline().rstrip()
            while LineFromFile != "":
                Items = LineFromFile.split(",")
                if Items[0] == "1":
                    Grid.AddPiece(True, Items[1], int(Items[2]))
                else:
                    Grid.AddPiece(False, Items[1], int(Items[2]))
                LineFromFile = f.readline().rstrip()
    except FileNotFoundError:
        print("File not loaded")
        return False, Player1, Player2, Grid
    return True, Player1, Player2, Grid


# * inserted code
def saveGame(Player1, Player2, Grid):
    fileName = input('file name: ')
    try:
        _ = open(fileName, 'r')
        check = input(f'a file called {fileName} already exists, would you like to overwrite it? y/n: ')
    except FileNotFoundError:
        print('creating new file')
        check = 'y'
    if check.lower() == 'y':
        with open(fileName, 'w') as file:
            file.write(Player1.getDataAsString() + '\n')
            file.write(Player2.getDataAsString() + '\n')
            file.write(str(Grid.getGridSize()) + '\n')
            file.write(Grid.getTerrainListAsString() + '\n')
            for count in range(Grid.getGridSize() * (Grid.getGridSize()//2)):
                piece = Grid.GetPieceTypeInTile(count)
                stringToSave = ''
                if piece != ' ':
                    if piece.isupper():
                        stringToSave += '1,'
                    else:
                        stringToSave += '2,'
                    if piece.lower() == 'b':
                        stringToSave += 'Baron,'
                    elif piece.lower() == 's':
                        stringToSave += 'Serf,'
                    elif piece.lower() == 'l':
                        stringToSave += 'LESS'
                    elif piece.lower() == 'p':
                        stringToSave += 'PBDS'
                    elif piece.lower() == 'm':
                        stringToSave += 'MASS'
                    stringToSave += f'{count}'
                    file.write(stringToSave + '\n')

def SetUpDefaultGame():

    T = [" ", "#", "#", " ", "~", "~", " ", " ", " ", "~", " ", "#", "#", " ", " ", " ",
         " ", " ", "#", "#", "#", "#", "~", "~", "~", "~", "~", " ", "#", " ", "#", " "]
    GridSize = 8
    Grid = HexGrid(GridSize)
    Player1 = Player("Player One", 0, 10, 10, 10, 5)
    Player2 = Player("Player Two", 1, 10, 10, 10, 5)
    Grid.SetUpGridTerrain(T)
    Grid.AddPiece(True, "Baron", 0)
    Grid.AddPiece(True, "Serf", 8)
    Grid.AddPiece(False, "Baron", 31)
    Grid.AddPiece(False, "Serf", 23)
    return Player1, Player2, Grid


def setUpCustomGame():
    GridSize = int(input('enter grid size: '))
    while GridSize % 2 != 0 and GridSize > 3:
        print('invalid grid size')
        GridSize = int(input('enter grid size: '))
    Grid = HexGrid(GridSize)
    Player1 = Player("Player One", 0, 10, 10, 10, 5)
    Player2 = Player("Player Two", 1, 10, 10, 10, 5)
    T = []
    for count in range(GridSize*(GridSize//2)-1):
        randType = random.randint(1, 8)
        if randType == 8:
            T.append('@')
        elif randType > 5:
            T.append('#')
        elif randType > 3:
            T.append('~')
        else:
            T.append(' ')
    Grid.SetUpGridTerrain(T)
    Grid.AddPiece(True, "Baron", 0)
    Grid.AddPiece(True, "Serf", GridSize)
    Grid.AddPiece(False, 'Baron', GridSize*(GridSize//2)-1)
    Grid.AddPiece(False, 'Serf', GridSize*((GridSize//2)-1)-1)
    return Player1, Player2, Grid


def CheckMoveCommandFormat(Items):
    if len(Items) == 3:
        for Count in range(1, 3):
            try:
                Result = int(Items[Count])
            except:
                return False
        return True
    return False


def CheckStandardCommandFormat(Items):
    if len(Items) == 2:
        try:
            Result = int(Items[1])
        except:
            return False
        return True
    return False


def CheckUpgradeCommandFormat(Items):
    if len(Items) == 3:
        if Items[1].upper() != "LESS" and Items[1].upper() != "PBDS" and Items[1].upper() != "MASS":
            return False
        try:
            Result = int(Items[2])
        except:
            return False
        return True
    return False


def CheckCommandIsValid(Items):
    if len(Items) > 0:
        if Items[0] == "move":
            return CheckMoveCommandFormat(Items)
        elif Items[0] in ["dig", "saw", "mine", "spawn"]:
            return CheckStandardCommandFormat(Items)
        elif Items[0] == "upgrade":
            return CheckUpgradeCommandFormat(Items)
    return False


def PlayGame(Player1, Player2, Grid):
    GameOver = False
    Player1Turn = True
    Commands = []
    print("Player One current state - " + Player1.GetStateString())
    print("Player Two current state - " + Player2.GetStateString())
    while not (GameOver and Player1Turn):
        print(Grid.GetGridAsString(Player1Turn))
        Grid.drawGridWithTileNumbers()
        if Player1Turn:
            print(Player1.GetName() +
                  " state your three commands, pressing enter after each one.")
        else:
            print(Player2.GetName() +
                  " state your three commands, pressing enter after each one.")
        for Count in range(1, 4):
            # * inserted code
            while True:
                command = input("Enter command: ").lower()
                if 'help' in command.lower():
                    print('''Available commands:
        move [from: int] [to: int] - moves a piece from one tile to another (cost: variable fuel)
        upgrade [type: LESS / PBDS / MASS] [position: int] - upgrades a serf into a LESS, PBDS or MASS (cost: 5 lumber)
        spawn [position: int] - spawns a serf at a position, must be adjacent to baron (cost: 3 lumber, 1 available piece)
        saw [position: int] - uses a LESS to obtain wood from a forest
        dig [position: int] - used a PBDS to obtain fuel from a peat bog
        mine [position: int} - uses a MASS to obtain ore from a cave
        save - saves the current game state to a file
        quit - saves and quits the game
                    ''')
                elif 'save' in command.lower():
                    saveGame(Player1, Player2, Grid)
                elif 'quit' in command.lower():
                    saveGame(Player1, Player2, Grid)
                    quit()
                else:
                    Commands.append(command)
                    break
        for C in Commands:
            Items = C.split(" ")
            ValidCommand = CheckCommandIsValid(Items)
            if not ValidCommand:
                print("Invalid command")
            else:
                FuelChange = 0
                LumberChange = 0
                SupplyChange = 0
                OreChange = 0
                if Player1Turn:
                    SummaryOfResult, FuelChange, LumberChange, OreChange, SupplyChange = Grid.ExecuteCommand(
                        Items, Player1.GetFuel(), Player1.GetLumber(), Player1.GetOre(), Player1.GetPiecesInSupply())
                    Player1.UpdateLumber(LumberChange)
                    Player1.UpdateFuel(FuelChange)
                    Player1.UpdateOre(OreChange)
                    if SupplyChange == 1:
                        Player1.RemoveTileFromSupply()
                else:
                    SummaryOfResult, FuelChange, LumberChange, OreChange, SupplyChange = Grid.ExecuteCommand(
                        Items, Player2.GetFuel(), Player2.GetLumber(), Player2.GetOre(), Player2.GetPiecesInSupply())
                    Player2.UpdateLumber(LumberChange)
                    Player2.UpdateFuel(FuelChange)
                    if SupplyChange == 1:
                        Player2.RemoveTileFromSupply()
                print(SummaryOfResult)
        Commands.clear()
        Player1Turn = not Player1Turn
        Player1VPsGained = 0
        Player2VPsGained = 0
        if GameOver:
            GameOver, Player1VPsGained, Player2VPsGained = Grid.DestroyPiecesAndCountVPs()
            GameOver = True
        else:
            GameOver, Player1VPsGained, Player2VPsGained = Grid.DestroyPiecesAndCountVPs()
        Player1.AddToVPs(Player1VPsGained)
        Player2.AddToVPs(Player2VPsGained)
        print("Player One current state - " + Player1.GetStateString())
        print("Player Two current state - " + Player2.GetStateString())
        input("Press Enter to continue...")
    print(Grid.GetGridAsString(Player1Turn))
    DisplayEndMessages(Player1, Player2)


def DisplayEndMessages(Player1, Player2):
    print()
    print(Player1.GetName() + " final state: " + Player1.GetStateString())
    print()
    print(Player2.GetName() + " final state: " + Player2.GetStateString())
    print()
    if Player1.GetVPs() > Player2.GetVPs():
        print(Player1.GetName() + " is the winner!")
    else:
        print(Player2.GetName() + " is the winner!")


def DisplayMainMenu():
    print("1. Default game")
    print("2. Load game")
    print('3. custom game')
    print("Q. Quit")
    print()
    print("Enter your choice: ", end="")


if __name__ == "__main__":
    Main()
