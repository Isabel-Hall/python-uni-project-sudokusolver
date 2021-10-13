# python-uni-project-sudokusolver
Uni project from AI module to create a sudoku solver from scratch


solver_backtracking.py contains the Solver class to perform a backtracking search with constraint satisfaction and a minimum value heuristic.
submission_code.py contains code to run the solver on several example sudokus.
data directory contains the example sudokus and their solutions.


Here is the accompanying text for the submission giving an outline of the code and algorithms used:

The algorithm used is primarily a depth first backtracking search with constraint satisfaction. 
It is adapted from the pseudocode from Russell and Norvig(1) and the Eight Queens Revisited activity from moodle(2).
Sudokus are clearly a constraint satisfaction problem with the 9x9 grid giving 81 variables, each with a domain of the numbers 1-9 as possible assignments. The constraints are that each specified area (row, column, 3x3 square) must contain 1-9 exactly once.
I chose a backtracking search rather than a local search as sudoku solving is highly based on deductions to find the only solution. The reason for this choice is that the number of potential assignments is huge and a local search, such as hill-climbing, is likely to get stuck at many local minima before finding the solution, especially for difficult sudokus with a lot of unknown variables.
Sudoku is different from other contraint satisfaction problems such as the eight queens problem as there is only one solution to the puzzle rather than trying to find a valid configuration out of many options. I therefore felt that a systematic approach would be more consistent in how long it takes to reach the solution and, given the properties of a sudoku puzzle, a backtracking search with constraint satisfaction would be a sensible way to approach this.

In order to efficiently keep track of the state of the domain at each cell in the sudoku, my code uses a 3D numpy array of bools where the x- and y-axes correspond to the same x- and y-axes in the sudoku and the z-axis records the possible values for that cell. Each 0-8 index in the z-axis corresponds to the numbers 1-9, so if the bool at the 0th index is True for a particular coordinate that means 1 is a valid option for that cell in the sudoku.
This set up for the domain allows me to use of a lot of functions in numpy, such as using argwhere to identify the index of the only remaining True element and therefore the value of a cell in the sudoku. Another example is easily being able to calculate if any cells have only one option or have run out of options by summing the z-axis of the domain.

My sudoku solver is wrapped in a Solver class that takes a sudoku as a numpy array as the input, and the first time it is initialised it will create the domain by propagating the contraints already imposed by the partially filled sudoku. This ensures all the variables are arc-consistent with each other. After this initial creation of the domain it then checks if any cells can be filled in straight away by looking for singletons with only one remaining value, this is sufficient to solve the easy or very easy sudokus without having to carry out any searches.

The backtracking search function will return "None" if an invalid state is reached or will recurse with a new Solver object, that takes the current sudoku and domain as inputs. This therefore performs a depth first backtracking search as when "None" is returned the solver moves onto the next possible value for the previous assignment.

At this point the solver could solve all of the sudokus, or determine when a solution was impossible, but it was not able to solve the hard sudokus in the timeframe, with some of them taking several minutes to reach a conclusion. To improve this time I added in a minimum-remaining-value heuristic when choosing the next cell to assign values to. Previously this had been selected at random but now I select one with the lowest possible number of values, though excluding those with one value remaining in the domain as these are the cells that already have a value assigned to them. This acts to prune the search tree by quickly identifying which assignments cause an empty domain and are therefore invalid.
This was sufficient to get the time taken to solve most sudokus to less than a second and to solve the hard sudokus in 1-2 seconds. 
The values that are evaluated for a particular cell are tried in ascending order, I considered if there was a better way to select the next value but ultimately I did not change this. Heuristics, such as least-constrained-variable, as described in the Russell and Norvig textbook are useful when trying to come up with a valid solution out of several possibilities. It keeps as much freedom as possible in the remaining variables to increase the chance that a solution will be found quickly. However, as there is either one correct solution or none for sudokus all values would need to be tried anyway so this is not a useful heuristic for this case.

If I had more time to work on my solver, I could add some further detail into the function that checks for a valid assignment of variables. Currently it checks that there are no domains left without any possible values but does not, for instance, check that 3 cells only have 2 possible options between them. A Maintaining Arc Consistency algorithm can propagate constraints forward and will recognise that a variable will inevitably have its domain reduced to no possible options and therefore the current assignment is invalid. 




1. Russell, S, & Norvig, P 2016, Chapter 6 Constraint Satisfaction Problems, In: Artificial Intelligence: a Modern Approach, Global Edition, Pearson Education, Limited, Harlow, United Kingdom. Available from: ProQuest Ebook Central. [12 March 2021].

2. Week 2: Informed Search and Constraint Satisfaction, 2020, Bath University Moodle, viewed 12 March 2021, <https://moodle.bath.ac.uk/course/view.php?id=59592&section=6>
