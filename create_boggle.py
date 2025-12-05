"""create_boggle: Generates high scoring boggle boards from random seeds or user inputs

Author: Andre Mones
"""

import tools_boggle
import random
import time
import config
import os
import display_boggle
import doctest
from file_boggle import lookup_board, read_high_score

REQUEST_NUM = int(input('Request_file_number: '))
REQUEST_PATH = config.get_request_x(REQUEST_NUM)
RESPONSE_PATH = config.get_response_x(REQUEST_NUM)
assert config.num_of_request(REQUEST_PATH) != 0

def prepare_request_file():
    """Clears completed requests from request file."""
    if os.path.exists(RESPONSE_PATH):
        with open(RESPONSE_PATH, 'r') as res_file:
            res_state, res_pos = eval(res_file.readline().strip())
    else:
        res_state, res_pos = True, 0
    requests = [str(res_state)+'\n']
    if os.path.exists(REQUEST_PATH):
        with open(REQUEST_PATH, 'r') as req_file:
            req_state = eval(req_file.readline().strip())
            assert isinstance(req_state, bool)
            if req_state == res_state:
                res_pos = 0
            requests += req_file.readlines()[res_pos:]
    requests[-1] = requests[-1].strip()
    with open(REQUEST_PATH, 'w') as req_file:
        req_file.writelines(requests)


def request(board_dict: dict):
    """Requests file_boggle.py to update data files with board_dicts."""
    prepare_request_file()
    with open(REQUEST_PATH, 'a') as req_file:
            req_file.write('\n' + repr(board_dict))


def get_opportune_squares(matrix: list[list[int]]) -> list[tuple[int, int]]:
    """Returns a list of (row, col) positions of squares in a matrix, 
    sorted by the values of the squares divided by the number of ajacent squares (including diagonals).
    
    Not perfectly accurate for single row or single collumn matrices.
    
    >>> get_opportune_squares([0, 20, 6], [9, 5, 15])
    [(0, 0), (1, 1), (0, 2), (1, 0), (0, 1), (1, 2)]

    >>> get_opportune_squares([[6, 5, 0], [15, 32, 25], [24, 35, 18]])
    [(0, 2), (0, 1), (0, 0), (1, 0), (1, 1), (1, 2), (2, 2), (2, 1), (2, 0)]
    """
    squares = []
    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            ajacents = 2**((0<row<len(matrix)-1)+(0<col<len(matrix[0])-1)+1) + 1 - (0<row<len(matrix)-1)*(0<col<len(matrix[0])-1)
            squares.append((matrix[row][col]/ajacents, (row,col)))
    squares.sort()
    return [item[1] for item in squares]


def update_letters(board, words) -> bool:
    """Find a single letter changes that will increase the score of board.
    Makes the most beneficial change from the first square it finds to have any beneficial changes

    Changes board!

    returns True on success, and False if no beneficial change is found.
    
    >>> update_letters([['T', 'H'], ['X', 'S']], ['THIS'], [[0,0],[0,0]])
    True

    >>> update_letters([['T', 'H'], ['X', 'X']], ['THIS'], [[0,0],[0,0]])
    False

    >>> update_letters([['T', 'H', 'I'], ['A', 'X', 'S'], ['X', 'X', 'X']], ['THAT', 'THIS'], [[1,1,1],[0,0,1],[0,0,0]])
    True
    
    """
    shadow = []
    og_score = tools_boggle.score(board, words, shadow)
    squares = get_opportune_squares(shadow)
    for i in range(len(squares)):
        row = squares[i][0]
        col = squares[i][1]
        og_letter = board[row][col]
        best_score = og_score
        best_letter = og_letter

        for letter in config.ALPHABET:
            board[row][col] = letter
            total = tools_boggle.score(board, words)
            if total > best_score:
                best_score = total
                best_letter = letter

        if best_letter != og_letter:
            board[row][col] = best_letter
            tools_boggle.boggle_solve(board, words, shadow)
            return True
        else:
            board[row][col] = og_letter
    return False


def perfect(words: dict, board_str: str, data: dict) -> str:
    """Upgrades a board with single letter changes until there is no
    single letter change that will increase the board's score.

    Changes data!
    
    returns the board as a string.
    """
    board = tools_boggle.unpack_board(board_str, config.SIZE)
    shadow = []
    Upgradable = True
    while Upgradable:
        difs = 0
        for i in range(len(board_str)):
            if board_str[i] != data['Avoid Board'][i]:
                difs += 1
        if difs < min(data['Heat'], 2):
            break
        Upgradable = bool(update_letters(board, words))
        score = tools_boggle.score(board, words, shadow)
        board_str = tools_boggle.repack_board(board)
        if score > data['High']['score']:
            data['High']['score'] = score
            data['High']['board'] = board_str
        display_boggle.display_data(board, score, data, REQUEST_NUM)
    return board_str


def generate(words, data, auto_refine = False):
    """Generates and perfects random boards. Requesting the storage of boards
    with scores that meet the threshold.
    
    If auto_refine == True, threshhold meeting boards will be refined under heat level 0.
    """
    while True:
        data['Heat'] = 0
        data['Iter'] += 1

        # generate random board
        board_str = ''
        for i in range(config.SIZE**2):
            board_str += random.choice(config.ALPHABET)
        
        # hillclimb
        perfect_board = perfect(words, board_str, data)
        score = tools_boggle.score(perfect_board, words)

        # store result if it's good enough (or a record)
        log_threshold = min(config.THRESHOLD, read_high_score())
        if score >= log_threshold and lookup_board(perfect_board) == None:
            board_dict = {}
            board_dict['board'] = perfect_board
            board_dict['score'] = score
            board_dict['seedboard'] = board_str
            board_dict['perfectboard'] = perfect_board
            board_dict['fromboard'] = board_str
            board_dict['fromtype'] = config.SEED
            board_dict['timefound'] = time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(time.time()))
            board_dict['wasrecord'] = False
            board_dict['upgraded'] = False
            board_dict['catagory'] = config.UNSTABLE
            request(board_dict)

            # automaticly start refining process if enabled.
            if auto_refine and score >= config.THRESHOLD:
                data['Start Board'] = board_str
                data['High'] = board_dict
                data['Heat'] = 1
                refine(words, data, heat_bump = False)
                data['Since High'] = -1
                data['High'] = {'board':'0000000000000000000000000', 'score': 0}


def patient_lookup(board_str: str) -> dict:
    """It's like lookup(), but it keeps trying untill it finds something"""
    board_dict = None
    waiting_time = -1
    while not board_dict:
        waiting_time += 1
        if waiting_time > 0:
            time.sleep(1)
            if waiting_time % 20 == 0:
                waiting_time = 0
            print('Hey, do you have file_boggle.py running in another tab? Because you definitely should.')
        board_dict = lookup_board(board_str)
    board_dict['score'] = int(board_dict['score'])
    return board_dict


def refine(words, data, heat_bump = True):
    """Makes different changes to data['high_board'] until it finds a higher scoring board,
    then starts tweaking that board."""
    # prepare for first iteration
    if data['Heat'] == 1:
        # Create list of indexes sorted by how "opportune" they are
        prev_high = patient_lookup(data['High']['board'])
        high_shadow = []
        tools_boggle.score(data['High']['board'], words, high_shadow)
        opportune_indexes = [row*config.SIZE+col for row, col in get_opportune_squares(high_shadow)]
    data['Since High'] = -1
    # start loop
    while True:
        if data['Iter'] >= 5:
            data['Avoid Board'] = data['High']['board']
        data['Iter'] += 1
        data['Since High'] += 1
        # generate board_str
        high_board = data['High']['board']
        if data['Heat'] == 1:
            # If every possible single letter change has been tried, increace Heat or stop refining
            if data['Since High'] >= config.SIZE**2 * config.ALPHA_LEN:
                data['Iter'] -= 1
                if lookup_board(data['High']['board'], check=('catagory', 'C1')) == None:
                    data['High']['catagory'] = config.C1
                    high_copy = data['High'].copy()
                    high_copy.pop('score')
                    request(high_copy)
                if heat_bump:
                    data['Heat'] += 1
                    continue
                return
            # Otherwise find next single letter change.
            replace_pos = opportune_indexes[data['Since High']//config.ALPHA_LEN]
            board_str = high_board[:replace_pos] + config.ALPHABET[data['Since High'] % config.ALPHA_LEN] + high_board[replace_pos+1:]
        else:
            # generate board with Heat-many random changes from data['High']
            board_str = high_board
            for i in range(data['Heat']):
                rand = random.randrange(len(board_str))
                board_str = board_str[:rand] + random.choice(config.ALPHABET) + board_str[rand+1:]

        # hillclimb
        perfect(words, board_str, data)

        # save board if it's good.
        if data['High']['score'] >= prev_high['score'] and lookup_board(data['High']['board']) == None:
            data['High']['fromboard'] = high_board
            data['High']['fromtype'] = data['High']['catagory']
            if data['Heat'] == 1 and prev_high['catagory'] == config.UNSTABLE:
                data['High']['fromtype'] = config.REFINED
            data['High']['timefound'] = time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(time.time()))
            data['High']['upgraded'] = False
            data['High']['catagory'] = config.UNSTABLE
            request(data['High'])
            
            if data['Heat'] == 1:
                prev_high['catagory'] = config.REFINED
                prev_high['upgraded'] = True
                prev_high.pop('score')
                request(prev_high)
                prev_high = patient_lookup(data['High']['board'])
                # Create list of indexes sorted by how "opportune" they are
                high_shadow = []
                tools_boggle.score(data['High']['board'], words, high_shadow)
                opportune_indexes = [row*config.SIZE+col for row, col in get_opportune_squares(high_shadow)]
            data['Since High'] = -1
            continue


def main():
    data = {'Breaks': 1, 'NB Score': 0, 'Iter': 0, 'Heat': 0, 'Since High': -1,
            'High': {'board':'0000000000000000000000000', 'score': 0},
            'Avoid Board': '0000000000000000000000000'}
    mode = '#'
    while mode not in ['G', 'R', '']:
        mode = input('generate or refine? (G or R) return to quit: ').upper()
        if mode == 'doctest' and __name__ == '__main__':
            doctest.testmod
    if mode == '':
        quit()
    if mode == 'R':
            data['Start Board'] = input('input board: ')
            assert len(data['Start Board']) == config.SIZE**2
            assert tools_boggle.allowed(data['Start Board'])
            start_dict = lookup_board(data['Start Board'])
            if not start_dict:
                print(f"Board not found in {config.COMPILED_BOARDS_PATH}. Refining is only implemented for pre-existing boards.\n")
                print(f"If you really want to refine this board, you can manualy add it to {config.COMPILED_BOARDS_PATH}, and it maybe won\'t break everything.")
                quit()
            start_dict['score'] = int(start_dict['score'])
            data['High'] = start_dict
            data['Heat'] = int(input('Heat Level: '))
            heat_bump = False
            if data['Heat'] == 1:
                while heat_bump not in ['Y', 'N']:
                    heat_bump = input('Heat Bump? (Y/N): ').upper()
                if heat_bump == 'Y':
                    heat_bump = True
                else:
                    heat_bump = False


    words = tools_boggle.read_tree(tools_boggle.read_dict(config.DICT_PATH))
    data['Time Start'] = time.time()

    if mode == 'G':
        generate(words, data, True)

    if mode == 'R':
        refine(words, data, heat_bump)


if __name__ == "__main__":
    main()