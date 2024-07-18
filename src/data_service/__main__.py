"""Main script for data server"""

import argparse
import signal
import threading
from data_service.app.server import DataService

server = DataService()


def read_args():
    """Read args and return object"""
    parser = argparse.ArgumentParser(
        description="Run the data service server."
    )
    parser.add_argument(
        '-d', '--detach',
        action='store_true',
        help="Enable stopping the server with Ctrl+C"
    )
    return parser.parse_args()


def signal_handler(sig, frame):  # pylint: disable=W0613
    """Handle Ctrl-C to exit"""
    server.stop_server()


def run_detach():
    """Run server detached"""
    server_thread = threading.Thread(target=server.start_server)
    server_thread.start()

    # keep script alive to capture Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)
    while server_thread.is_alive():
        server_thread.join(1)


if __name__ == "__main__":
    args = read_args()
    if args.detach:
        run_detach()
    else:
        server.start_server()
