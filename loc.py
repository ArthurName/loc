"""loc.py: Simple lines of code ("loc") counter.

Run with -v for verbose output -- lines of docstrings, comments and empty
lines are reported in addition to lines of code. Run with -f to list details
for every file.

Examples:
     python loc.py loc.py
     python loc.py . -rvf
     python loc.py . test/ -v

This is a one-file project; classes and application reside in the same file.
"""

from optparse import OptionParser
import os
import glob

COL_WIDTH = 8

#
# Classes
#
class LocCounter(object):
    """Count number of lines of code, and optionally lines of docstrings,
    comments and empty lines."""

    def __init__(self, fname=''):
        """Initialize with filename.

        Arguments:
            fname:      Name of file to count lines in (str).
        """
        self.fname = fname

        # Counters
        self.nbr_loc = 0
        self.nbr_docstrings = 0
        self.nbr_comments = 0
        self.nbr_empty = 0

        # Count!
        if self.fname:
            self.count(self.file_lines())

    def count(self, flines):
        """Count number of lines of code (and more) in a Python file.

        Arguments:
            flines:     The lines of a python file (list).

        Precondition:
            Docstrings defined using triple quotes.

        Postcondition:
            Counters (member variables) set.
        """
        docstring = False
        docstring_char = ''
        for line in flines:
            line = line.strip()

            # Empty line
            if not line:
                self.nbr_empty += 1
                continue

            # Comment
            if line.startswith('#'):
                self.nbr_comments += 1
                continue

            # Single line docstring
            if not docstring and len(line) > 3:
                if (line.startswith('"""') and line.endswith('"""')) or \
                                line.startswith("'''") and line.endswith("'''"):
                    self.nbr_docstrings += 1
                    continue

            # Start of (multiline) docstring
            if not docstring:
                if line.startswith('"""'):
                    docstring_char = '"'
                    docstring = True
                    self.nbr_docstrings += 1
                    continue
                elif line.startswith("'''"):
                    docstring_char = "'"
                    docstring = True
                    self.nbr_docstrings += 1
                    continue

            # End of docstring
            else:
                if (docstring_char == '"' and line.endswith('"""')) or \
                        (docstring_char == "'" and line.endswith("'''")):
                    docstring = False
                    self.nbr_docstrings += 1
                continue

            # A line of code!
            self.nbr_loc += 1

    def file_lines(self):
        """Retrieve file lines.

        Returns:
            The lines of the file self.fname (list).
        """
        fobject = open(self.fname, 'r')
        fdata = fobject.read()
        fobject.close()
        return fdata.splitlines()

    def __str__(self):
        """String representation.

        Returns:
            LOC and filename (str).
        """
        return "%s  %s" % (str(self.nbr_loc).rjust(COL_WIDTH), self.fname)

    def verbose(self):
        """Verbose string representation.

        Returns:
            LOC, docstrings, comments, empty lines and filename (str).
        """
        return "%s%s%s%s  %s" % (str(self.nbr_loc).rjust(COL_WIDTH),
                                 str(self.nbr_docstrings).rjust(COL_WIDTH),
                                 str(self.nbr_comments).rjust(COL_WIDTH),
                                 str(self.nbr_empty).rjust(COL_WIDTH),
                                 self.fname)


class MultipleFileLocCounter(object):
    """Count lines of code and more in multiple files."""

    def __init__(self, recurse=False):
        """Initialize with settings.

        Arguments:
            recurse:    Recurse directories or not (boolean)?
        """
        self.recurse = recurse
        self.filenames = None
        self.found_files = list()
        self.counted = list()
        self.total_loc = 0
        self.total_docstrings = 0
        self.total_comments = 0
        self.total_empty = 0

    def count(self):
        """Count loc, docstrings etc for every file.

        Precondition:
            Run self.add() first, so that self.found_files is set.

        Postcondition:
            self.counted contains a LocCounter object for each file.
        """
        # Count in files.
        for fname in self.found_files:
            self.counted.append(LocCounter(fname))

        # Count totals.
        for counter in self.counted:
            self.total_loc += counter.nbr_loc
            self.total_docstrings += counter.nbr_docstrings
            self.total_comments += counter.nbr_comments
            self.total_empty += counter.nbr_empty

    def add(self, filenames, recurse=None, first=True):
        """Gather .py files from a list of files and directories.

        Raises:
            IOError; if a file or directory, that is explicitly supplied by the
            user (i.e. not found during recursion), or globbed from a user
            supplied directory, does not exist or is inaccessible due to
            permissions.

        Arguments:
            filenames:      Names of files and directories to look in (list).
            recurse:        Recurse directories or not (boolean)?
            first:          Intended for internal use only; is this the first
                            run or a recursive one (boolean)?
        """
        if recurse is None:
            recurse = self.recurse
        self.filenames = filenames

        for fname in self.filenames:
            if len(fname) != 2 and fname.startswith("./"):
                fname = fname[2:]
            if not os.path.exists(fname):
                if first:
                    raise IOError("Error: Dir/file '%s' does not exist." % fname)
                else:
                    continue
            if not os.access(fname, os.R_OK):
                if first:
                    raise IOError("Error: Dir/file '%s' is inaccessible." % fname)
                else:
                    continue
            if os.path.isdir(fname):
                if not fname.endswith('/'):
                    fname += '/'
                items = glob.glob(fname + '*')
                if items:
                    if recurse or first:
                        self.add(items, recurse, first=False)
            elif fname.endswith(".py") and fname not in self.found_files:
                self.found_files.append(fname)

    def __str__(self):
        """String representation: total LOC.

        Returns:
            Total LOC (str).
        """
        return str(self.total_loc)

    def verbose(self):
        """Verbose string representation.

        Returns:
            Total LOC, docstrings, comments and empty lines (str).
        """
        return "%s%s%s%s  " % (str(self.total_loc).rjust(COL_WIDTH),
                               str(self.total_docstrings).rjust(COL_WIDTH),
                               str(self.total_comments).rjust(COL_WIDTH),
                               str(self.total_empty).rjust(COL_WIDTH))

#
# Application
#

def parse_command_line():
    """Parse command line.

    Returns:
        options, filenames:     User options and provided filenames.
    """
    parser = OptionParser()
    parser.add_option("-r", "--recurse", help="Recurse subdirectories.",
                      action="store_true", dest="recurse")
    parser.add_option("-v", "--verbose", help="Verbose output.",
                      action="store_true", dest="verbose")
    parser.add_option("-f", "--files", help="Show details about each file.",
                      action="store_true", dest="files")
    return parser.parse_args()


def main():
    """Application: Get user options and filenames and view counters."""
    # Get options
    options, filenames = parse_command_line()

    # Count.
    mfloc = MultipleFileLocCounter(options.recurse)
    mfloc.add(filenames)
    mfloc.count()

    # View file counters.
    if mfloc.counted:
        if options.verbose:
            header = "%s%s%s%s  " % ("LOC".rjust(COL_WIDTH),
                                     "DOCSTR".rjust(COL_WIDTH),
                                     "CMMNTS".rjust(COL_WIDTH),
                                     "EMPTY".rjust(COL_WIDTH))
            if options.files:
                header += "FILENAME".rjust(COL_WIDTH)
            print header
            if options.files:
                for filecounter in mfloc.counted:
                    print filecounter.verbose()
            print mfloc.verbose()
        elif options.files:
            for filecounter in mfloc.counted:
                print filecounter
            print mfloc
        else:
            print mfloc


# Launcher
if __name__ == '__main__':
    main()
