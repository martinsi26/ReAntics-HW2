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
                    
            if enemyWorkers == None:
                enemyQueen = [ant for ant in enemyInv.ants if ant.type == QUEEN]
                distToEnemyQ = stepsToReach(currentState, rSoldier.coords, enemyQueen.coords)
                
                if distToEnemyQ <= 3:
                    evaluation += 0.6  # reward being in attack range
                elif distToEnemyQ <= 6:
                    evaluation += 0.2 * (6 - distToEnemy) / 6 # reward heaing to enemy
                    
            # reward for being in enemy territory
            if rSoldier.coords[1] > 5:
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
        # Create test ants with proper coordinates
        myAnts = [
            Ant((0,0), QUEEN, 0), 
            Ant((1,0), WORKER, 0), 
            Ant((2,1), R_SOLDIER, 0)
        ]
        enemyAnts = [
            Ant((0,9), QUEEN, 1), 
            Ant((1,8), WORKER, 1)
        ]
      
        anthill = Construction((0,0), ANTHILL)
        tunnel = Construction((1,0), TUNNEL)
        food = Construction((5,5), FOOD)
      
        myInv = Inventory(0, myAnts, [anthill, tunnel], 3)
        enemyInv = Inventory(1, enemyAnts, [Construction((0,9), ANTHILL)], 2)
        neutralInv = Inventory(2, [], [food], 0)
      
        # Create a proper board
        board = [[Location((x,y)) for y in range(10)] for x in range(10)]
        
        state = GameState(board, [myInv, enemyInv, neutralInv], 0, 0)
      
        agent = AIPlayer(0)
        result = agent.utility(state, {})
      
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 100)  # Updated range since we return (1-eval)*10
  
    def test_BestMove(self):
        n1 = Node("move1", None, 1, 2.0, None)  # Higher score = worse in minimax
        n2 = Node("move2", None, 1, 0.5, None)  # Lower score = better
        n3 = Node("move3", None, 1, 3.0, None)  
      
        agent = AIPlayer(0)
        result = agent.bestMove([n1, n2, n3])
        self.assertEqual(result, n2)  # Should pick the lowest score
      
    def test_getAttack_RangeSoldier(self):
        # Test range soldier prioritizes workers then queen
        myAnts = [Ant((2,4), R_SOLDIER, 0)]
        enemyAnts = [
            Ant((2,5), QUEEN, 1), 
            Ant((3,5), WORKER, 1),
            Ant((1,5), SOLDIER, 1)
        ]
      
        myInv = Inventory(0, myAnts, [], 0)
        enemyInv = Inventory(1, enemyAnts, [], 0)
        neutralInv = Inventory(2, [], [], 0)
      
        board = [[Location((x,y)) for y in range(10)] for x in range(10)]
        state = GameState(board, [myInv, enemyInv, neutralInv], 0, 0)
        
        agent = AIPlayer(0)
        
        # Test: Should attack worker first (let's debug which one it picks)
        enemyLocations = [(2,5), (3,5), (1,5)]  # Queen, Worker, Soldier
        result = agent.getAttack(state, myAnts[0], enemyLocations)
        # The method should pick any worker location - let's just check it finds a worker
        # First, verify there's a worker at the returned location
        found_worker = False
        for ant in enemyAnts:
            if ant.coords == result and ant.type == WORKER:
                found_worker = True
                break
        self.assertTrue(found_worker, f"Should attack a worker, but attacked {result}")
        
        # Test: Should attack queen when no workers
        enemyLocations = [(2,5), (1,5)]  # Queen, Soldier (no worker)
        result = agent.getAttack(state, myAnts[0], enemyLocations)
        self.assertEqual(result, (2,5))  # Should pick queen
        
    def test_utility_RangeSoldierRewards(self):
        # Test that range soldiers get rewards for being close to enemies
        myAnts = [
            Ant((0,0), QUEEN, 0),
            Ant((1,0), WORKER, 0), 
            Ant((5,3), R_SOLDIER, 0)  # Range soldier close to enemy
        ]
        enemyAnts = [
            Ant((0,9), QUEEN, 1), 
            Ant((5,6), WORKER, 1)  # Enemy worker 3 steps away from range soldier
        ]
        
        # Add food to prevent empty foods list error
        food1 = Construction((2,2), FOOD)
        food2 = Construction((8,8), FOOD)
      
        anthill = Construction((0,0), ANTHILL)
        tunnel = Construction((1,0), TUNNEL)
        myInv = Inventory(0, myAnts, [anthill, tunnel], 2)
        enemyInv = Inventory(1, enemyAnts, [], 2)
        neutralInv = Inventory(2, [], [food1, food2], 0)  # Add foods to neutral inventory
        
        board = [[Location((x,y)) for y in range(10)] for x in range(10)]
        state = GameState(board, [myInv, enemyInv, neutralInv], 0, 0)
        
        agent = AIPlayer(0)
        
        # Test with range soldier close to enemy (should get high reward)
        result_close = agent.utility(state, {})
        
        # Move range soldier far from enemy
        myAnts[2].coords = (0,1)  # Far from enemy worker
        result_far = agent.utility(state, {})
        
        # Range soldier close to enemy should have better (lower) evaluation score
        self.assertLess(result_close, result_far)
        
        
if __name__ == "__main__":
    unittest.main()