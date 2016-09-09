"""Use information provided by input file to generate NDI data request.

**Input file**:
    - SAS7BDAT, CSV, JSON
    - specify column names using parameters

**Output file**:
    - file according to NDI coding specifications
    .. note:: National Center for Health Statistics. National Death Index user’s guide. Hyattsville, MD. 2013

**Description**:
    - read in and parse format
    - ensure that all subjects have at least minimum eligible combination of data
    - output data to specified file
"""
import csv

from sas7bdat import SAS7BDAT


class FileHandler(object):
    def __init__(self, input_file, input_format):
        self.input_file = input_file
        self.input_format = input_format
        self.line = None
        self.iterator = None
        self.handler = None

    def __enter__(self):
        if self.input_format == 'sas':
            self.handler = SAS7BDAT(self.input_file).__enter__()
            self.iterator = self.handler
        elif self.input_format == 'csv':
            self.handler = open(self.input_file, 'rb').__enter__()
            self.iterator = csv.reader(self.handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.handler.__exit__(exc_type, exc_val, exc_tb)

    def get(self, col):
        return col


class AttributeGetter(object):

    def __init__(self, name, ssn, birthdate, sex):
        self.name = name
        self.ssn = ssn
        self.birthdate = birthdate
        self.sex = sex

    def process(self, subject):
        """Extract each bit of information from line"""
        name = self.name.get(subject)
        ssn = self.ssn.get(subject)
        birthdate = self.birthdate.get(subject)
        sex = self.sex.get(subject)

    @staticmethod
    def validate(name, ssn, birthdate, sex):
        """Validate that subject satisfies NDI minimum specs


        """
        validated = False
        if name[0] and name[1]:
            if ssn or birthdate[0] and birthdate[1]:
                validated = True
        if ssn and birthdate[0] and birthdate[1] and birthdate[2] and sex:
            validated = True


class ValidatorException(ValueError):
    pass


def create_document(input_file, input_format, output_file):
    with FileHandler(input_file, input_format) as f:
        with open(output_file, 'w') as out:

            out.write('{:<20}'.format(f.get('fname')))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('-i', '--input-file', required=True,
                        help='Input file path.')
    parser.add_argument('-o', '--output-file', default='ndi_output',
                        help='NDI-formatted output file.')
    parser.add_argument('-f', '--input-format', choices=['sas', 'csv', 'json'], default='sas',
                        help='Input file format.')
    parser.add_argument('-L', '--log-file', default='ndi_formatter.log',
                        help='Logfile name.')

    parser.add_argument('--fname', help='Name/index of column with first name')
    parser.add_argument('--lname', help='Name/index of column with last name')
    parser.add_argument('--mname', help='Name/index of column with middle name/initial')
    parser.add_argument('--name', help='Name/index of column with full name')
    parser.add_argument('--ssn', help='Name/index of column with ssn')
    parser.add_argument('--birth-month', help='Name/index of column with birth month')
    parser.add_argument('--birth-year', help='Name/index of column with birth year')
    parser.add_argument('--birthdate', help='Name/index of column with birthdate')
    parser.add_argument('--sex', help='Name/index of column with sex')

    # additional configurations

    args = parser.parse_args()
