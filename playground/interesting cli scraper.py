import argparse
import json
import sys
from config.config import AppConfig
from src.controllers import google_alerts_controller
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
        self.parser = CustomArgumentParser(
            description="Data scraper"
        )  # argparse.ArgumentParser(description="Data scraper")
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
            required=True,
            help=f"instruments",
        )
        specific_parser.add_argument(
            "-k",
            "--keywords",
            type=str,
            nargs="*",
            required=True,
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
            required=True,
            help=f"instruments",
        )
        specific_parser.add_argument(
            "-k",
            "--keywords",
            type=str,
            nargs="*",
            required=True,
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
        with open(args.json, "r", encoding="utf-8") as f:
            json_args = json.load(f)
        valid_flags = self.get_flags_for_command(args.mode)
        for key, value in json_args.items():
            if key in valid_flags.keys():  # Only override existing arguments
                setattr(args, key, value)
            else:
                print(f"Warning: Ignoring unknown JSON key '{key}'")
        return args

    def get_rss_link_parser(self):
        specific_parser = self.subparsers.add_parser("get-rss", help="get RSS")

    def get_flags_for_command(self, command_name):
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

    def validate_flags(self, args):
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
        required_flags = [
            valid_flag
            for valid_flag in valid_flags.keys()
            if valid_flags[valid_flag]["required"]
        ]
        for required_flag in required_flags:
            if required_flag not in user_flags:
                logger.info(
                    f"{required_flag} is a required flag for the command {args.mode}. Use -h for more info"
                )
                exit(1)

    def _cli_args_to_dict(self):
        """Convert CLI args to dict, normalizing short flags to long flags."""
        args_dict = {}
        i = 1  # Skip script name (sys.argv[0])
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg.startswith(("-", "--")):
                # Case 1: --flag=value
                if "=" in arg:
                    flag, value = arg.split("=", 1)
                    i += 1
                # Case 2: --flag value
                else:
                    flag = arg
                    # Check if next arg is a value (not another flag)
                    if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith(
                        ("-", "--")
                    ):
                        value = sys.argv[i + 1]
                        i += 2
                    else:
                        value = True  # Boolean flag (e.g., "-v")
                        i += 1

                # Normalize short flags to long flags (e.g., "-s" → "--statement")
                if flag in self.parser._option_string_actions:
                    action = self.parser._option_string_actions[flag]
                    long_flag = action.option_strings[-1]  # Get longest flag
                    args_dict[long_flag] = value
                else:
                    args_dict[flag] = value  # Unknown flags
            else:
                i += 1  # Skip non-flag args (e.g., command name)
        return args_dict

    def dict_to_cli_args(self, args_dict):
        args_list = []
        for flag, value in args_dict.items():
            if value is True:  # Boolean flag (e.g., "--verbose")
                args_list.append(flag)
            else:
                args_list.extend([flag, str(value)])
        return args_list

    def handle_args(self):
        # Step 1: Convert CLI args to normalized dict (long flags)
        cli_args = self._cli_args_to_dict()
        logger.info(f"cli args{cli_args}")
        # Step 2: Load JSON config if provided (override CLI)
        if hasattr(self.parser, "json") and cli_args.get("--json"):
            json_args = self._load_json_config(cli_args["--json"])
            # Merge CLI and JSON (JSON takes priority)
            merged_args = {**cli_args, **json_args}
        else:
            merged_args = cli_args

        # Step 3: Convert merged args back to sys.argv format
        sys.argv = [sys.argv[0]] + self._dict_to_cli_args(merged_args)

        # Step 4: Parse final args with argparse
        args = self.parser.parse_args()

        # Validate mode and other flags
        if not args.mode:
            self.parser.print_help()
            return 1
        self.validate_flags(args)
        return args

    def _load_json_config(self, json_path):
        """Load JSON and convert keys to long flags (e.g., "statement" → "--statement")."""
        with open(json_path) as f:
            json_config = json.load(f)
        return {f"--{k}": v for k, v in json_config.items()}

    def _dict_to_cli_args(self, args_dict):
        """Convert dict back to CLI args list (e.g., {"--flag": "value"} → ["--flag", "value"])."""
        args_list = []
        for flag, value in args_dict.items():
            if value is True:  # Boolean flag
                args_list.append(flag)
            else:
                args_list.extend([flag, str(value)])
        return args_list

    async def execute_command(self):
        self.set_cookie_parser()
        self.set_alert_parser()
        self.get_alerts_parser()
        self.rm_alert_parser()
        self.get_rss_link_parser()
        args = self.handle_args()
        logger.info(
            f"Here are the flags of the command {args.mode}: {self.get_flags_for_command(args.mode)}"
        )
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
