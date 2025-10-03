"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""
    cnf = CNF()
    for i in range(1,10):
        for j in range(1,10):
            if(grid[i-1][j-1]!=0):
                cnf.append([100*i+10*j+grid[i-1][j-1]])
    
    for i in range(1,10):
        for k in range(1,10):
            lis = []
            lis1 = []
            for _ in range(1,10):
                x = 100*i + k
                lis.append(x+_*10)
                x = 10*i + k
                lis1.append(x+_*100)
            cnf.append(lis)
            cnf.append(lis1)
    
    for i in range(1,10):
        for j in range(1,10):
            for k1 in range(1,10):
                for k in range(1,10):
                    if(k!=k1):
                        cnf.append([-(100*i + 10*j + k1),-(100*i + 10*j + k)])
    
    lis=[]
    for i in [1,4,7]:
        for j in [1,4,7]:
            lis.append((i,j))
    for (i,j) in lis:
        for k in range(1,10):
            x = 100*i + 10*j + k
            l1=[]
            for m in [0,1,2]:
                for n in [0,1,2]:
                    l1.append(x+100*m+10*n)
            cnf.append(l1)
    
    sudoku_sol = [list(i) for i in grid]
    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf.clauses)
        solver.solve()
        model = solver.get_model()
        for x in model:
            if(x>0):
                sudoku_sol[int(x/100-1)][(int(x/10)%10)-1] = x%10
        return sudoku_sol