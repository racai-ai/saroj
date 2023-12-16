import argparse


def parse_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('PORT', type=int, help='Port to listen for requests')
    parser.add_argument('--DICTIONARY', '-d', type=str, help='path for dictionary, mandatory')
    parser.add_argument('--REPLACEMENT', '-r', type=str, default="X", help='replacement pattern, by default is "X" ')
    parser.add_argument('--CONFIG', '-c', type=str, help='path for config file, mandatory')
    return parser.parse_args()


args = parse_command_line_args()
