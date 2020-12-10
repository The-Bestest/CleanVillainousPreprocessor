import csv
import os


def parse_thresholds(threshold_str):
    return threshold_str[1:-2].split(" ")


def get_thresholds(game_file):
    """
    Returns a list of thresholds as they change in time
    """

    header = next(game_file)

    def h(column_name):
        return header.index(column_name)
    
    last_motor_imagery = None
    thresholds = []

    for event in game_file:
        if event[h("Event")] == "MotorImagery":
            last_motor_imagery = event
        if event[h("Event")] == "GameDecision":
            if last_motor_imagery == None:
                continue
            event_thresholds = parse_thresholds(last_motor_imagery[h("BCIThresholdBuffer")])

            if event[h("TrialResult")] == "AccInput":
                thresholds.append(min(event_thresholds))
            elif event[h("TrialResult")] == "RejInput":
                thresholds.append(0)

    return thresholds


directory = r'data'

for node in os.scandir(directory):
    participant = node.name
    levels = list(os.scandir(node.path))

    for level in levels:
        game_path = [file for file in list(os.scandir(level.path)) if file.name.endswith("Game.csv")][0].path

        with open(game_path) as game_file:
            thresholds = get_thresholds(csv.reader(game_file))

            print(participant, level.name, thresholds)