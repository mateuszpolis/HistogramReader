"""Main entry point for HistogramReader application."""

import argparse
import sys
from typing import Optional


def main(args: Optional[list] = None) -> int:
    """Run the HistogramReader application.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    if args is None:
        args = sys.argv[1:]

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="HistogramReader - FIT Detector Histogram Analysis Tool"
    )
    parser.add_argument(
        "--cli", action="store_true", help="Run in command line mode (GUI is default)"
    )
    parser.add_argument("--version", action="version", version="HistogramReader 1.0.0")

    parsed_args = parser.parse_args(args)

    if parsed_args.cli:
        # Command line mode
        print("HistogramReader - FIT Detector Histogram Reader")
        print("Command line interface not yet implemented.")
        print("Use without --cli flag to launch GUI.")
        return 0
    else:
        # GUI mode (default)
        try:
            from .gui import HistogramReaderApp

            print("Starting HistogramReader GUI...")
            app = HistogramReaderApp()
            app.run()
            return 0

        except ImportError as e:
            print(f"Error: Could not import GUI components: {e}")
            print("Please ensure all dependencies are installed:")
            print("pip install -e .[dev]")
            return 1
        except Exception as e:
            print(f"Error starting application: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
