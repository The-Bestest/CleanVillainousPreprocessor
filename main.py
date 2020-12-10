import csv
import os


def get_thresholds(game_file):
    """
    Returns a list of thresholds as they change in time
    """

    header = next(game_file)

    def h(column_name):
        return header.index(column_name)
    
    last_motor_imagery = None

    for event in game_file:
        if event[h("Event")] == "MotorImagery":
            last_motor_imagery = event
        if event[h("Event")] == "GameDecision":
            if event[h("TrialResult")] == "AccInput":
                print("Success: ", last_motor_imagery[h("BCIThresholdBuffer")])
            elif event[h("TrialResult")] == "RejInput":
                print("Failure: ", last_motor_imagery[h("BCIThresholdBuffer")])

            print('\n')


directory = r'data'

for node in os.scandir(directory):
    participant = node.name
    levels = list(os.scandir(node.path))

    for level in levels:
        print(participant, level.name)
        game_path = [file for file in list(os.scandir(level.path)) if file.name.endswith("Game.csv")][0].path

        with open(game_path) as game_file:
            thresholds = get_thresholds(csv.reader(game_file))