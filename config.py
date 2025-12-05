"""config: configuration file for best boggle project

Author: Andre Mones
"""

import re

ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
ALPHA_LEN = len(ALPHABET)

MIN_WORD = 3

DICT_PATH = "data/dicts/dictBig.txt"

THRESHOLD = 5500

# THE VAIRABLES BELOW ARE USED BY CSV FILES!
    # DO NOT CHANGE THEM UNLESS YOU REALLY KNOW WHAT YOU'RE DOING, BECAUSE THE CODE WON'T AJUST ON IT'S OWN!
SIZE = 5    # side length of the board.
SEED = 'Seed'           # Signifies that a board is a random seed.
UNSTABLE = 'Unstable'   # Signifies that a board hasn't been tested under heat 1.
C1 = 'C1'               # Signifies that a board can't be refined with heat 1.
REFINED = 'Refined'     # Signifies that a board has been refined with heat 1.
NA = 'N/A'              # Signifies nothing in particular: unknown / other.

BOARDS_FOLDER_PATH = str(f"data/boards/{SIZE}x{SIZE}/")
# BOARDS_FOLDER_PATH = str(f"data/boards/5x5-Andre/")

COMPILED_FOLDER_PATH = BOARDS_FOLDER_PATH + "compiled boards/"
COMPILED_BOARDS_PATH = COMPILED_FOLDER_PATH + "all_boards.csv"
COMPILED_BEST_PATH = COMPILED_FOLDER_PATH + "records.csv"
COMPILED_UNSTABLES_PATH = COMPILED_FOLDER_PATH + "unstables.csv"
COMPILED_C1_PATH = COMPILED_FOLDER_PATH + "C1s.csv"
COMPILED_PERFECTS_PATH = COMPILED_FOLDER_PATH + "perfects.csv"
REQUESTS_FOLDER_PATH = BOARDS_FOLDER_PATH + "requests/"

def get_request_x(i: int) -> str:
    """returns a request file corresponding to the given number"""
    assert isinstance(i, int) and i >= 0
    return REQUESTS_FOLDER_PATH + f"{i}_request.txt"

def get_response_x(i: int) -> str:
    """returns a response file corresponding to the given number"""
    assert isinstance(i, int) and i >= 0
    return REQUESTS_FOLDER_PATH + f"{i}_response.txt"

request_format = re.compile("^.+/([1-9][0-9]*)_request.txt$")
response_format = re.compile("^.+/([1-9][0-9]*)_response.txt$")

def num_of_request(path: str) -> int:
    """tells you num of request file, if it is one. 0 otherwise"""
    section = request_format.match(path)
    if section == None:
        num = 0
    else:
        num = int(section.group(1))
    return num

def num_of_response(path: str) -> int:
    """tells you num of respones file, if it is one. 0 otherwise"""
    section = response_format.match(path)
    if section == None:
        num = 0
    else:
        num = section.group(1)
    return num


# git test