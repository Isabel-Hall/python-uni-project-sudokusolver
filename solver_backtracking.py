import copy
import random
import time
import numpy as np

class Solver:
    def __init__(self, sudoku, domain_grid=None):
        self.sudoku = sudoku
        if domain_grid is None:
            # Creates a 3D array to store the possible values for each cell in the sudoku
            # Possible values are stored as True with the indices 0-8 representing the value itself (so offset by 1).
            self.domain_grid = np.zeros((9, 9, 9)).astype(bool)
            self.update_known_values()
            self.sudoku = self.find_and_update_blanks()
        else:
            self.domain_grid = domain_grid
            
    def update_known_values(self):
        # Finds the coordinates of the zeros in the sudoku
        # Updates the corresponding indices in the domain grid so all possible values set to True
        zero_idx = np.argwhere(self.sudoku == 0)
        self.domain_grid[
            zero_idx[:, 0],
            zero_idx[:, 1],
            :
        ] = True
        
        # Gets the non-zero values
        # Updates the domain grid so only the correct index for that value is set to True
        non_zero_idx = np.argwhere(self.sudoku > 0)
        values = self.sudoku[
            non_zero_idx[:, 0],
            non_zero_idx[:, 1]
        ]
        self.domain_grid[
            non_zero_idx[:, 0],
            non_zero_idx[:, 1],
            values - 1
        ] = True
        
        
    def find_and_update_blanks(self): 
        # Used when initialising the domain grid, removes values that are already present in the row/column/3x3 square for each cell
        # Any unknown cells with only one option are then updated
        # This results in some of the simple sudokus being solved without having to carry out a search
        sudoku_copy = copy.deepcopy(self.sudoku)
        zero_idx = np.argwhere(self.sudoku == 0)
        # Searches surrounding cells for each 0 in the sudoku to work out remaining options
        for row, column in zero_idx:
            values_to_remove = set()
            values_to_remove.update(self.row_values_to_remove(row))
            values_to_remove.update(self.column_values_to_remove(column))
            values_to_remove.update(self.square_values_to_remove(row, column))
            self.update_possibilities(row, column, values_to_remove)
            sudoku_copy = self.update_if_singleton_cell(row, column, sudoku_copy)
        return sudoku_copy
    
    def row_values_to_remove(self, i):
        # Returns a set of the values already present in the given row i
        # Used by find_and_update_blanks() above
        taken_values = set()
        for j in range(0, len(self.sudoku[0])):
            taken_values.add(self.sudoku[i, j])
        return taken_values
    
    def column_values_to_remove(self, j):
        # Returns a set of the values already present in the given column j
        # Used by find_and_update_blanks() above
        taken_values = set()
        for i in range(0, len(self.sudoku)):
            taken_values.add(self.sudoku[i, j])
        return taken_values

    def square_values_to_remove(self, i, j):
        # Returns a set of the values already present in the surrounding 3x3 square
        # Used by find_and_update_blanks() above
        taken_values = set()
        for y in range((i//3)*3, ((i//3)*3)+3):
            for x in range((j//3)*3, ((j//3)*3)+3):
                taken_values.add(self.sudoku[y, x])
        return taken_values
    
    def update_possibilities(self, row, column, val_set):
        # Used by find_and_update_blanks() above
        # Removes any values that are already taken by setting the relevant indices in the domain grid to False
        idx = set()
        for val in val_set:
            if (val - 1) >= 0:
                idx.add(val - 1)
        for i in range(0, 9):
            if i in idx:
                self.domain_grid[row, column, i] = False
                
    def update_if_singleton_cell(self, row, column, sudoku):
        # Used by find_and_update_blanks() above
        # Returns an updated sudoku where any blanks with only one possible value have been filled in
        if self.domain_grid[row, column].sum() == 1:
            idx = np.argwhere(self.domain_grid[row, column])
            sudoku[row, column] = idx[0,0] + 1
        return sudoku
    
    
    def check_for_singletons_and_update(self):
        # More complex function used in the search function to identify and update any cells with a single possibility
        # Returns a True/False if there are singletons present and an updated Solver object if there are
        zero_idx = np.argwhere(self.sudoku == 0)
        zero_domains = self.domain_grid[
            zero_idx[:, 0],
            zero_idx[:, 1],
            : ]

        #finds if any 0s have only 1 option
        if (zero_domains.sum(axis=1) == 1).any():
            singletons = zero_idx[zero_domains.sum(axis=1) == 1]
            values = np.argwhere(self.domain_grid[
                singletons[:,0],
                singletons[:,1]
                ])[:,1] + 1
         
            new_solver = self.set_value(singletons[0,0], singletons[0,1], values[0])
           
            if len(singletons) > 1:
                for i in range(1, len(singletons)):
                    new_solver = new_solver.set_value(singletons[i,0], singletons[i,1], values[i])
            # Recursively calls itself to ensure no new singletons created by updating values for the current ones
            further_singletons, updated_solver = new_solver.check_for_singletons_and_update()
            if further_singletons:
                new_solver = updated_solver
            return True, new_solver
        return False, None

    
    def set_value(self, row, column, value):
        # Updates a given cell in the sudoku with a value then updates the possible values for related cells
        sudoku_copy = copy.deepcopy(self.sudoku)
        domain_copy = copy.deepcopy(self.domain_grid)
        sudoku_copy[row, column] = value
        domain_copy[row, column, :] = False        
        # update other cells with new contraint
        domain_copy[row, : , (value - 1)] = False
        domain_copy[ : , column, (value - 1)] = False
        lower_bound_row = (row // 3)*3
        upper_bound_row = lower_bound_row + 3
        lower_bound_column = (column // 3) * 3
        upper_bound_column = lower_bound_column + 3
        domain_copy[
            lower_bound_row : upper_bound_row,
            lower_bound_column : upper_bound_column,
            value - 1
        ] = False
        # after updating other domains, set chosen value to true
        domain_copy[row, column, (value - 1)] = True
        # create and return new state with new sudoku and domain grid 
        new_solver = Solver(sudoku_copy, domain_copy)
        return new_solver
    
    
    def all_diff(self):
        # Checks there are no repeated values for each row, column and 3x3 square
        # Checks rows first
        for i in range(0, len(self.sudoku[0])):
            if not self.is_unique_1d_array(self.sudoku[i]):
                return False
        # Checks columns
        for j in range(0, len(self.sudoku)):
            if not self.is_unique_1d_array(self.sudoku[:, j]):
                return False
        # Checks 3x3 squares
        arr_list = [
            self.sudoku[0:3, 0:3].flatten(),
            self.sudoku[0:3, 3:6].flatten(),
            self.sudoku[0:3, 6:9].flatten(),
            self.sudoku[3:6, 0:3].flatten(),
            self.sudoku[3:6, 3:6].flatten(),
            self.sudoku[3:6, 6:9].flatten(),
            self.sudoku[6:9, 0:3].flatten(),
            self.sudoku[6:9, 3:6].flatten(),
            self.sudoku[6:9, 6:9].flatten(),
        ]
        for k in arr_list:
            if not self.is_unique_1d_array(k):
                return False
        return True

    def is_unique_1d_array(self, array):
        # Checks a given array contains no repeated values (excluding zeros)
        # Used by all_diff() above
        array_without_zeros = array[array > 0]
        values, counts = np.unique(array_without_zeros, return_counts=True)
        if (counts > 1).any():
            return False
        return True
    

    def is_goal(self):
        # Returns True once a valid sudoku is reached
        return (not (self.sudoku == 0).any()) and self.is_valid()
    
    def is_valid(self):
        # Checks the sudoku and domain grid are valid by ensuring all cells have at least one option and no repeated values in the sudoku
        number_of_options = self.domain_grid.sum(axis=2)
        return (not (number_of_options == 0).any()) and self.all_diff()

    
    def get_options(self, row, column):
        # Returns the possible values for a given cell
        idx = np.argwhere(self.domain_grid[row, column])
        return (idx.flatten() + 1)
    
    
    def choose_next_cell(self):
        # Returns a coordinate for an unknown cell so the search algorithm can then try the possible values 
        # Chooses a cell with the minimum remaining value for the number options
        
        # sum of the Z-axis of domain grid, number of options for each cell
        num_options = self.domain_grid.sum(axis=2)
        # coordinates where num_options is more than 1
        idx = np.argwhere(num_options > 1)
        # Gets the number of options at each cell, excluding those with only one option, and finds what the smallest number is
        n_opt_gt_1 = num_options[idx[:, 0], idx[:, 1]] 
        min_val_pos = np.argmin(n_opt_gt_1) 
        # Finds the coordinates for this cell with the minimum remaining value and returns this
        min_val_idx = idx[min_val_pos, :] 
        return min_val_idx
    
    
    def backtracking_search(self):
        # Backtracking search using constraint satisfaction
        if not self.is_valid():
            return None
        elif self.is_goal():
            return self
        else:
            [row, column] = self.choose_next_cell()
            values = self.get_options(row, column)
            for value in values:
                new_state = self.set_value(row, column, value)
                singletons_present, updated_state = new_state.check_for_singletons_and_update()
                if singletons_present:
                    new_state = updated_state
                if new_state.is_goal():
                    return new_state
                elif new_state.is_valid():
                    deep_state = new_state.backtracking_search()
                    if (deep_state is not None) and (deep_state.is_goal()):
                        return deep_state
            return None