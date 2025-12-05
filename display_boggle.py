import time
import tools_boggle


def display_board(board: list[list[str]]):
    for row in board:
        line = '   '
        for letter in row:
            line += ' ' + letter
        print(line)
    print('')


def display_data(board, score, data, request_num):
    High_Board = tools_boggle.unpack_board(data['High']['board'], 5)
    print('\n\n\n\n\n')
    print('Request Slot:', request_num)
    print('')
    if data['Heat'] > 0:
        print('Start Board:', data['Start Board'])
        print('Heat Level:', data['Heat'])
    else:
        print(' '*25 + '\n')
    print('Curr Board:')
    display_board(board)
    # show_board(shadow)
    print('Curr Score:', score)
    print('')
    print('High Board:')
    display_board(High_Board)
    print('High Score', data['High']['score'])
    duration = round(time.time()-data['Time Start'])
    print('Time:', str(int(time.strftime('%j', time.gmtime(duration)))-1) + time.strftime(':%H:%M:%S', time.gmtime(duration)),duration)
    print('Iteration:', data['Iter'])
    if data['Since High'] > -1:
        print('Since High:', data['Since High'])
    else:
        print()