import csv
import os


def parse_thresholds(threshold_str):
    return threshold_str[1:-2].split(" ")


def get_thresholds(game_file):
    """
    Returns a list of thresholds as they change in time. The zeroes mean a failure
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
                thresholds.append(0)
                continue
            event_thresholds = parse_thresholds(last_motor_imagery[h("BCIThresholdBuffer")])

            if event[h("TrialResult")] == "AccInput":
                thresholds.append(min(event_thresholds))
            elif event[h("TrialResult")] == "RejInput":
                thresholds.append(0)

    return thresholds

class Participant:
    def __init__(self, name):
        self.name = name
        self.body = []
        self.blocks = []

def get_formatted_row(data, level_name):
    row = [participant.name, level_name]
    start_threshold = min([el for el in data[:5] if el != 0])
    main_threshold = min([el for el in data[5:] if el != 0])

    row.extend([start_threshold, main_threshold])
    row.extend(data)

    return row


directory = r'data'
data = []

for node in os.scandir(directory):
    participant = Participant(node.name)
    data.append(participant)

    levels = list(os.scandir(node.path))

    for level in levels:
        game_path = [file for file in list(os.scandir(level.path)) if file.name.endswith("Game.csv")][0].path

        with open(game_path) as game_file:
            thresholds = get_thresholds(csv.reader(game_file))

            if level.name == "Body":
                participant.body = thresholds
            elif level.name == "Blocks":
                participant.blocks = thresholds

data.sort(key=lambda x: int(x.name[1:]))
data = list(filter(lambda x: len(x.body) == 30 and len(x.blocks) == 30, data)) # remove incomplete datasets

for participant in data:
    print(participant.name,
        "\tBody:", str(len(participant.body)) + "(" + str(len(list(filter(lambda x: x == 0, participant.body)))) + " fails)",
        "\tBlocks: ", str(len(participant.blocks)) + "(" + str(len(list(filter(lambda x: x == 0, participant.blocks)))) + " fails)")

with open('thresholds.csv', 'w') as thresholds_file:
    writer = csv.writer(thresholds_file, quoting=csv.QUOTE_MINIMAL)
    header = ["Participant", "Level", "StartThresholdEstimate", "MainThresholdEstimate"]
    header.extend(["Trial" + str(el) for el in list(range(1, 31))])
    writer.writerow(header)

    for participant in data:
        writer.writerow(get_formatted_row(participant.body, "Body"))
        writer.writerow(get_formatted_row(participant.blocks, "Blocks"))