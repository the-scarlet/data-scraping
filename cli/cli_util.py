import argparse
import json
from config.config import AppConfig
from src.controllers import google_alerts_controller
import logging


logger = logging.getLogger("Data-scraping")
config = AppConfig()


class CliUtil:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Data scraper")
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
            nargs="*",
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
            help=f"instruments",
        )
        specific_parser.add_argument(
            "-k",
            "--keywords",
            type=str,
            nargs="*",
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

        for key, value in json_args.items():
            if hasattr(args, key):  # Only override existing arguments
                setattr(args, key, value)
            else:
                print(f"Warning: Ignoring unknown JSON key '{key}'")
        return args

    def get_rss_link_parser(self):
        specific_parser = self.subparsers.add_parser("get-rss", help="get RSS")

    def handle_args(self):
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
        return args

    async def execute_command(self):
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
