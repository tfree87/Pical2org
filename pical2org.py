#!/usr/bin/python3

import os
import sys
import argparse
from datetime import datetime, timezone
from icalendar import Calendar


def datetime2String(dateTime):
    if isinstance(dateTime, datetime):
        return dateTime.astimezone().strftime("%Y-%m-%d %H:%M")
    else:
        return dateTime.strftime("%Y-%m-%d")


class orgEvent:
    def __init__(self, event):
        # Store the summary of the event
        if event.get("summary") is not None:
            self.summary = event.get("summary")
            self.summary = self.summary.replace("\\,", ",")
        else:
            self.summary = "(No title)"

        # Store the start and end time of the event
        self.dtstart = event.get("dtstart").dt
        if event.get("dtend") is not None:
            self.dtend = event.get("dtend").dt
        else:
            self.dtend = None

        # Store the description of the event
        if event.get("description") is not None:
            self.description = "\n".join(event.get("description").split("\\n"))
            self.description = self.description.replace("\\,", ",")
        else:
            self.description = ""

    def __str__(self):
        results = ""
        results = "* {}\n".format(self.summary)

        if self.dtstart and self.dtend:
            results += "  <{}>--<{}>\n".format(
                datetime2String(self.dtstart),
                datetime2String(self.dtend),
            )

        elif self.dtstart and not self.dtend:
            results += "  <{}>\n".format(datetime2String(self.dtstart))

        results += "{}\n".format(self.description)

        return results


class Convertor:
    def __init__(self, iCalendar):
        icalFile = open(iCalendar, "r", encoding="utf-8")
        self.calendar = Calendar.from_ical(icalFile.read())

    def __call__(self):
        results = ""

        for component in self.calendar.walk("VEVENT"):
            event = orgEvent(component)
            results += str(event)

        return results


def createParser():
    """Creates the default ArgumentParser object for the script

    Creates a parser using the argparse library to collect arguments
    from the command line. These arguments are then stored as and
    ArgumentParser object and returned.

    Returns
    -------
    ArgumentParser
        An ArgumentParser object

    """

    # Create the parser
    parser = argparse.ArgumentParser(
        description="Converts an ical (.ics) file into a text file formatted for use in Emacs org-mde.",
        add_help=True,
        fromfile_prefix_chars="@",
    )

    # Tell the parser which version of the script this is
    parser.version = "0.1"

    # Add an argument to accept an input file
    parser.add_argument("INPUT_FILE", help="A ical (.ics) file to be read.")

    # Add an option to output results to a file instead of stdout
    parser.add_argument(
        "-o",
        "--output",
        help="Name of file to store the output results.",
        action="store",
        type=str,
        nargs=1,
        metavar="OUTPUT_FILE",
    )

    return parser


def main():
    parser = createParser()
    args = parser.parse_args()

    if args.output:

        # Check if a file with the same name as output file exists
        if os.path.exists(args.output[0]) and not args.force_clobber:
            print(
                "File {outfile} exists.\nPlease specify a new name or run"
                "script again with -f to force clobbering of existing "
                "file".format(outfile=args.output[0])
            )
        else:
            convertor = Convertor(args.INPUT_FILE)
            with open(args.output[0], "w") as outFile:
                outFile.write(convertor())

    # If no output file is given print data to stdout
    else:
        convertor = Convertor(args.INPUT_FILE)
        print(convertor())


if __name__ == "__main__":
    main()
