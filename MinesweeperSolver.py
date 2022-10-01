import numpy as np

class Solver():

    def __init__(self, adapter):
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
                    visible_set.add(id)
    
    def generate_adjacency_matrix(self):
        useful_neighbours, tile_neighbours = \
            self.__adapter.get_useful_neighbours(self.__info_set)
        self.__column_to_id = {column: useful_neighbours[column] for column in \
                        range(len(useful_neighbours))}
        id_to_column = {id: column for column, id in self.__column_to_id.items()}
        number_of_cols = len(useful_neighbours) + 1
        
        gaussian_rows = set()

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
            # n 1 1
            # The 2 1s on right hand side both indicate the right unmarked tile
            # is a mine. No need to add them both to the matrix.
            gaussian_rows.add(new_row)

        gaussian_rows = list(gaussian_rows)
        aug_matrix = np.array(gaussian_rows, dtype= 'float')
        b = aug_matrix[:,-1]
        A = np.delete(aug_matrix, -1, 1)

        return A, b

    def gaussian_solver(self, A, b):
        #Gaussian component of solving.

        #Get row-echelon matrix and corresponding vector.
        rem, c = row_echelon(A, b)

        new_info = [None for i in rem]

        for i in range(-1, - len(c) - 1, -1):
            row = rem[i]
            adjacents = c[i]
            # if sum(row) == adjacents:            


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