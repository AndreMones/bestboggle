"""File Boggle:

"""

import _thread
import config
import csv
import os
from time import sleep



def read_csv(path: str) -> list[dict]:
    result = []
    with open(path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, skipinitialspace=True)
        for line in reader:
            dud = True
            for value in line.values():
                if value != '':
                    dud = False
            if not dud:
                result.append(line)
    return result


def read_high_score():
    records = read_csv(config.COMPILED_BEST_PATH)
    high_score = 0
    for board in records:
        score = int(board['score'])
        if score > high_score:
            high_score = score
            continue
    return high_score


RECORD_SCORE = read_high_score()

END_PROMPTED = False


def prompt_kill():
   global END_PROMPTED
   input("input anything to quit safely: ")
   END_PROMPTED = True


def lookup_fields(path: str) -> list[str]:
    with open(path, 'r', newline='') as csvfile:
        feilds = csvfile.readline().rstrip().split(',')
    return feilds


def lookup_board(board_str: str, path = config.COMPILED_BOARDS_PATH, catagory = None) -> dict:
    file = read_csv(path)
    for row in file:
        if board_str == row['board']:
            row['score'] = int(row['score'])
            if catagory != None:
                if row['catagory'] == catagory:
                    return row
                else:
                    break
            return row


def write_dict(path: str, board_dict: dict, fields: list = None):
    if fields == None:
        fields = lookup_fields(path)
    assert set(board_dict.keys()) <= set(fields)
    line = ''
    for field in fields:
        if field in board_dict:

            line += str(board_dict[field])
        else:
            line += 'N/A'
        line += ','
    line = line[:-1] + '\n'
    with open(path, 'a', newline='') as csvfile:
        csvfile.write(line)



def get_com_files() -> tuple[list[tuple], list[tuple]]:
    comfiles = [os.path.join(config.REQUESTS_FOLDER_PATH, f) for f in os.listdir(config.REQUESTS_FOLDER_PATH) if os.path.isfile(os.path.join(config.REQUESTS_FOLDER_PATH, f))]
    request_files = {}
    response_files = {}
    for path in comfiles:
        num = int(config.num_of_request(path))
        if num > 0:
            request_files[num] = path
        else:
            num = int(config.num_of_response(path))
            if num > 0:
                response_files[num] = path
    return (request_files, response_files)


def main():
    _thread.start_new_thread(prompt_kill, ())
    while not END_PROMPTED:
        sleep(5)
        request_files, response_files = get_com_files()

        response_states = {}
        request_states = {}
        request_lengths = {}
        poses = {}
        requests = []
        for num in request_files:
            req_file = request_files[num]
            if num in response_files:
                response_exists = True
                res_file = response_files[num]
            else:
                response_exists = False
                res_file = config.get_response_x(num)
                response_states[num] = res_file

            if response_exists:
                with open(res_file, 'r') as line:
                        response_states[num], poses[num] = eval(line.readline().strip())
            else:
                response_states[num] = True
                response_files[num] = config.get_response_x(num)
                poses[num] = 0
            with open(req_file, 'r') as lines:
                line_index = 0
                skipto = 1
                for line in lines:
                    if line_index == 0:
                        request_states[num] = eval(line)
                        if request_states[num] == response_states[num]:
                            response_states[num] = not request_states[num]
                            skipto = poses[num] + 1
                    else:
                        if line == '':
                            continue
                        if line_index >= skipto:
                            requests.append(eval(line))
                    line_index += 1
                request_lengths[num] = line_index

        requests.sort(key=lambda item: -len(item))

        posible_bests = []
        all_boards = read_csv(config.COMPILED_BOARDS_PATH)
        for request in requests:
            for i in range(len(all_boards)):
                board_dict = all_boards[i]
                if request['board'] == board_dict['board']:
                    if request['timefound'] != board_dict['timefound']:
                        break
                    if eval(str(board_dict['upgraded']).strip()) == True:
                        request['upgraded'] = True
                    all_boards[i].update(request)
                    break
            else:
                all_boards.append(request)
                if 'score' in request:
                        if int(request['score']) > RECORD_SCORE:
                            posible_bests.append(request)
        

        posible_bests.sort(key=lambda contender: contender['score'])
        high_time = []
        actual_bests = []
        for contender in posible_bests:
            time = contender['timefound'].split()
            time[0] = time[0].split('/').reverse()
            if time >= high_time:
                high_time = time
                actual_bests.append(contender)
        for best in actual_bests:
            best['wasrecord'] = True
            write_dict(config.COMPILED_BEST_PATH, best)

        field_names = lookup_fields(config.COMPILED_BOARDS_PATH)
        with open(config.COMPILED_BOARDS_PATH, 'w') as all_file:
            all_file.write(','.join(field_names)+'\n')
            writer = csv.DictWriter(all_file, fieldnames=field_names, delimiter=',', restval=config.NA)
            writer.writerows(all_boards)

        for num in response_states:
            with open(response_files[num], 'w') as res_file:
                res_file.write(str((response_states[num], request_lengths[num]))+'\n')
        
        for path in [config.COMPILED_C1_PATH, config.COMPILED_UNSTABLES_PATH, config.COMPILED_PERFECTS_PATH]:
            if os.path.exists(path):
                os.remove(path)
            with open(path, 'w') as file:
                file.write(','.join(field_names)+'\n')   

        for row in all_boards:
            catagory = row['catagory']
            if catagory == config.C1:
                write_dict(config.COMPILED_C1_PATH, row)
            elif catagory == config.UNSTABLE:
                write_dict(config.COMPILED_UNSTABLES_PATH, row)
            if row['board'] == row['perfectboard']:
                write_dict(config.COMPILED_PERFECTS_PATH, row)

# BESTS CURRENTLY DON'T AUTO UPDATE PROPERLY


if __name__ == "__main__":
    main()