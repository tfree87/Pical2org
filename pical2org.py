#!/usr/bin/python3

import os
import sys
import argparse
from datetime import datetime, timedelta
from icalendar import Calendar
import recurring_ical_events
from urllib.request import urlopen
import validators

WINDOW = 365


def org_date(dateTime):
    if isinstance(dateTime, datetime):
        return dateTime.astimezone().strftime("<%Y-%m-%d %a %H:%M>")
    else:
        return dateTime.strftime("<%Y-%m-%d %a>")


def create_header(title="Calendar", author="", email=""):
    results = ""
    results += "#+TITLE: {}\n".format(title)
    results += "#+AUTHOR: {}\n".format(author)
    results += "#+EMAIL: {}\n".format(email)
    results += "#+DESCRIPTION: converted using the Pical2org python script\n"
    results += "#+CATEGORY: calendar\n"
    results += "\n\n"

    return results


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

        self.isDateTime = isinstance(self.dtstart, datetime)

        if event.get("dtend") is not None:
            self.dtend = event.get("dtend").dt

            # If all day event, then dtstart and dtend are datetime.date
            # objects and dtend is exactly one day in the future.
            # The dtend can be removed to make it more elegant in org-mode
            if not self.isDateTime and self.dtend == self.dtstart + timedelta(days=1):
                self.dtend = None
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

        # Event has a start time and end time
        if self.dtstart and self.dtend:
            results += "{}--{}\n".format(
                org_date(self.dtstart),
                org_date(self.dtend),
            )

        # Event only has a start time
        elif self.dtstart and not self.dtend:
            results += "{}\n".format(org_date(self.dtstart))

        results += "{}\n".format(self.description)

        return results


class Convertor:
    def __init__(self, args):
        icalFile = self.read_file(args.INPUT_FILE)
        self.calendar = Calendar.from_ical(icalFile.read())
        self.startDate = datetime.now() - timedelta(days=WINDOW)
        self.endDate = datetime.now() + timedelta(days=WINDOW)

    def __call__(self):
        results = ""
        results = create_header()
        events = recurring_ical_events.of(self.calendar).between(
            self.startDate, self.endDate
        )
        for component in events:
            event = orgEvent(component)
            results += str(event)
            
        return results 
    
    def read_file(self, file_name):
        """Open the file from the local system or a url and return it
        
        Take a string representing either a url of a file or a name of
        a local file and return the open file.
        
        Parameters
        ----------
        file_name : str
            A url of a remote file or a path to a local file
        
        """
        if validators.url(file_name) is True:
            f = urlopen(file_name)
        else:
            try:
                f = open(file_name, "r", encoding="utf-8")
            except OSError:
                print("Could not open/read file: ", f)
                sys.exit()
                
        return f

    
def create_parser():
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
    parser.version = "1.0"

    # Add an argument to accept an input file
    parser.add_argument("INPUT_FILE", help="A ical (.ics) file to be read. This can either be a path to a local or it may be a url to a remote file.")

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

    # Add a window determining how many days to convert events
    parser.add_argument(
        "-w",
        "--window",
        help="Length of time before and after today in which events will be collected",
        action="store",
        type=int,
        nargs="?",
        default=365,
    )

    # Add an option to force clobbering of the output file
    parser.add_argument(
        "-f",
        "--force_clobber",
        help="Force clobbering of and output file i the file already exists. If this option is provided, the output file will overwrite the existing file with the same name.",
        action="store_true",
        default=False,
    )
    
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    
    WINDOW = args.window
    
    # Check to see if results should be saved to a file
    if args.output:
        
        # Check if a file with the same name as output file exists
        if os.path.exists(args.output[0]) and not args.force_clobber:
            print(
                "File {outfile} exists.\nPlease specify a new name or run"
                "script again with -f to force clobbering of existing "
                "file".format(outfile=args.output[0])
            )
        else:
            convertor = Convertor(args)
            with open(args.output[0], "w") as outFile:
                outFile.write(convertor())

    # If no output file is given print data to stdout
    else:
        convertor = Convertor(args)
        print(convertor())


# If this file is called directly, then execute main()
if __name__ == "__main__":
    main()
