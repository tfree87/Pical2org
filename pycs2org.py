#!/usr/bin/python3

import sys
import argparse
from datetime import date, datetime, timedelta, tzinfo
from icalendar import Calendar


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

    fh = open(args.INPUT_FILE, "r", encoding="utf-8")

    if args.output:
        fh_w = open(args.output[0], "w", encoding="utf-8")
    else:
        fh_w = sys.stdout

    try:
        cal = Calendar.from_ical(fh.read())
    except:
        print("ERROR parsing ical file", file=sys.stderr)
        exit(1)
        pass

    for event in cal.walk():
        SUMMARY = ""
        if event.get("summary") is not None:
            SUMMARY = event.get("summary")
            SUMMARY = SUMMARY.replace("\\,", ",")
        else:
            SUMMARY = "(No title)"
        fh_w.write("* {}\n".format(SUMMARY))

        if event.get("dtstart") and event.get("dtend"):
            fh_w.write(
                "  <{}>--<{}>\n".format(
                    event.get("dtstart").dt.strftime("%Y-%m-%d %H:%M"),
                    event.get("dtend").dt.strftime("%Y-%m-%d %H:%M"),
                )
            )
        if event.get("dtstart") and not event.get("dtend"):
            fh_w.write(
                "  <{}>\n".format(event.get("dtstart").dt.strftime("%Y-%m-%d %H:%M"))
            )

        if event.get("description") is not None:
            description = "\n".join(event.get("description").split("\\n"))
            description = description.replace("\\,", ",")
            fh_w.write("{}\n".format(description))

        fh_w.write("\n")


if __name__ == "__main__":
    main()
