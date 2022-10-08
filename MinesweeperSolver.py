import numpy as np
from AdapterSolver import SolvingAdapter
from itertools import combinations

class Solver():

    def __init__(self, adapter):
        # adapter: reference to the solver adapter.
        # info_set: a set of all visible tiles that contain useful information.
        # to_mark: a set of all tiles which should be flagged.
        # to_reveal: a set of all tiles should be revealed.
        self.__adapter = adapter
        self.__info_set = set()
        self.__to_mark = set()
        self.__to_reveal = set()

    def info_setup(self):
        #Setup "info" set - the set of all visible tiles which contain
        #useful information (so should be passed to Gaussian elimination).
        visible_set = self.__adapter.get_visible()
        for id in visible_set:
            if not self.__adapter.is_redundant(id):
                if not self.__adapter.check_redundant(id):
                    self.__info_set.add(id)
    
    def generate_adjacency_matrix(self):
        useful_neighbours, tile_neighbours = \
            self.__adapter.get_useful_neighbours(self.__info_set)
        self.__column_to_id = {column: useful_neighbours[column] for column in \
                        range(len(useful_neighbours))}
        id_to_column = {id: column for column, id in self.__column_to_id.items()}
        number_of_cols = len(useful_neighbours) + 1
        
        gaussian_rows = set()
        # print(self.__info_set)

        for id in self.__info_set:
            # Get the neighbour ids for the tile.
            neighbour_ids = tile_neighbours[id]

            # Generate the respective columns for each of the neighbours in 
            # the matrix row.
            neighbour_columns = [id_to_column[id] for id in neighbour_ids]
            
            # Start with a 0 row vector, and flag the neighbours in the vector. 
            # The last column corresponds to the number of adjacent mines to
            # the current tile.
            new_row = [0] * number_of_cols 
            for column in neighbour_columns:
                new_row[column] = 1
            new_row[-1] = self.__adapter.get_adjacents(id)
            
            # Some tiles will contain information that has already been seen.
            # Example:
            # ? ? 1
            # n m 1
            # The 2 1s on right hand side both indicate the right unmarked tile
            # is a mine. No need to add them both to the matrix.
            new_row = tuple(new_row)
            if id == (1,2):
                print("(1,2) info:", new_row)
            gaussian_rows.add(new_row)

        gaussian_rows = list(gaussian_rows)
        aug_matrix = np.array(gaussian_rows, dtype= 'float')
        # print(aug_matrix)
        b = aug_matrix[:,-1]
        A = np.delete(aug_matrix, -1, 1)

        return A, b

    def gaussian_solver(self, A, b):
        #Gaussian component of solving.

        #Get row-echelon matrix and corresponding vector.
        rem, c = row_echelon(A, b)

        # print(rem, c)

        # info = [None for i in rem]
        info = {i: None for i in range(len(rem[0]))}

        for i in range(-1, - len(c) - 1, -1):

            row = rem[i]
            checksum = c[i]

            # print(i, row, checksum)

            #Non-trivial coefficient indices.
            row_coeff = {index: row[index] for index in range(len(row))}
            row_coeff_copy = row_coeff.copy() #Copy for iteration.

            # The tile identity may have been figured out previously, in a 
            # previous solve run. Iterate through the coefficients and fill
            # info with known ones.
            for index in row_coeff:
                tile_identity = info[index]
                if tile_identity == None:
                    tile_id = self.__column_to_id[index]
                    tile_identity = self.__adapter.get_tile_identity(tile_id)
                    info[index] = tile_identity

            # print(row_coeff)

            for index in row_coeff_copy:
                tile_identity = info[index]                    

                # If the tiles identity has been figured out, we adjust
                # the rest of the row to make sure we extract as much
                # information from it as possible.
                if tile_identity != None: 
                    coeff = row_coeff.pop(index) 
                    if tile_identity == 1:
                        checksum -= coeff
                    row[index] = 0 
                    
            zero_coeffs = [x for x in row if x == 0]

            if len(zero_coeffs) != len(row):

                # row_sum = sum(row)
                upper_bound = sum([x for x in row if x > 0])
                lower_bound = sum([x for x in row if x < 0])

                # The simplest case which requires no prior information is 
                # when the checksum of the row is equal to either bound. In
                # such a case, all the elements with a 
                # +ve (upper)/ -ve (lower) coefficient are 1, and the 
                # -ve/+ve coefficients are 0.
                
                # print(row, checksum, upper_bound, lower_bound)

                if checksum == upper_bound:
                    for index in row_coeff:
                        if row_coeff[index] > 0:
                            info[index] = 1
                        elif row_coeff[index] < 0:
                            info[index] = 0
                elif checksum == lower_bound:
                    for index in row_coeff:
                        if row_coeff[index] < 0:
                            info[index] = 1
                        elif row_coeff[index] > 0:
                            info[index] = 0

            if row[0] != 0:
                print("(0,1) status")
                print("current info:", info)
                print(row)
                print(zero_coeffs)
                print(checksum)
        
        print("Da info:", info)
        print("Conversion", self.__column_to_id)

        # And now (with the editor position opening up), having collected
        # all the information, we pack it neatly for the adapter to pass it.
        for index in info:
            if info[index] != None:
                tile_id = self.__column_to_id[index]
                if info[index] == 1:
                    self.__to_mark.add(tile_id)
                elif info[index] == 0:
                    self.__to_reveal.add(tile_id)

    def partial_satisfaction_solve(self):
        # There isnt a single possible row echelon form of the augmented
        # matrix - it's possible that the generated matrix may not see 
        # a piece of information that it could, if rows were added in a 
        # different order. We therefore check additionally if any 
        # non-redundant tiles satisfy their adjacency, but don't have
        # a revealed tile.

        # This is a bodge job for time being, as I am not using REDUCED
        # row echelon form. With reduction, will always be able to find
        # the maximum amount of information.

        for tile_id in self.__info_set:
            print(tile_id)
            if self.__adapter.partially_satisfied(tile_id):
                id_set = set()
                id_set.add(tile_id)
                useful_neighbours, adjacency = self.__adapter.get_useful_neighbours(id_set)
                # print(useful_neighbours)
                for neighbour_id in useful_neighbours:
                    if not self.__adapter.is_marked(neighbour_id):
                        self.__to_reveal.add(neighbour_id)

    def get_moves(self):
        return self.__to_reveal, self.__to_mark

    def reset(self):
        self.__info_set = set()
        self.__to_mark = set()
        self.__to_reveal = set()

    def solve(self):
        self.reset()
        self.info_setup()
        print("Is (1,2) in the set",  bool((1,2) in self.__info_set))
        A, b = self.generate_adjacency_matrix()
        self.gaussian_solver(A, b)
        self.partial_satisfaction_solve()
        print("To mark:", self.__to_mark)
        print("To reveal:", self.__to_reveal)
        return self.get_moves()

    def guess(self):
        # Take a calculated guess - the tile which is likeliest to not
        # have a mine should be revealed/the mine which is likeliest 
        # to have a mine should be marked, and gaussian elimination be
        # reapplied.
        # There are 2^n possible configurations, where n is the remaining
        # number of tiles. Can be made more efficient by splitting
        # boundaries into independent components.
        
        # 1. Get a set of all remaining hidden tiles.
        # 2. Get the boundary information.
        # 3. Generate a configuration, subject to the total number of 
        #    remaining tiles.
        # 4. Check if said configuration is valid (satisfies boundary)
        # 5. If valid, increment counters for each tile being hidden/
        #    visible.
        # 6. Determine the tile with the highest counter of being hidden/
        #    visible.
        # 7. Mark/reveal the likeliest tile and add guess to the board.
        #    Can now rerun Gaussian, with new information.
        
        # Works great if the there's only a few remaining tiles on the
        # boundary, not so great otherwise...

        hidden_tiles = self.__adapter.get_hidden_tiles()

        print("Hidden tiles", hidden_tiles)
        print("")

        boundary_neighbours, adjacency_dict = \
            self.__adapter.get_useful_neighbours(self.__info_set)

        total_legit_combs = 0

        #Running total for each id of tile.
        comb_frequency = {hidden_tile: 0 for hidden_tile in hidden_tiles \
                          if hidden_tile in boundary_neighbours}
        mark_frequency = comb_frequency.copy()
        # mark_frequency = {hidden_tile: 0 for hidden_tile in hidden_tiles \
        #                   if hidden_tile in boundary_neighbours}

        #Indices used in combinations correspond to hidden tile ids 1 to 1.
        index_to_id = {i: tile_id for i, tile_id in \
                       enumerate(comb_frequency.keys())}
        id_to_index = {tile_id: index for index, tile_id\
                       in index_to_id.items()}

        boundary_conditions = set()

        for hint_tile_id in adjacency_dict:
            adjacents = self.__adapter.get_adjacents(hint_tile_id)
            adj_key_list = adjacency_dict[hint_tile_id]
            to_guess_key_list = [tile_id for tile_id in adj_key_list if tile_id in hidden_tiles]
            adj_id_list = [id_to_index[tile_id] for tile_id in to_guess_key_list]
            adjacents = adjacents + (len(to_guess_key_list) - len(adj_key_list))
            new_info = tuple(adj_id_list + [adjacents])
            boundary_conditions.add(new_info)

        boundary_conditions = list(boundary_conditions)

        max_freq = 0
        max_freq_id = None
        move_type = 0

        #Generating all possible mine configurations 

        total_mines = self.__adapter.remaining_mines()

        for mines in range(1, min(total_mines + 1, len(new_info))):
            mine_combs = combinations(hidden_tiles, mines)

            print(list(combinations(hidden_tiles, mines)))

            # print("Boundary conditions:", boundary_conditions)

            #Checking whether each configuration is legit.
            for config in mine_combs:
                config = config[0]
                config_dict = {i: 1 if i in config else 0 for i in \
                            range(len(index_to_id))}
                conditions_satisfied = True
                counter = 0
                # print(config)
                # print(config_dict)
                while conditions_satisfied and counter < len(boundary_conditions):
                    next_condition = boundary_conditions[counter]
                    # print("Current condition", next_condition)
                    mine_sum = sum([config_dict[j] for j in next_condition[:-1]])
                    if mine_sum != next_condition[-1]:
                        conditions_satisfied = False
                    counter += 1
                
                if conditions_satisfied:
                    total_legit_combs += 1
                    for index in index_to_id:
                        tile_id = index_to_id[index]
                        if index in config_dict:
                            comb_frequency[tile_id] += 1
                            if comb_frequency[tile_id] > max_freq:
                                max_freq = comb_frequency[tile_id]
                                max_freq_id = tile_id
                                move_type = 0
                        else:
                            mark_frequency[tile_id] += 1
                            if mark_frequency[tile_id] > max_freq:
                                max_freq = mark_frequency[tile_id]
                                max_freq_id = tile_id
                                move_type = 1

        return max_freq_id, move_type

    def heuristic_guess(self):
        # Instead of going through every possible combination, each
        # adjacent tile contributes to an average mine probability. 
        # The tile with the lowest mine probability is revealed (this
        # gets you more information so a Gaussian method could 
        # potentially be applied).

        hidden_tiles = self.__adapter.get_hidden_tiles()

        boundary_neighbours, adjacency_dict = \
            self.__adapter.get_useful_neighbours(self.__info_set)        

        remaining_mines = self.__adapter.remaining_mines()
        initial_prob = remaining_mines / len(hidden_tiles)
        tile_estimates = {hidden_tile: initial_prob for hidden_tile \
                          in hidden_tiles}

        print(tile_estimates)

        tile_counters = {hidden_tile: 1 for hidden_tile in hidden_tiles}

        for hint_tile_id in adjacency_dict:
            adjacents = self.__adapter.get_adjacents(hint_tile_id)
            to_guess_key_list = [tile_id for tile_id in \
                adjacency_dict[hint_tile_id] if tile_id in hidden_tiles]
            adjacents = adjacents + (len(to_guess_key_list) \
                                    - len(adjacency_dict[hint_tile_id]))
            for neighbour in to_guess_key_list:
                tile_estimates[neighbour] += adjacents / len(to_guess_key_list)
                tile_counters[neighbour] += 1

        tile_probs = {hidden_tile: tile_estimates[hidden_tile] / tile_counters[hidden_tile]\
                      for hidden_tile in hidden_tiles}

        minimum_prob = 1
        to_mark_id = (0,0)
        for tile_id in tile_probs:
            next_prob = tile_probs[tile_id]
            if next_prob < minimum_prob:
                to_mark_id = tile_id
                minimum_prob = next_prob

        return to_mark_id

def row_echelon(A, b):
    #A is the matrix representing the mine adjacencies.
    #b is the adjacency number corresponding to each row's guess value.
    #Adapted from https://math.stackexchange.com/questions/3073083/how-to-reduce-matrix-into-row-echelon-form-in-numpy
    # (added b vector, A matrix completely ripped off)

    # if matrix A has no columns or rows,
    # it is already in REF, so we return itself
    r, c = A.shape
    if r == 0 or c == 0:
        return A, b

    # we search for non-zero element in the first column
    for i in range(len(A)):
        if A[i,0] != 0:
            break
    else:
        # if all elements in the first column is zero,
        # we perform REF on matrix from second column
        B, b = row_echelon(A[:,1:], b)
        # and then add the first zero-column back
        return np.hstack([A[:,:1], B]), b

    # if non-zero element happens not in the first row,
    # we switch rows
    if i > 0:
        ith_row = A[i].copy()
        A[i] = A[0]
        A[0] = ith_row

        ith_x = b[i].copy()
        b[i] = b[0]
        b[0] = ith_x

    # we divide first row by first element in it, and the
    # corresponding row in the x vector.
    b[0] = b[0] / A[0,0]
    A[0] = A[0] / A[0,0]
    # we subtract all subsequent rows with first row (it has 1 now as first element)
    # multiplied by the corresponding element in the first column

    b[1:] -= (A[1:,0:1] * b[0]).flatten()
    A[1:] -= A[0] * A[1:,0:1]

    # we perform REF on matrix from second row, from second column
    B, c = row_echelon(A[1:,1:], b[1:])

    # we add first row and first (zero) column, and return
    return np.vstack([A[:1], np.hstack([A[1:,:1], B])]), np.hstack([b[0], c])

if __name__ == "__main__":

    A = np.array([[1,1,0,0,0],
                  [1,1,1,0,0],
                  [0,1,1,1,0],
                  [0,0,1,1,1],
                  [0,0,0,1,1]], dtype='float')

    b = np.array([1,2,2,2,1], dtype='float')

    # B, c = row_echelon(A, b)

    # print(B, c)

    solver = Solver("Lol")

    solver.gaussian_solver(A, b)