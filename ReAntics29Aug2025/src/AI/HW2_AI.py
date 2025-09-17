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

        # Step 1: store pre-move carrying state for all my workers
        myWorkers = getAntList(currentState, currentState.whoseTurn, (WORKER,))
        preCarrying = {worker.UniqueID: worker.carrying for worker in myWorkers}

        # Step 2: generate simulated states and evaluate utility
        for move in moves:
            gameState = getNextState(currentState, move)
            gameStates.append(gameState)
            node = Node(move, gameState, 1, self.utility(gameState, preCarrying), None)
            nodeList.append(node)

        # Step 3: pick the best move
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
        maxChance = max(node.winChance for node in nodeList)
        bestNodes = [node for node in nodeList if node.winChance == maxChance]
        return random.choice(bestNodes)

    def utility(self, currentState, preCarrying):
        winChance = 0.5  # baseline

        myWorkers = getAntList(currentState, currentState.whoseTurn, (WORKER,))
        myRSoldiers = getAntList(currentState, currentState.whoseTurn, (R_SOLDIER,))
        foods = getConstrList(currentState, None, (FOOD,))
        homeSpots = getConstrList(currentState, currentState.whoseTurn, (TUNNEL, ANTHILL))

        # Get current player's inventory
        myInv = getCurrPlayerInventory(currentState)

        # ----- Incentives / disincentives -----
        numWorkers = len(myWorkers)
        if numWorkers > 2:
            winChance -= 0.05 * (numWorkers - 1)  # penalize having more than 1 worker

        # Stored food incentive
        winChance += 0.02 * myInv.foodCount

        # ----- Worker movement / pickup / delivery -----
        for worker in myWorkers:
            workerID = worker.UniqueID
            wasCarrying = preCarrying.get(workerID, False)

            closestFood = min(foods, key=lambda f: stepsToReach(currentState, worker.coords, f.coords))
            closestHome = min(homeSpots, key=lambda h: stepsToReach(currentState, worker.coords, h.coords))

            # Pickup / delivery incentive
            if not wasCarrying and worker.carrying:  # just picked up food
                winChance += 0.05
            elif wasCarrying and not worker.carrying:  # just delivered food
                winChance += 0.05
            else:
                # Reward moving toward target
                if not worker.carrying:  # heading to food
                    dist = stepsToReach(currentState, worker.coords, closestFood.coords)
                    winChance += 0.005 * max(0, 10 - dist)
                else:  # heading to home
                    dist = stepsToReach(currentState, worker.coords, closestHome.coords)
                    winChance += 0.005 * max(0, 10 - dist)

        # ----- Ranged Soldier incentives -----
        # Encourage having exactly 1 ranged soldier
        if len(myRSoldiers) > 1:
            winChance -= 0.05 * (len(myRSoldiers) - 1)
        elif len(myRSoldiers) == 0:
            winChance -= 0.05  # small penalty for having no ranged soldier
        
        enemyAnts = getAntList(currentState, 1 - currentState.whoseTurn, (WORKER, QUEEN))
        for r_soldier in myRSoldiers:
            if enemyAnts:
                closestEnemy = min(enemyAnts, key=lambda ea: stepsToReach(currentState, r_soldier.coords, ea.coords))
                dist = stepsToReach(currentState, r_soldier.coords, closestEnemy.coords)

                if dist >= 1:
                    # Reward moving closer
                    winChance += 0.01 * max(0, 10 - dist)





        # Clamp to [0,1]
        winChance = max(0, min(1, winChance))
        return winChance










    # def utility(self, currentState):
    #     """
    #     Returns a value between 0 and 1 representing how well we are doing.
    #     0 = lost, 1 = won.
    #     """
    #     myInv = getCurrPlayerInventory(currentState)
    #     enemyInv = getEnemyInv(self, currentState)

    #     winChance = 0.5  # start neutral

    #     # --- Food difference (strong incentive, max ±0.4) ---
    #     netFood = myInv.foodCount - enemyInv.foodCount
    #     winChance += 0.1 * netFood

    #     # # --- Queen health difference (moderate, max ±0.1) ---
    #     myQueenHP = myInv.getQueen().health
    #     enemyQueenHP = enemyInv.getQueen().health
    #     winChance += 0.1 * (myQueenHP - enemyQueenHP)

    #     # --- Workers ---
    #     myWorkers = getAntList(currentState, currentState.whoseTurn, (WORKER,))
    #     foods = getConstrList(currentState, None, (FOOD,))
    #     homeSpots = getConstrList(currentState, currentState.whoseTurn, (TUNNEL, ANTHILL))

    #     for worker in myWorkers:
    #         # Initialize flags if they don't exist yet
    #         if not hasattr(worker, "justSteppedOnFood"):
    #             worker.justSteppedOnFood = False
    #         if not hasattr(worker, "justSteppedOnHome"):
    #             worker.justSteppedOnHome = False

    #         closestFood = min(foods, key=lambda f: stepsToReach(currentState, worker.coords, f.coords))
    #         closestHome = min(homeSpots, key=lambda h: stepsToReach(currentState, worker.coords, h.coords))

    #         # Worker is going to food
    #         if not worker.carrying:
    #             # Step-on-home incentive (reset food flag)
    #             if worker.coords == closestHome.coords and not worker.justSteppedOnHome:
    #                 worker.justSteppedOnHome = True
    #                 worker.justSteppedOnFood = False
    #                 winChance += 0.05

    #             else:
    #                 # Distance-based incentive toward food
    #                 dist = stepsToReach(currentState, worker.coords, closestFood.coords)
    #                 winChance += 0.005 * (10 - dist)

    #         # Worker is going to home
    #         else:
    #             # Step-on-food incentive (reset home flag)
    #             if worker.coords == closestFood.coords and not worker.justSteppedOnFood:
    #                 worker.justSteppedOnFood = True
    #                 worker.justSteppedOnHome = False
    #                 winChance += 0.05

    #             else:
    #                 # Distance-based incentive toward home
    #                 dist = stepsToReach(currentState, worker.coords, closestHome.coords)
    #                 winChance += 0.005 * (10 - dist)

    #     if worker.coords == worker.prevCoords:
    #         winChance -= 0.05
    #     worker.prevCoords = worker.coords

    #     # --- Penalize excess units ---
    #     if len(myWorkers) > 1:
    #         winChance -= 0.3
    #     if len(getAntList(currentState, currentState.whoseTurn, (SOLDIER,))) > 1:
    #         winChance -= 0.3
    #     if len(getAntList(currentState, currentState.whoseTurn, (DRONE,))) > 1:
    #         winChance -= 0.3
    #     if len(getAntList(currentState, currentState.whoseTurn, (R_SOLDIER,))) > 1:
    #         winChance -= 0.3

    #     # --- Clamp to [0, 1] ---
    #     winChance = max(0, min(1, winChance))
    #     print(winChance)
    #     return winChance




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