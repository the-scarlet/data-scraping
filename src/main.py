try:
    from .config import LOG_LEVEL
    from .controllers import google_alerts_controller
    from .utils.logger import configure_logging
except ImportError:
    from config import LOG_LEVEL
    from controllers import google_alerts_controller
    from utils.logger import configure_logging
import argparse
import asyncio

configure_logging(level=LOG_LEVEL)


async def main():
    parser = argparse.ArgumentParser(description="Data scraper")

    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest="mode", help="Scraping mode")

    # Create parser for setting cookies mode
    set_cookies_parser = subparsers.add_parser("set-cookies", help="set cookies")

    # # Create parser for set alert
    # set_alert_parser = subparsers.add_parser("set-alert", help="set-alert")

    # # Create parser for set alert
    # get_alerts_parser = subparsers.add_parser("get-alerts", help="get-alerts")
    # # Create parser for set alert
    # rm_alert_parser = subparsers.add_parser("rm-alert", help="Calculate: a - b + c - d")
    # Add the same optional parameters to both parsers
    # for subparser in [calc1_parser, calc2_parser]:
    #     subparser.add_argument(
    #         "-a", "--param-a", type=float, default=0, help="Parameter a (default: 0)"
    #     )
    #     subparser.add_argument(
    #         "-b", "--param-b", type=float, default=0, help="Parameter b (default: 0)"
    #     )
    #     subparser.add_argument(
    #         "-c", "--param-c", type=float, default=0, help="Parameter c (default: 0)"
    #     )
    #     subparser.add_argument(
    #         "-d", "--param-d", type=float, default=0, help="Parameter d (default: 0)"
    #     )

    # # Additional options
    # subparser.add_argument(
    #     "-v", "--verbose", action="store_true", help="Show detailed calculation"
    # )
    # subparser.add_argument(
    #     "--precision",
    #     type=int,
    #     default=2,
    #     help="Number of decimal places in result (default: 2)",
    # )

    args = parser.parse_args()

    # Exit if no mode was selected
    if not args.mode:
        parser.print_help()
        return 1

    # Get which parameters were explicitly provided by the user
    provided_params = []
    if hasattr(args, "param_a") and args.param_a != 0:
        provided_params.append(("a", args.param_a))
    if hasattr(args, "param_b") and args.param_b != 0:
        provided_params.append(("b", args.param_b))
    if hasattr(args, "param_c") and args.param_c != 0:
        provided_params.append(("c", args.param_c))
    if hasattr(args, "param_d") and args.param_d != 0:
        provided_params.append(("d", args.param_d))

    # Calculate the result based on the selected mode
    if args.mode == "set-cookies":
        # Calculate: a + b - c - d
        result = await google_alerts_controller.get_cookies()

        print(result)

    elif args.mode == "calc2":
        # Calculate: a - b + c - d
        # result = calculate2(
        #     a=args.param_a, b=args.param_b, c=args.param_c, d=args.param_d
        # )
        pass

    return 0


if __name__ == "__main__":
    exit(main())
