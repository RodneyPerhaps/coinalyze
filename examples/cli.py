import argparse
import sys
from pprint import pprint

from coinalyze.client import CoinalyzeClient
from coinalyze.enums import CurrentEndpoint, Endpoint, HistoryEndpoint, Interval

HISTORY_ENDPOINTS = [e.value for e in HistoryEndpoint]
CURRENT_ENDPOINTS = [e.value for e in CurrentEndpoint]
REFERENCE_ENDPOINTS = [e.value for e in Endpoint]
ENDPOINTS = [*REFERENCE_ENDPOINTS, *CURRENT_ENDPOINTS, *HISTORY_ENDPOINTS]


class CoinalyzeCLI:
    """Simple CLI for Coinalyze API to explore the different endpoints."""

    def __init__(self, argv):
        self.argv = argv
        self.client = CoinalyzeClient()
        self.parser = argparse.ArgumentParser(
            description=self.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
        )

    def parse_arguments(self):
        """Parse the arguments."""
        self.parser.add_argument("endpoint", choices=ENDPOINTS)
        self.parser.add_argument("--symbols", "-s", type=str, nargs="+")
        self.parser.add_argument("--interval", "-i", type=Interval, choices=list(Interval), default=Interval.D1)
        self.parser.add_argument("--start", type=str)
        self.parser.add_argument("--end", type=str)
        self.parser.add_argument("--current", action="store_true")
        return self.parser.parse_args(args=self.argv[1:])

    def run(self):
        """Run the command."""
        args = self.parse_arguments()
        endpoint = args.endpoint

        if endpoint in list(REFERENCE_ENDPOINTS):
            response = self.client.get(endpoint)

        else:
            if (symbols := args.symbols) is None:
                raise ValueError(f"Symbols are required for endpoint {endpoint}")
            if args.current and endpoint in list(CURRENT_ENDPOINTS):
                response = self.client.get_current(endpoint, symbols)
            elif endpoint in list(HISTORY_ENDPOINTS):
                response = self.client.get_history(endpoint, symbols, args.interval, args.start, args.end)
            else:
                raise ValueError("Unknown endpoint")

        print(f"Response for endpoint {endpoint}:")
        pprint(response)


if __name__ == "__main__":
    CoinalyzeCLI(sys.argv).run()
