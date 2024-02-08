import argparse


def parse_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('PORT', type=int, help='port to listen for requests')
    parser.add_argument('--RUN_ANALYSIS', '-r', action='store_true',
                        help='if present, will run text analysis using UDPIPE')
    parser.add_argument('--SAVE_INTERNAL_FILES', '-s', action='store_true',
                        help='if present, will save internal files, useful for debugging')
    parser.add_argument("--udpipe_model", type=str, help="Path to the UDPipe model file.")
    return parser.parse_args()


args = parse_command_line_args()
