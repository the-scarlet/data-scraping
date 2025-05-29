import argparse
import json
import sys
from config.config import AppConfig
from src.controllers import google_alerts_controller
from src.utils.error_util import ErrorUtil
import logging


logger = logging.getLogger("Data-scraping")
config = AppConfig()


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # Custom error handling
        logger.error(f"❌ Command error: {message}")
        logger.error("💡 Use -h or --help to see all available commands")
        # logger.error(
        #     "💡 Use <command-name> -h or --help to see all valid options/ flags"
        # )
        sys.exit(2)


class CliScrapper:
    def __init__(self):
        self.parser = CustomArgumentParser(description="Data scraper")
        self.subparsers = self.parser.add_subparsers(dest="mode", help="Scraping mode")

    def set_cookie_parser(self):
        specific_parser = self.subparsers.add_parser("set-cookies", help="set cookies")

    def set_alert_parser(self):
        specific_parser = self.subparsers.add_parser("set-alert", help="set alert")
        specific_parser.add_argument(
            "-i",
            "--instruments",
            type=str,
            nargs="+",
            help=f"instruments",
        )
        specific_parser.add_argument(
            "-k",
            "--keywords",
            type=str,
            nargs="+",
            help=f"keywords",
        )
        specific_parser.add_argument(
            "-f",
            "--frequency",
            type=str,
            default=config.frequency,
            help=f"Alert frequency (default: {config.frequency})",
        )

        specific_parser.add_argument(
            "-s",
            "--source",
            type=str,
            default=config.source,
            choices=["Automatic", "Finance"],
            help=f"Alert source (default: {config.source})",
        )

        specific_parser.add_argument(
            "-l",
            "--language",
            type=str,
            default=config.language,
            help=f"Alert language (default: {config.language})",
        )

        specific_parser.add_argument(
            "-r",
            "--region",
            type=str,
            default=config.region,
            help=f"Alert region (default: {config.region})",
        )

        specific_parser.add_argument(
            "-v",
            "--volume",
            type=str,
            default=config.volume,
            choices=["Seulement les meilleurs résultats", "Tous les résultats"],
            help=f"Results volume (default: {config.volume})",
        )
        specific_parser.add_argument(
            "-d",
            "--delivery",
            type=str,
            default=config.delivery,
            help=f"Results delivery format (default: {config.delivery})",
        )
        specific_parser.add_argument(
            "-j",
            "--json",
            type=str,
            default="",
            help=f"Json file that contains parameters and options",
        )

    def get_alerts_parser(self):
        specific_parser = self.subparsers.add_parser(
            "get-alerts", help="get alerts list"
        )

    def rm_alert_parser(self):
        specific_parser = self.subparsers.add_parser("rm-alert", help="remove alert")
        specific_parser.add_argument(
            "-i",
            "--instruments",
            type=str,
            nargs="+",
            help=f"instruments",
        )
        specific_parser.add_argument(
            "-k",
            "--keywords",
            type=str,
            nargs="+",
            help=f"keywords",
        )
        specific_parser.add_argument(
            "-j",
            "--json",
            type=str,
            default="",
            help=f"Json file that contains parameters and options",
        )

    def json_override(self, args):
        try:
            with open(args.json, "r", encoding="utf-8") as f:
                json_args = json.load(f)

            for key, value in json_args.items():
                if hasattr(args, key):  # Only override existing arguments
                    setattr(args, key, value)
                else:
                    print(f"Warning: Ignoring unknown JSON key '{key}'")
            return args
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in json override")

    def get_rss_link_parser(self):
        specific_parser = self.subparsers.add_parser("get-rss", help="get RSS")

    def get_flags_for_command(self, command_name):
        try:
            """Returns a dictionary of flags and their details for a given command"""
            if command_name not in self.subparsers.choices:
                raise ValueError(f"Unknown command: {command_name}")

            command_parser = self.subparsers.choices[command_name]
            flags = {}

            for action in command_parser._option_string_actions.values():
                # Skip duplicate entries (like -i and --instruments)
                if action.dest not in flags:
                    flags[action.dest] = {
                        "flags": [opt for opt in action.option_strings],
                        "type": action.type,
                        "required": action.required,
                        "help": action.help,
                        "nargs": action.nargs,
                    }

            return flags
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in get flags for command")

    def validate_flags(self, args):
        try:
            """validate flags answers 2 questions:
            Are user flags valid?
            Are required flags provided by the user?
            """
            user_flags = [flag for flag in vars(args).keys() if flag != "mode"]
            valid_flags = self.get_flags_for_command(args.mode)
            # Are user flags valid?
            for flag in user_flags:
                if flag not in valid_flags.keys():
                    logger.info(
                        f"{flag} is an invalid flag for the command {args.mode}. Use -h for valid flags"
                    )
                    exit(1)

            # Are required flags provided by the user?
            required_flags = set([valid_flag for valid_flag in valid_flags.keys()]) & {
                "instruments",
                "keywords",
            }
            logger.info(required_flags)
            for required_flag in required_flags:
                logger.info(required_flag)
                if (required_flag not in user_flags) or (
                    getattr(args, required_flag) == None
                ):
                    logger.info(
                        f"{required_flag} is a required flag for the command {args.mode}. Use -h for more info"
                    )
                    exit(1)
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in validate flags")

    def handle_args(self):
        try:
            args = self.parser.parse_args()
            logger.info(args)
            # Exit if no mode was selected
            if not args.mode:
                self.parser.print_help()
                return 1
            if not (hasattr(args, "json")):
                pass
            elif args.json:
                args = self.json_override(args)
            # Calculate the result based on the selected mode

            logger.info(args)
            self.validate_flags(args)
            return args
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in handle args")

    async def execute_command(self):
        # try:
        self.set_cookie_parser()
        self.set_alert_parser()
        self.get_alerts_parser()
        self.rm_alert_parser()
        self.get_rss_link_parser()
        args = self.handle_args()

        if args.mode == "set-cookies":
            result = await google_alerts_controller.get_cookies()
        elif args.mode == "set-alert":
            result = await google_alerts_controller.set_google_alerts(args)
        elif args.mode == "get-alerts":
            result = await google_alerts_controller.get_existing_google_alerts()
        elif args.mode == "rm-alert":
            result = await google_alerts_controller.remove_google_alerts(args)
        elif args.mode == "get-rss":
            result = await google_alerts_controller.get_rss_links()
        print(result)
        return 0

    # except Exception as e:
    #     return ErrorUtil.handle_error(e, "Error in execute command")
