import numpy as np
from AdapterSolver import SolvingAdapter

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
        
        print("Da info:", info)

        # And now (with the editor position opening up), having collected
        # all the information, we pack it neatly for the adapter to pass it.
        for index in info:
            if info[index] != None:
                tile_id = self.__column_to_id[index]
                if info[index] == 1:
                    self.__to_mark.add(tile_id)
                elif info[index] == 0:
                    self.__to_reveal.add(tile_id)

    def get_moves(self):
        return self.__to_reveal, self.__to_mark

    def reset(self):
        self.__info_set = set()
        self.__to_mark = set()
        self.__to_reveal = set()

    def solve(self):
        self.reset()
        self.info_setup()
        A, b = self.generate_adjacency_matrix()
        self.gaussian_solver(A, b)
        print("To mark:", self.__to_mark)
        print("To reveal:", self.__to_reveal)
        return self.get_moves()

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