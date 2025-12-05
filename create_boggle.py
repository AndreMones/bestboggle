import tools_boggle
import random
import time
import config
import os
import display_boggle
from file_boggle import read_csv
from file_boggle import lookup_board

REQUEST_NUM = int(input('Request_file_number: '))
REQUEST_PATH = config.get_request_x(REQUEST_NUM)
RESPONSE_PATH = config.get_response_x(REQUEST_NUM)
assert config.num_of_request(REQUEST_PATH) != 0

def prepare_request_file():
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
    prepare_request_file()
    with open(REQUEST_PATH, 'a') as req_file:
            req_file.write('\n' + repr(board_dict))


def get_opportune_squares(matrix: list[list[int]]) -> list[tuple[int, int]]:
    """Returns a list of (row, col) positions of squares in a matrix, 
    sorted by the values of the squares divided by the number of ajacent squares (including diagonals).
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
    board = tools_boggle.unpack_board(board_str, 5)
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


def generate(words, data, threshold, auto_refine = False):
    while True:
        data['Heat'] = 0
        data['Iter'] += 1

        # generate random board
        board_str = ''
        for i in range(5**2):
            board_str += config.ALPHABET[random.randint(0,25)]
        
        # hillclimb
        perfect_board = perfect(words, board_str, data)
        score = tools_boggle.score(perfect_board, words)

        # store result if it's good enough
        if score >= threshold and lookup_board(perfect_board) == None:
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
            if auto_refine:
                data['Start Board'] = board_str
                data['High'] = board_dict
                data['Heat'] = 1
                refine(words, data, heat_bump = False)
                data['Since High'] = -1
                data['High'] = {'board':'0000000000000000000000000', 'score': 0}


def refine(words, data, heat_bump = True):
    # prepare for first iteration
    if data['Heat'] == 1:
        # Create list of indexes sorted by how "opportune" they are
        prev_high = None
        while prev_high == None:
            time.sleep(1)
            prev_high = lookup_board(data['High']['board'])
        high_shadow = []
        tools_boggle.score(data['High']['board'], words, high_shadow)
        high_lows = [row*5+col for row, col in get_opportune_squares(high_shadow)]
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
            if data['Since High'] >= config.SIZE**2 * 26:
                data['Iter'] -= 1
                if lookup_board(data['High']['board'], config.COMPILED_C1_PATH) == None:
                    data['High']['catagory'] = config.C1
                    high_copy = data['High'].copy()
                    high_copy.pop('score')
                    request(high_copy)
                if heat_bump:
                    data['Heat'] += 1
                    continue
                else:
                    return
            # Otherwise find next single letter change.
            replace_pos = high_lows[data['Since High']//26]
            board_str = high_board[:replace_pos] + config.ALPHABET[data['Since High'] % 26] + high_board[replace_pos+1:]
        else:
            # generate board with Heat-many random changes from data['High']
            board_str = high_board
            for i in range(data['Heat']):
                rand = random.randint(0,24)
                board_str = board_str[:rand] + config.ALPHABET[random.randint(0,25)] + board_str[rand+1:]

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
                prev_high = None
                while prev_high == None:
                    time.sleep(1)
                    prev_high = lookup_board(data['High']['board'])
                # Create list of indexes sorted by how "opportune" they are
                high_shadow = []
                tools_boggle.score(data['High']['board'], words, high_shadow)
                high_lows = [row*5+col for row, col in get_opportune_squares(high_shadow)]
            data['Since High'] = -1
            continue


def main():
    data = {'Breaks': 1, 'NB Score': 0, 'Iter': 0, 'Heat': 0, 'Since High': -1,
            'High': {'board':'0000000000000000000000000', 'score': 0},
            'Avoid Board': '0000000000000000000000000'}
    mode = ' '
    while mode not in ['G', 'R', '']:
        mode = input('generate or refine? (G or R) return to quit: ').upper()
    if mode == '':
        quit()
    if mode == 'R':
            data['Start Board'] = input('input board: ')
            start_dict = lookup_board(data['Start Board'])
            data['High'] = start_dict
            data['Heat'] = int(input('Heat Level: '))
            heat_bump = ' '
            while heat_bump not in ['Y', 'N']:
                heat_bump = input('Heat Bump? (Y/N): ').upper()
            if heat_bump == 'Y':
                heat_bump = True
            else:
                heat_bump = False


    words = tools_boggle.read_tree(tools_boggle.read_dict(config.DICT_PATH))
    data['Time Start'] = time.time()

    if mode == 'G':
        generate(words, data, 5500, True)

    if mode == 'R':
        refine(words, data, heat_bump)


if __name__ == "__main__":
    main()