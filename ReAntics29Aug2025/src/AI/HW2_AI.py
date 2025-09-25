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

    DEPTH_LIMIT = 3

    def getMove(self, currentState):
        frontierNodes = []
        expandedNodes = []

        rootNode = Node(None, currentState, 0, self.utility(currentState, {}), None)
        frontierNodes.append(rootNode)

        for i in range(self.DEPTH_LIMIT):
            nextNode = min(frontierNodes, key=lambda n: n.evaluation)
            expandedNodes.append(nextNode)

            frontierNodes.remove(nextNode)
            expandedNodes.append(nextNode)

            newNodes = self.expandNode(nextNode)
            frontierNodes.extend(newNodes)

        bestNode = min(frontierNodes, key=lambda n: n.evaluation)

        node = bestNode
        while node.parent is not None and node.depth > 1:
            node = node.parent

        return node.move


    
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


    ##
    #bestMove
    #Description: Gets the best move based on evaluation.
    #
    #Parameters:
    #   nodeList - a list of nodes for a given move
    #
    #Return: The best evaluated node
    ##
    def bestMove(self, nodeList):
        minMoves = min(node.evaluation for node in nodeList)
        bestNodes = [node for node in nodeList if node.evaluation == minMoves]
        return random.choice(bestNodes)

    def expandNode(self, node):
        moves = listAllLegalMoves(node.gameState)
        nodeList = []

        myWorkers = getAntList(node.gameState, node.gameState.whoseTurn, (WORKER,))
        preCarrying = {worker.UniqueID: worker.carrying for worker in myWorkers}

        for move in moves:
            gameState = getNextState(node.gameState, move)
            childNode = Node(move, gameState, node.depth+1, self.utility(gameState, preCarrying), node)
            nodeList.append(childNode)
        
        return nodeList

    ##
    #utility
    #Description: Calculates the evaluation score for a given game state.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #   preCarrying - A boolean value to see if a worker was carrying food before the move
    #
    #Return: The evaluation value for the move
    ##
    def utility(self, currentState, preCarrying):
        evaluation = 0.5  # baseline

        myWorkers = getAntList(currentState, currentState.whoseTurn, (WORKER,))
        foods = getConstrList(currentState, None, (FOOD,))
        homeSpots = getConstrList(currentState, currentState.whoseTurn, (TUNNEL, ANTHILL))
        myRSoldiers = getAntList(currentState, currentState.whoseTurn, (R_SOLDIER,))
        enemyInv = getEnemyInv(self, currentState)
        enemyWorkers = [ant for ant in enemyInv.ants if ant.type == WORKER]

        # Get current player's inventory
        myInv = getCurrPlayerInventory(currentState)

        # ----- Incentives / disincentives -----
        numWorkers = len(myWorkers)
        if numWorkers > 2:
            evaluation -= 0.05 * (numWorkers - 1)  # penalize having more than 1 worker

        # Stored food incentive
        evaluation += 0.02 * myInv.foodCount
        
        # ----- Range Soldier build incentive ------
        numRSoldiers = len(myRSoldiers)
        
        # reward building range soldiers when food is enough and there are not too many
        if myInv.foodCount >= 2 and numRSoldiers < 3:
            evaluation += 0.03 # small reward for having the resources to build one
            
        # reward having range soldiers
        if numRSoldiers > 0:
            evaluation += 0.04 * min(numRSoldiers, 3) * (1 - 0.1 * max(0, numRSoldiers - 3))
            
        # ----- Range Soldier attack incentive -------
        for rSoldier in myRSoldiers:
            if enemyWorkers:
                # find closest worker
                closestWorker = min(enemyWorkers, key=lambda w: stepsToReach(currentState, rSoldier.coords, w.coords))
                distToEnemy = stepsToReach(currentState, rSoldier.coords, closestWorker.coords)
                
                if distToEnemy <= 3:
                    evaluation += 0.06  # reward being in attack range
                elif distToEnemy <= 6:
                    evaluation += 0.02 * (6 - distToEnemy) / 6 # reward heaing to enemy
                    
            # reward for being in enemy territory
            if rSoldier.coords[1] >= 5:
                evaluation += 0.02

        # ----- Worker movement / pickup / delivery -----
        for worker in myWorkers:
            workerID = worker.UniqueID
            wasCarrying = preCarrying.get(workerID, False)

            closestFood = min(foods, key=lambda f: stepsToReach(currentState, worker.coords, f.coords))
            closestHome = min(homeSpots, key=lambda h: stepsToReach(currentState, worker.coords, h.coords))

            # Pickup / delivery incentive
            if not wasCarrying and worker.carrying:  # just picked up food
                evaluation += 0.05
            elif wasCarrying and not worker.carrying:  # just delivered food
                evaluation += 0.05
            else:
                # Reward moving toward target
                if not worker.carrying:  # heading to food
                    dist = stepsToReach(currentState, worker.coords, closestFood.coords)
                    evaluation += 0.005 * max(0, 10 - dist)
                else:  # heading to home
                    dist = stepsToReach(currentState, worker.coords, closestHome.coords)
                    evaluation += 0.005 * max(0, 10 - dist)

        # Clamp to [0,1]
        evaluation = max(0, min(1, evaluation)) 
        return ((1-evaluation)*10)



class Node:
    def __init__(self, move, gameState, depth, evaluation, parent):
        self.move = move
        self.gameState = gameState
        self.depth = depth
        self.evaluation = evaluation
        self.parent = parent
        
        
        
# ------------ TESTS ------------
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
        result = agent.utility(state, {})
      
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