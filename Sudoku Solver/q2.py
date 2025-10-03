"""
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""

from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])

        self.goals = []
        self.boxes = []
        self.player_start = None
        tmp=[]
        for i in range(self.M):
            tmp.append('#')
        self.grid = [tmp]+[tmp]+self.grid+[tmp]+[tmp]
        self.N+=4
        self.M+=4
        self.grid = [['#','#']+row[:]+['#','#'] for row in self.grid]



        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start
        self._parse_grid()

        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        for i in range(self.N):
            for j in range(self.M):
                if self.grid[i][j] == 'P':
                    self.player_start = (i, j)
                elif self.grid[i][j] == 'B':
                    self.boxes.append((i, j))
                elif self.grid[i][j] == 'G':
                    self.goals.append((i, j))

    # ---------------- Variable Encoding ----------------
    def var_player(self, x, y, t):
        """
        Variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        return int(17*17*17*t + 17*(x+1) + (y+1))

    def var_box(self, b, x, y, t):
        """
        Variable ID for box b at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        return int(17*17*17*(t) + 17*17*b + 17*(x+1) + (y+1))

    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        # TODO: Add constraints for:
        # 1. Initial conditions
        # 2. Player movement
        # 3. Box movement (push rules)
        # 4. Non-overlap constraints
        # 5. Goal conditions
        # 6. Other conditions

        # initial conditions
        self.cnf.append([self.var_player(self.player_start[0],self.player_start[1],0)])
        b = 1
        for (i,j) in self.boxes:
            self.cnf.append([self.var_box(b,i,j,0)])
            b+=1

        # goal conditions
        for b in range(1,self.num_boxes+1):
            goals=[]
            for i,j in self.goals:
                goals.append(self.var_box(b,i,j,self.T))
            self.cnf.append(goals)

        # Wall condition 
        for m in range(self.M):
            for n in range(self.N):
                    if self.grid[n][m]=='#':
                        for t in range(self.T+1):
                            self.cnf.append([-self.var_player(n,m,t)])      # player cannot be at wall position
                            for b in range(1,self.num_boxes+1):
                                self.cnf.append([-self.var_box(b,n,m,t)])   # boxes cannot be at wall position

        # player movement
        for i in range(2,self.N-2):
            for j in range(2,self.M-2):
                for t in range(self.T):
                    lis = [-self.var_player(i,j,t),self.var_player(i,j+1,t+1),self.var_player(i-1,j,t+1),self.var_player(i+1,j,t+1),self.var_player(i,j-1,t+1),self.var_player(i,j,t+1)]
                    self.cnf.append(lis)

        # player one position
        for x in range(self.N):
            for y in range(self.M):
                for i in range(self.N):
                    for j in range(self.M):
                        for t in range(self.T+1):
                            if x!=i or y!=j:
                                self.cnf.append([-self.var_player(x,y,t),-self.var_player(i,j,t)])
        # box one position
        for t in range(self.T+1):
            for b in range(1,self.num_boxes+1):
                for x in range(self.N):
                    for y in range(self.M):
                        for i in range(self.N):
                            for j in range(self.M):
                                    if x!=i or y!=j:
                                        self.cnf.append([-self.var_box(b,x,y,t),-self.var_box(b,i,j,t)])
        # player,box no collision
        for t in range(self.T+1):
            for i in range(self.N):
                for j in range(self.M):
                    l = []
                    l.append(self.var_player(i,j,t))
                    for b in range(1,self.num_boxes+1):
                        l.append(self.var_box(b,i,j,t))
                    for var in l:
                        for v in [tmp for tmp in l if tmp!=var]:
                            self.cnf.append([-var,-v])

        # box movement
        for b in range(1,self.num_boxes+1):
            for t in range(self.T):
                for i in range(2,self.N-2):
                    for j in range(2,self.M-2):
                        l1 = [-self.var_box(b,i,j,t+1)]
                        l2 = [self.var_box(b,i,j,t)]
                        l3 = [self.var_box(b,i+1,j,t),self.var_player(i+2,j,t),self.var_player(i+1,j,t+1)]
                        l4 = [self.var_box(b,i-1,j,t),self.var_player(i-2,j,t),self.var_player(i-1,j,t+1)]
                        l5 = [self.var_box(b,i,j+1,t),self.var_player(i,j+2,t),self.var_player(i,j+1,t+1)]
                        l6 = [self.var_box(b,i,j-1,t),self.var_player(i,j-2,t),self.var_player(i,j-1,t+1)]
                        for c1 in l1:
                            for c2 in l2:
                                for c3 in l3:
                                    for c4 in l4:
                                        for c5 in l5:
                                            for c6 in l6:
                                                self.cnf.append([c1,c2,c3,c4,c5,c6])
                    
        return self.cnf

def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """
    N, M, T = encoder.N, encoder.M, encoder.T
    N=N+4
    M=M+4
    t=0
    i1=0
    j1=0
    ls=[]
    for x in range(N):
        for y in range(M):
            if(17*17*17*(t) + 17*(x+1) + (y+1) in model):
                i1=x
                j1=y
    for t in range(T+1):
        if(17*17*17*t + 17*(i1+2) + j1+1 in model):
            i1+=1
            ls.append('D')
        elif(17*17*17*t+17*(i1+1)+j1+2 in model):
            j1+=1
            ls.append('R')
        elif(17*17*17*t+17*(i1)+j1+1 in model):
            i1-=1
            ls.append('U')
        elif(17*17*17*t+17*(i1+1)+j1 in model):
            j1-=1
            ls.append('L')
             
    return ls


def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.

    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()

    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1

        model = solver.get_model()
        if not model:
            return -1

        return decode(model, encoder)