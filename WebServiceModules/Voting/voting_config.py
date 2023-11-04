import argparse

# Define the supported voting algorithms
ALGORITHMS = ["DIFF", "ADD", "INTERSECT", "MAJORITY"]


def parse_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('PORT', type=int, help='Port to listen for requests')
    parser.add_argument('--ALGORITHM', '-a', choices=ALGORITHMS, help='algorithm to use, mandatory')

    return parser.parse_args()


args = parse_command_line_args()
