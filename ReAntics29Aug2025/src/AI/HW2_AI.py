import random
import sys
import unittest
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "HW2_AI")
    
    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)
        gameStates = []
        nodeList = []
        for move in moves:
            gameState = getNextState(currentState, move)
            gameStates.append(gameState)
            node = Node(move, gameState, 1, self.utility(currentState), None)
            nodeList.append(node)

        winningNode = self.bestMove(nodeList)
        return winningNode.move

    
    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass


    def bestMove(self, nodeList):
        bestChance = 0
        winningNode = None
        for node in nodeList:
            if node.winChance > bestChance:
                bestChance = node.winChance
                winningNode = node

        return winningNode


    def utility(self, currentState):
        #ants = (WORKER, DRONE, SOLDIER, R_SOLDIER)

        myInv = getCurrPlayerInventory(currentState)
        enemyInv = getEnemyInv(self, currentState)

        #foodDif = myInv.foodCount - enemyInv.foodCount

        myAnts = myInv.ants
        enemyAnts = enemyInv.ants

        myAntCost = 0
        for ant in myAnts:
            cost = UNIT_STATS[ant.type][COST]
            if cost != None:
                myAntCost += cost

        enemyAntCost = 0
        for ant in enemyAnts:
            cost = UNIT_STATS[ant.type][COST]
            if cost != None:
                enemyAntCost += cost

        myNetWorth = myAntCost + myInv.foodCount
        enemyNetWorth = enemyAntCost + enemyInv.foodCount

        netWorthDif = myNetWorth - enemyNetWorth

        winChance = 0.5

        foodFactor = 0.05
        winChance += netWorthDif * foodFactor

        myFood = myInv.foodCount
        match myFood:
            case 0:
                if len(getAntList(currentState, currentState.whoseTurn, (WORKER,))) == 0:
                    winChance = 0
            case 1:
                winChance += 0.05
            case 2:
                winChance += 0.05
            case 3:
                winChance += 0.1
            case 4:
                winChance += 0.15
            case 5:
                winChance += 0.2
            case 6:
                winChance += 0.25
            case 7:
                winChance += 0.3
            case 8:
                winChance += 0.35
            case 9:
                winChance += 0.4
            case 10:
                winChance += 0.45
            case 11:
                winChance = 1

        enemyFood = enemyInv.foodCount
        match enemyFood:
            case 0:
                if len(getAntList(currentState, currentState.whoseTurn - 1, (WORKER,))) == 0:
                    winChance = 1
            case 1:
                winChance -= 0.05
            case 2:
                winChance -= 0.05
            case 3:
                winChance -= 0.1
            case 4:
                winChance -= 0.15
            case 5:
                winChance -= 0.2
            case 6:
                winChance -= 0.25
            case 7:
                winChance -= 0.3
            case 8:
                winChance -= 0.35
            case 9:
                winChance -= 0.4
            case 10:
                winChance -= 0.45
            case 11:
                winChance = 0
        
        myQueenHP = myInv.getQueen().health
        match myQueenHP:
            case 8:
                winChance -= 0.05
            case 7:
                winChance -= 0.1
            case 6:
                winChance -= 0.15
            case 5:
                winChance -= 0.2
            case 4:
                winChance -= 0.3
            case 3:
                winChance -= 0.35
            case 2:
                winChance -= 0.4
            case 0:
                winChance = 0

        enemyQueenHP = enemyInv.getQueen().health
        match enemyQueenHP:
            case 8:
                winChance -= 0.05
            case 7:
                winChance -= 0.1
            case 6:
                winChance -= 0.15
            case 5:
                winChance -= 0.2
            case 4:
                winChance -= 0.3
            case 3:
                winChance -= 0.35
            case 2:
                winChance -= 0.4
            case 0:
                winChance = 0

        queenHPDif = myQueenHP - enemyQueenHP
        hpFactor = 0.05
        winChance += queenHPDif * hpFactor

        myAnthill = myInv.getAnthill()
        myAnthillHP = CONSTR_STATS[myAnthill.type][CAP_HEALTH]
        match myAnthillHP:
            case 1:
                winChance -= 0.4
            case 0:
                winChance = 0

        enemyAnthill = enemyInv.getAnthill()
        enemyAnthillHP = CONSTR_STATS[enemyAnthill.type][CAP_HEALTH]
        match enemyAnthillHP:
            case 1:
                winChance += 0.4
            case 0:
                winChance = 1

        return winChance


class Node:
    def __init__(self, move, gameState, depth, winChance, parent):
        self.move = move
        self.gameState = gameState
        self.depth = depth
        self.winChance = winChance
        self.parent = parent
        

class TestMethods(unittest.TestCase):
    
    def test_Utility(self):
        myAnts = [Ant(None, QUEEN, 0), Ant(None, WORKER, 0), Ant(None, DRONE, 0), Ant(None, SOLDIER, 0)]
        enemyAnts = [Ant(None, QUEEN, 0), Ant(None, WORKER, 1)]
        
        anthill = Construction(None, ANTHILL)
        tunnel = Construction(None, TUNNEL)
        
        
        myInv = Inventory(0, myAnts, [anthill, tunnel], 5)
        enemyInv = Inventory(1, enemyAnts, [anthill, tunnel], 3)
        
        state = GameState(None, [myInv, enemyInv], 0, 0)
        
        agent = AIPlayer(0)
        result = agent.utility(state)
        
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 1)
    
    def test_BestMove(self):
        n1 = Node("move1", None, 1, 0, None)
        n2 = Node("move2", None, 1, 0.6, None)
        n3 = Node("move3", None, 1, -0.7, None)  
        
        agent = AIPlayer(0)
        result = agent.bestMove([n1, n2, n3])
        self.assertEqual(result, n2)
        
    def test_getMove(self):
        myAnts = [Ant((0,0), QUEEN, 0), Ant((1,0), WORKER, 0), Ant((2,2), DRONE, 0), Ant((3,3), SOLDIER, 0)]
        enemyAnts = [Ant((0,0), QUEEN, 0), Ant((1,0), WORKER, 1)]
        
        anthill = Construction(None, ANTHILL)
        tunnel = Construction(None, TUNNEL)
        
        myInv = Inventory(0, myAnts, [anthill, tunnel], 5)
        enemyInv = Inventory(1, enemyAnts, [anthill, tunnel], 3)
        neutralInv = Inventory(2, [], [], 0)
        
        state = GameState(None, [myInv, enemyInv, neutralInv], 0, 0)
        
        agent = AIPlayer(0)
        result = agent.getMove(state)
        self.assertEqual(result.moveType == MOVE_ANT, result.coordList == [(0,0),(0,1)])
        
        
if __name__ == "__main__":
    unittest.main()