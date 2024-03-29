import argparse


def parse_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('PORT', type=int, help='Port to listen for requests')
    parser.add_argument('--DICTIONARY', '-d', type=str, required=True, help='path for dictionary, mandatory')

    return parser.parse_args()


args = parse_command_line_args()
