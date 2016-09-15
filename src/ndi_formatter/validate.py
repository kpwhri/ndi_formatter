import re

import sys
from collections import defaultdict


def output_error(out, line_no, error_type, error_message):
    out.write('{}: {} error: {}\n'.format(line_no, error_type, error_message))


def check_line_length(out, line_no, line, expected_size):
    """expected size includes line feed character, so subtract by 1 to get 100"""
    if len(line) != expected_size:
        output_error(out, line_no, 'line length', 'expected {} actual {}'.format(expected_size - 1, len(line)))


def check(out, line_no, segment, title, regex, requirements):
    if not re.match('^{}$'.format(regex), segment):
        output_error(out, line_no, '{} segment'.format(title),
                     'requirements not met: "{}": {}'.format(segment, requirements))
    return not bool(re.match('^ +$', segment))  # was there something present?


def check_name(out, line_no, segment, title):
    return check(out, line_no, segment, title, '[A-Z]* *', 'left-justified, upper case, alpha')


def check_numeric(out, line_no, segment, title, req, length):
    return check(out, line_no, segment, title, '(\d{{{0}}}| {{{0}}})'.format(length), req)


def check_numeric_range(out, line_no, segment, title, start: int, end: int, length=1):
    res = check_numeric(out, line_no, segment, title, 'numeric between {} and {}'.format(start, end), length)
    if res:  # if number entered
        value = int(segment)
        if value < start or value > end:
            output_error(out, line_no, '{} segment'.format(title),
                         'value not between {} and {}: "{}"'.format(start, end, segment))
    return res


def check_ssn(out, line_no, segment, title):
    return check_numeric(out, line_no, segment, title, '9 digit numeric', 9)


def check_dob(out, line_no, segment):
    month = check_numeric(out, line_no, segment[0:2], 'month', 'numeric, zero-fill', 2)
    day = check_numeric(out, line_no, segment[2:4], 'day', 'numeric, zero-fill', 2)
    year = check_numeric(out, line_no, segment[4:8], 'year', 'numeric', 4)
    return year, month, day


def check_age_units(out, line_no, segment):
    return check_numeric_range(out, line_no, segment, 'age units', 0, 6)


def check_sex(out, line_no, segment):
    return check(out, line_no, segment, 'sex', '(M|F|1|2| )', 'M, F, 1, 2')


def check_race(out, line_no, segment):
    return check_numeric_range(out, line_no, segment, 'race', 0, 8)


def check_marital_status(out, line_no, segment):
    return check_numeric_range(out, line_no, segment, 'marital status', 0, 4)


def check_state(out, line_no, segment, state_of_residence=True):
    return check_numeric_range(out, line_no, segment,
                               'state of {}'.format('residence' if state_of_residence else 'birth'),
                               0, 59, length=2)


def check_id(out, line_no, segment):
    return check(out, line_no, segment, 'optional id', '[A-Z0-9]* *', 'left-justified capitalized alphanumeric')


def check_blank(out, line_no, segment):
    return check(out, line_no, segment, 'blank', '   \n', 'blank spaces followed by newline')


def check_eligibility(out, line_no, fname, lname, ssn, year, month, day, sex):
    """Check if record is eligible for review"""
    if fname and lname and ssn:
        return True
    if fname and lname and month and year:
        return True
    if ssn and year and month and day and sex:
        return True
    output_error(out, line_no, 'eligibility', 'subject is ineligible for NDI submission')
    return False


def check_duplicates(out, records):
    for segment in records:
        if len(records[segment]) > 1:
            duplicates = ', '.join(str(x) for x in records[segment])
            for line_no in records[segment]:
                output_error(out, line_no, 'duplicate',
                             'same record appears in lines {}: "{}"'.format(duplicates, segment))


def validate(input_file, output_file=sys.stderr):
    """Validate input file according to NDI guidelines"""
    with open(input_file) as f:
        try:
            out = open(output_file, 'w')
        except TypeError:
            out = output_file
        records = defaultdict(list)
        for line_no, line in enumerate(f, start=1):
            check_line_length(out, line_no, line, 101)  # 101 because this measures the newline/linefeed character

            # segment check
            lname = check_name(out, line_no, line[0:20], 'last name')
            fname = check_name(out, line_no, line[20:35], 'first name')
            check_name(out, line_no, line[35:36], 'middle initial')
            ssn = check_ssn(out, line_no, line[36:45], 'ssn')
            y, m, d = check_dob(out, line_no, line[45:53])
            check_name(out, line_no, line[53:71], 'father surname')
            check_age_units(out, line_no, line[71:72])
            check_numeric(out, line_no, line[72:74], 'age value', 'zero-fill two-digit numeric', 2)
            sex = check_sex(out, line_no, line[74:75])
            check_race(out, line_no, line[75:76])
            check_marital_status(out, line_no, line[76:77])
            check_state(out, line_no, line[77:79], True)
            check_state(out, line_no, line[79:81], False)
            check_id(out, line_no, line[81:91])
            check_id(out, line_no, line[91:97])
            check_blank(out, line_no, line[97:101])

            # eligibility check
            check_eligibility(out, line_no, fname, lname, ssn, y, m, d, sex)

            # check for duplicate records (ignore id)
            records[line[0:81]].append(line_no)

        # check for duplicate records (ignoring id)
        check_duplicates(out, records)

        out.close()  # both stderr and files can be closed


def main():
    import argparse
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('-i', '--input-file', required=True,
                        help='Input candidate NDI file.')
    parser.add_argument('-o', '--output-file', default=sys.stderr,
                        help='File containing any validation errors.')
    args = parser.parse_args()

    validate(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
