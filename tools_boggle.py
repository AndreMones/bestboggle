"""score boggle: scores a boggle board.
Andre Mones
Credits:
"""
import doctest
import config

# Possible search outcomes
NOPE = "Nope"       # Not a match, nor a prefix of a match
MATCH = "Match"     # Exact match to a valid word
PREFIX = "Prefix"   # Not an exact match, but a prefix (keep searching!)

# Special character in position that is
# already in use
IN_USE = "@"

# Max word length is 16, so we can just list all
# the point values.
#
#         0  1  2  3  4  5  6  7  8
POINTS = [0, 0, 0, 1, 1, 2, 3, 5, 11,
          11, 11, 11, 11, 11, 11, 11, 11 ]
#          9  10  11  12  13  14  15  16
        

def allowed(s: str) -> bool:
    """Is s a legal Boggle word?

    >>> allowed("am")  ## Too short
    False

    >>> allowed("de novo")  ## Non-alphabetic
    False

    >>> allowed("about-face")  ## Non-alphabetic
    False
    """
    # I thought about checking if len(s) > config.N_ROWS * config.N_COLS, but opted not to.
        # It would limit the function's adapatability more than anything, and I was also worried it would cause me to fail some weird test case.
    if len(s) >= config.MIN_WORD and s.isalpha():
        return True
    else:  
        return False
        

def normalize(s: str) -> str:
    """Canonical for strings in dictionary or on board
    >>> normalize("filter")
    'FILTER'
    """
    return s.upper()


def read_dict(path: str) -> list[str]:
    """Returns ordered list of valid, normalized words from dictionary.

    >>> read_dict("data/shortdict.txt")
    ['ALPHA', 'BED', 'BETA', 'DELTA', 'GAMMA', 'OMEGA']
    """
    result = []
    with open(path, 'r', encoding="cp437") as lines:
        for line in lines:
            word = normalize(line.strip())
            if allowed(word):
                result.append(word)
    return sorted(result)


def read_tree(words: list[str], skip = 0) -> dict:
    if words == []:
        return {'state':NOPE}
    tree = {}
    if words[0][skip:] == '':
        tree['state'] = MATCH
        slice_end = 1
    else:
        tree['state'] = PREFIX
        slice_end = 0
    for i in range(len(config.ALPHABET)):
        slice_start = slice_end

        lower_bound = 0
        upper_bound = len(words) - 1

        if i == 25:
            lower_bound = len(words)
        else:
            next_letter = config.ALPHABET[i+1]

        while lower_bound <= upper_bound:
            mid = (upper_bound + lower_bound) // 2
            mid_word = words[mid][skip:]
            if next_letter == mid_word:
                lower_bound = mid
                break
            if next_letter < mid_word:
                upper_bound = mid - 1
            if next_letter > mid_word:
                lower_bound = mid + 1

        slice_end = lower_bound
        tree[config.ALPHABET[i]] = read_tree(words[slice_start:slice_end], skip + 1)
    return tree


def tree_search(candidate: str, tree: dict) -> str:
    """Determine whether candidate is a MATCH, a PREFIX of a match, or a big NOPE.

    >>> tree_search("ALPHA", read_tree(['ALPHA', 'BETA', 'GAMMA'])) == MATCH
    True

    >>> tree_search("BE", read_tree(['ALPHA', 'BETA', 'GAMMA'])) == PREFIX
    True

    >>> tree_search("FOX", read_tree(['ALPHA', 'BETA', 'GAMMA'])) == NOPE
    True

    >>> tree_search("ZZZZ", read_tree(['ALPHA', 'BETA', 'GAMMA'])) == NOPE
    True
    """
    for char in candidate:
        if tree[char]['state'] == NOPE:
            return NOPE
        tree = tree[char]
    return tree['state']


def unpack_board(letters: str, rows: int) -> list[list[str]]:
    """Unpack a single string of characters into
    a square matrix of individual characters, N_ROWS x N_ROWS.

    >>> unpack_board("abcdefghi", rows=3)
    [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]

    >>> unpack_board("abcdefghijklmnop", rows=4)
    [['a', 'b', 'c', 'd'], ['e', 'f', 'g', 'h'], ['i', 'j', 'k', 'l'], ['m', 'n', 'o', 'p']]
    """
    matrix = []
    for i in range(rows):
        matrix.append(list(letters[i*rows : (i+1)*rows]))
    return matrix


def repack_board(board: list) -> str:
    board_str = ''
    for row in board:
        for square in row:
            board_str += str(square)
    return board_str


def boggle_solve(board: list[list[str]], words: dict, shadow = None) -> list[str]:
    """Find all the words that can be made by traversing
    the boggle board in all 8 directions.  Returns sorted list without
    duplicates.

    >>> board = unpack_board("PLXXMEXXXAXXSXXX", rows=4)
    >>> words = read_dict("data/dict.txt")
    >>> boggle_solve(board, words)
    ['AMP', 'AMPLE', 'AXE', 'AXLE', 'ELM', 'EXAM', 'LEA', 'MAX', 'PEA', 'PLEA', 'SAME', 'SAMPLE', 'SAX']
    """
    solutions = []
    row_count = len(board)
    if row_count == 0:
        return []
    col_count = len(board[0])
    has_shadow = False
    if shadow != None:
        shadow.clear()
        shadow += [[0 for i in range(col_count)] for i in range(row_count)]
        has_shadow = True

    def solve(row: int, col: int, prefix: str):
        """One solution step"""
        solved = len(solutions)
        letter = board[row][col]
        if letter == IN_USE:
            return
        
        prefix = prefix + letter
        status = tree_search(prefix, words)
        if status == NOPE:
            return
        
        if status == MATCH:
            if prefix not in solutions:
                solutions.append(prefix)

        board[row][col] = IN_USE  # Prevent reusing
        
        for new_row in range(row-1,row+2):
            if 0 <= new_row < row_count:
                for new_col in range(col-1,col+2):
                    if 0 <= new_col < col_count:
                        solve(new_row, new_col, prefix)

        # Restore
        board[row][col] = letter
        if has_shadow:
                shadow[row][col] += list_score(solutions[solved:])

    # Look for solutions starting from each board position
    for row_i in range(row_count):
        for col_i in range(col_count):
            solve(row_i, col_i, "")

    # Return solutions without duplicates, in sorted order
    solutions = list(set(solutions))
    return sorted(solutions)


def word_score(word: str) -> int:
    """Standard point value in Boggle"""
    # assert len(word) <= 16
    if len(word) >= 8:
        return 11
    return POINTS[len(word)]


def list_score(solutions: list) -> int:
    total = 0
    for word in solutions:
        total += word_score(word)
    return total


def score(board, words: dict, shadow = None):
    if isinstance(board, str):
        board = unpack_board(board, int(len(board)**0.5))
    solutions = boggle_solve(board, words, shadow)
    return list_score(solutions)


if __name__ == "__main__":
    doctest.testmod()