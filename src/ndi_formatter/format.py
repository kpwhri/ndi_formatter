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
import itertools
import json
import logging
import re

import sys

from ndi_formatter.attributes import Attribute, Name, SSN, BirthDate, Sex, State, AttributeMapping, DeathAge
from ndi_formatter.lookup import MS_TO_CODES, RACE_TO_CODES
from ndi_formatter.utils import flatten_list, combinations
from ndi_formatter.validate import validate

try:
    from sas7bdat import SAS7BDAT

    SAS7BDAT_IMPORT = True
except ImportError:
    SAS7BDAT_IMPORT = False


class FileHandler(object):
    def __init__(self, input_file, input_format, ignore_case=True):
        self.input_file = input_file
        self.input_format = input_format.lower()
        self.line = None
        self.iterator = None
        self.handler = None
        self.ignore_case = ignore_case

    def __enter__(self):
        if self.input_format in ['sas', 'csv']:
            if self.input_format == 'sas':
                self.handler = SAS7BDAT(self.input_file).__enter__()
                self.iterator = self.handler.readlines()
                self.header = next(self.iterator)
            elif self.input_format == 'csv':
                self.handler = open(self.input_file, 'r').__enter__()
                self.iterator = csv.reader(self.handler)  # first line is header
                self.header = self.iterator.__next__()

            if self.ignore_case:
                self.header_to_index = {name.upper(): idx for idx, name in enumerate(self.header)}
            else:
                self.header_to_index = {name: idx for idx, name in enumerate(self.header)}

        elif self.input_format in ['json']:
            self.handler = open(self.input_file).__enter__()
            lst = json.load(self.handler)
            if self.ignore_case:
                self.header_to_index = {n.upper(): n for n in lst[0].keys()}  # no indices in json
            else:
                self.header_to_index = {n: n for n in lst[0].keys()}  # no indices in json
            self.iterator = iter(lst)

        else:
            raise ValueError('Unsupported file type: "{}"')

        self.next_line()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.handler.__exit__(exc_type, exc_val, exc_tb)

    def __next__(self):
        if self.input_format == 'sas':
            self.line = next(self.iterator)
        elif self.input_format == 'csv':
            self.line = next(self.iterator)
        elif self.input_format == 'json':
            self.line = next(self.iterator)

    def next_line(self):
        try:
            self.__next__()
        except StopIteration:
            return False
        return bool(self.line)

    def get(self, col, perm_names=None):
        if isinstance(col, Attribute):
            return self._get(col)
        elif isinstance(col, list):
            results = []
            p_names = []
            for i, c in enumerate(col):
                res = self._get(c)
                if res.strip() and res not in results:
                    p_names.append(c.__class__.__name__[:2].upper() + str(i))  # TODO: what to include here?
                    results.append(res)
            if len(results) > 1:
                perm_names.append(p_names)
                return results
            elif len(results) == 1:
                return results[0]
            return ''  # there's only one attribute
        else:
            raise ValueError('Unrecognized format for Attribute: {}'.format(col))

    def _get(self, col: Attribute):
        return col.get(self.line, self.header_to_index)


class Validator(object):
    @staticmethod
    def validate(name, ssn, birthdate, sex):
        """Validate that subject satisfies NDI minimum specs


        """
        validated = 0
        if name[0] and name[1]:
            if ssn or birthdate[0] and birthdate[1]:
                validated = 2
            elif birthdate[0]:  # only year and no ssn
                validated = 1
        if ssn and birthdate[0] and birthdate[1] and birthdate[2] and sex:
            validated = 2
        return validated


class ValidatorException(ValueError):
    pass


def _format_name(name, length):
    remove_illegal = re.compile('[^a-zA-Z]')
    return remove_illegal.sub('', name).upper()[:length]


def _format_string(name, length):
    return str(name)[:length]


def _format_number(number, length):
    if number:
        return str(number).zfill(length)[:length]
    else:
        return ''


def month_iterator():
    for i in range(1, 13):
        yield 'M{:02d}'.format(i)


def create_document(input_file, input_format, output_file, name, ssn_col, birthdate, death_col, sex_col,
                    race_col, ms_col, residence_state_col, birth_state_col, id_col,
                    options):
    Attribute.IGNORE_CASE = 'case_insensitive_columns' in options
    with FileHandler(input_file, input_format, ignore_case=Attribute.IGNORE_CASE) as f:
        with open(output_file, 'w') as out:
            while True:
                # this is for naming each permutation
                permutation_names = []  # items must be added in the same order in which they are output

                # get name
                names = lname, fname, mname, sname = f.get(name)

                ssn = f.get(ssn_col)
                year, month, day = f.get(birthdate)

                # age_units will be treated as year unless otherwise specified by "for-all" option
                age, age_units = f.get(death_col)
                sex = f.get(sex_col)
                race = f.get(race_col)
                marital_status = f.get(ms_col)
                state_of_residence = f.get(residence_state_col, permutation_names)
                state_of_birth = f.get(birth_state_col)
                id_value = f.get(id_col)

                # validate
                valid = Validator.validate(names,
                                           ssn,
                                           (year, month, day),
                                           sex)

                # permutations
                # check names
                names = [names]
                p_names = []
                if ('-' in lname or ' ' in lname) \
                        and ('duplicate_records_on_lname' in options
                             or ('female_hyphen_lname_to_sname' in options and sex in ['2', 'F'])):
                    p_names.append('')
                    if 'duplicate_records_on_lname' in options:
                        for ln in re.compile('-| ').split(lname):
                            names.append([ln, fname, mname, sname])
                            p_names.append('L')
                    if 'female_hyphen_lname_to_sname' in options and sex in ['2', 'F']:
                        sn = re.compile('-| ').split(lname)
                        if len(sn) == 2:  # only handle when there are two names
                            sn1, sn2 = sn
                            # Dutch/German "from" common case of FPs
                            if sn1.upper() in ['VAN', 'VON', 'VANDER', 'VONDER', 'VANDEN', 'VER', 'VANDE', 'VANT',
                                               'ST']:
                                p_names = []
                            else:
                                # account for both possible orderings
                                names.append([sn2, fname, mname, sn1])
                                names.append([sn1, fname, mname, sn2])
                                p_names.append('S1')
                                p_names.append('S2')
                        else:
                            p_names = []

                if p_names:
                    permutation_names.append(p_names)

                # check validation and add month if requested
                if valid == 2:
                    pass  # correctly validated
                elif valid == 1 and 'duplicate_records_on_year_only' in options:
                    month = range(1, 13)
                    permutation_names.append(month_iterator())
                else:
                    msg = 'Invalid record for subject: {}'.format(id_value or lname or ssn or year)
                    logging.error(msg)
                    if 'include_invalid_records' in options:
                        logging.warning('Including invalid record: {}'.format(id_value or lname or ssn or year))
                    elif 'ignore_invalid_records' in options:
                        logging.warning('Ignoring invalid record: {}'.format(id_value or lname or ssn or year))
                        continue
                    else:
                        raise ValidatorException(msg)

                # write line (or multiple lines)
                values = [names, ssn, year, month, day, age_units, age, sex, race,
                          marital_status, state_of_residence, state_of_birth, id_value]
                for arguments, id_dupe in zip(combinations(values), itertools.product(*permutation_names)):
                    if isinstance(id_dupe, tuple) and len(id_dupe) > 0:
                        id_dupe = id_dupe[0]
                    write(out, *flatten_list(arguments), id_dupe=id_dupe or '')

                # move to next line
                if not f.next_line():
                    break


def write(out, lname, fname, mname, sname, ssn, year, month, day, age_units, age, sex, race,
          marital_status, state_of_residence, state_of_birth, id_value, id_dupe=''):
    # 1. name of person in study group
    out.write('{:<20}'.format(_format_name(lname, 20)))
    out.write('{:<15}'.format(_format_name(fname, 16)))
    out.write('{:<1}'.format(_format_name(mname, 1)))
    # 2. social security number
    out.write('{:<9}'.format(_format_number(ssn, 9)))
    # 3. date of birth
    out.write('{:<2}'.format(_format_number(month, 2)))
    out.write('{:<2}'.format(_format_number(day, 2)))
    out.write('{:<4}'.format(_format_number(year, 4)))
    # 4. father's surname
    out.write('{:<18}'.format(_format_name(sname, 18)))
    # 5. age at death
    if age_units:
        out.write('{:<1}'.format(age_units))
        out.write('{:<2}'.format(_format_number(age, 2)))
    else:
        out.write('{:<3}'.format(_format_number(age, 3)))
    # 6. sex
    out.write('{:<1}'.format(sex))
    # 7. Race
    out.write('{:<1}'.format(race))
    # 8. Marital status
    out.write('{:<1}'.format(marital_status))
    # 9. State of residence
    out.write('{:<2}'.format(state_of_residence))
    # 10. State of birth
    out.write('{:<2}'.format(state_of_birth))
    # 11. Id number
    out.write('{:<10}'.format(_format_number(id_value, 10)))
    # 12. Duplicate marker
    out.write('{:<6}'.format(_format_string(id_dupe, 6)))
    # 13. Blank field
    out.write('{:<3}'.format(''))
    # new line character: this will vary depending on platform
    out.write('\n')


def output_sample_config_file():
    print("# comments like this will need to be removed from your config file")
    print("--input-file=PATH_TO_INPUT_FILE")
    print("--output-file=PATH_TO_OUTPUT_FILE")
    print("--input-format=CSV|SAS7BDAT|JSON")
    print("--name=NAME_COL")
    print("--ssn=SSN_COL")
    print("--birthdate=BIRTHDATE_COL  # or specify birth-day, birth-month, and birth-year")
    print("--sex=SEX_COL")
    print("--sname=SNAME_COL")
    print("--death-age=DEATH_AGE_COL")
    print("--race=RACE_COL,RACE2_COL")
    print("--marital-status=MARRIED_STATUS_COL")
    print("--id=ID_COL")
    print("--same-state-of-residence-for-all=WASHINGTON")
    print("--state-of-birth=STATE_COL")
    print('--name-format="F m L"')
    print('--sex-format="M1,F2"')
    print('--marital-status-mapping')
    print('SINGLE')
    print('MARRIED')
    print('WIDOWED')
    print('DIVORCED')
    print('--race-mapping')
    print('"Pacific Islander"')
    print('White')
    print('Black')
    print('Indian')
    print('Chinese')
    print('Japanese')
    print('Hawaiian')
    print('X  # skip this race')
    print('Filipino')
    print("--validate-generated-file=PATH_TO_VALIDATION_FILE")


def multiple_args(klass, column_names, *args):
    if column_names:
        return [klass(col, *args) for col in column_names.split(',')]
    else:
        return klass(column_names, *args)


def main():
    import argparse

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@', add_help=False)
    parser.add_argument('-c', '--create-sample', default=False, action='store_true',
                        help='Create sample. Do not process anything.')
    args, _ = parser.parse_known_args()
    if args.create_sample:
        output_sample_config_file()
        return

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@', add_help=False)
    parser.add_argument('-i', '--input-file',
                        help='Input file path.')
    parser.add_argument('-o', '--output-file', default='ndi_output',
                        help='NDI-formatted output file.')
    parser.add_argument('-f', '--input-format', type=str.lower, choices=['sas', 'csv', 'json'], default='sas',
                        help='Input file format.')
    parser.add_argument('-L', '--log-file', default='ndi_formatter.log',
                        help='Logfile name.')
    parser.add_argument('-h', '--help', action='store_true', default=False)

    parser.add_argument('--fname', help='Name/index of column with first name')
    parser.add_argument('--lname', help='Name/index of column with last name')
    parser.add_argument('--mname', help='Name/index of column with middle name/initial')
    parser.add_argument('--sname', help='Name/index of column with father name')
    parser.add_argument('--name', help='Name/index of column with full name')
    parser.add_argument('--ssn', help='Name/index of column with ssn; accepts multiple columns')
    parser.add_argument('--birth-day', help='Name/index of column with birth day')
    parser.add_argument('--birth-month', help='Name/index of column with birth month')
    parser.add_argument('--birth-year', help='Name/index of column with birth year')
    parser.add_argument('--birthdate', help='Name/index of column with birthdate')
    parser.add_argument('--sex', help='Name/index of column with sex; accepts multiple columns')
    parser.add_argument('--death-age', help='Name/index of column with age at death (in years)')
    parser.add_argument('--race', help='Name/index of column with race; accepts multiple columns')
    parser.add_argument('--marital-status', help='Name/index of column with marital status; accepts multiple columns')
    parser.add_argument('--state-of-residence', help='Name/index of column with state of residence;'
                                                     ' accepts multiple columns')
    parser.add_argument('--state-of-birth', help='Name/index of column with state of birth; accepts multiple columns')
    parser.add_argument('--id', help='Name/index of column with id number')

    # additional configuration/formatting
    parser.add_argument('--race-mapping', nargs=9, default=None,
                        metavar=('OA/PI', 'WH', 'BA', 'NA/IN', 'CH', 'JP', 'HI', 'Onon-WH', 'FL'),
                        help='Mapping of variable to NDI race in following order: '
                             'Other Asian/Pacific Islander, White, Black, Native American, Chinese, Japanese, '
                             'Hawaiian, Other nonwhite, Filipino; everything else will be treated '
                             'as unknown; use an "X" instead of a value to skip a race')
    parser.add_argument('--marital-status-mapping', nargs=4, default=None,
                        metavar=('Single', 'Married', 'Widowed', 'Divorced'),
                        help='Mapping of variable to ND marital status in following order: '
                             'Never married/single, Married, Widowed, Divorced; everything else will '
                             'be treated as unknown; use an "X" instead of a value to skip a status')
    parser.add_argument('--same-state-of-residence-for-all', default=None,
                        help='State abbreviation/number for all subjects')
    parser.add_argument('--same-state-of-birth-for-all', default=None,
                        help='State abbreviation/number for all subjects')
    parser.add_argument('--age-at-death-units-for-all', default=None,
                        choices=['MONTH', 'WEEK', 'DAY', 'HOUR', 'MINUTE'],
                        help='Specify units for age of death it not years.')
    parser.add_argument('--name-format', default='L, F M.',
                        help='Format to parse full names. L=Last name, F=first name, M=Middle name, S=father name, '
                             'X=ignore; algorithm will continue to add any character found to the name until the next '
                             'non-[LFMSX] character is found')
    parser.add_argument('--date-format', default=None,
                        help='Date format for parsing year/month/day from a date; for more documentation, see '
                             'https://docs.python.org/dev/library/datetime.html#strftime-and-strptime-behavior')
    parser.add_argument('--sex-format', default=None,
                        help='Specify the values for male/female if different than NDI using "MALE,FEMALE"; '
                             'NDI default is "M,F" or "1,2" or "M1,F2"')
    parser.add_argument('--validate-generated-file', default=None, const=sys.stderr, nargs='?',
                        help='Validate NDI file and output results to specified file.')
    parser.add_argument('--strip-lname-suffix', default='', const='JR,SR,II,III,IV', nargs='?', type=str.upper,
                        help='Look for suffixes in lname column and strip them out; default: JR, SR, II, III, IV;'
                             ' if specifying an argument, use a comma-separated list as a single string')
    parser.add_argument('--strip-lname-suffix-attached', default='', const='JR,SR,II,III,IV', nargs='?',
                        type=str.upper,
                        help='Look for suffixes in last word of lname column and strip them out even if they '
                             ' are attached to the word itself; default: JR, SR, II, III, IV;'
                             ' if specifying an argument, use a comma-separated list as a single string')

    args, unk = parser.parse_known_args()

    # additional configurations
    opt_parser = argparse.ArgumentParser()
    opt_parser.add_argument('--duplicate-records-on-lname', action='store_true',
                            help='If space or hyphen in last name, duplicate the subject into three records: '
                                 '1) both together; 2) only the first part; 3) only the second part')
    opt_parser.add_argument('--female-hyphen-lname-to-sname', action='store_true',
                            help='If hyphen in last name of female, duplicate the subject into two records: '
                                 '1) both together; 2) only the first part with the second part in the father '
                                 'last name field')
    opt_parser.add_argument('--duplicate-records-on-year-only', action='store_true',
                            help='Create 12 duplicate records if only a year and no month')
    opt_parser.add_argument('--ignore-invalid-records', action='store_true',
                            help='Ignore records which invalid per NDI requirements due to insufficient information')
    opt_parser.add_argument('--include-invalid-records', action='store_true',
                            help='Include records which invalid per NDI requirements due to insufficient information')
    opt_parser.add_argument('--case-sensitive-columns', dest='case_insensitive_columns', action='store_false',
                            help='All columns will be treated as case-sensitive.')
    oargs = opt_parser.parse_args(unk)

    if args.help or not args.input_file:
        parser.print_help()
        opt_parser.print_help()
        sys.exit(0)

    create_document(args.input_file, args.input_format, args.output_file,
                    # multiples would be very difficult to handle for names
                    Name(args.name, args.fname, args.mname, args.lname, args.sname, args.name_format,
                         args.strip_lname_suffix.split(','), args.strip_lname_suffix_attached.split(',')),
                    multiple_args(SSN, args.ssn),
                    # multiples would need to be incorporated into additional logic in validation section
                    BirthDate(args.birthdate, args.birth_year, args.birth_month, args.birth_day, args.date_format),
                    DeathAge(args.death_age, args.age_at_death_units_for_all),
                    multiple_args(Sex, args.sex, args.sex_format),
                    multiple_args(AttributeMapping, args.race, RACE_TO_CODES, args.race_mapping),
                    multiple_args(AttributeMapping, args.marital_status, MS_TO_CODES, args.marital_status_mapping),
                    multiple_args(State, args.state_of_residence, args.same_state_of_residence_for_all),
                    multiple_args(State, args.state_of_birth, args.same_state_of_birth_for_all),
                    Attribute(args.id),  # can't have multiples
                    {x for x, y in vars(oargs).items() if y},
                    )

    if args.validate_generated_file:
        validate(args.output_file, args.validate_generated_file)
