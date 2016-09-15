import logging
from datetime import datetime, date as dt_date

try:
    import dateutil.parser as dparser

    DATEUTIL_IMPORT = True
except ImportError:
    DATEUTIL_IMPORT = False

from ndi_formatter.lookup import STATES_TO_CODES


class Attribute(object):
    IGNORE_CASE = True

    def __init__(self, val=None):
        self.val = val

    def get_data(self, val, line, header_to_index):
        if self.IGNORE_CASE:
            val = str(val).upper()
        if val in header_to_index:
            if header_to_index[val] in line or (
                        isinstance(header_to_index[val], int) and header_to_index[val] < len(line)):
                return line[header_to_index[val]]
            else:  # account for incomplete json data entries
                return ''
        try:  # assume this is an index
            return line[int(val)]
        except ValueError:
            raise AttributeError(
                'Column name or index not present in file: "{}" not in {}'.format(val, header_to_index.keys()))

    def get(self, line, header_to_index):
        if self.val:
            return self.get_data(self.val, line, header_to_index)
        return ''


class Name(Attribute):
    def __init__(self, name=None, fname=None, mname=None, lname=None, sname=None, fmt='L, F M.',
                 strip_lname_suffix=None, strip_lname_suffix_attached=None):
        super().__init__()
        self.strip_lname_suffix_attached = strip_lname_suffix_attached
        self.strip_lname_suffix = strip_lname_suffix
        self.fname = fname
        self.mname = mname
        self.lname = lname
        self.sname = sname
        self.name = name
        self.fmt = fmt + 'X'  # add this X as final fencepost to absorb anything remaining
        self.format_codes = ['L', 'M', 'm', 'F', 'f', 'S', 's', 'X']

    def _update_index_and_value(self, idx):
        idx += 1
        if len(self.fmt) <= idx:
            value = None
        elif self.fmt[idx] in self.format_codes:
            value = self.fmt[idx]
            idx += 1
        else:
            value = None
        return idx, value

    def _get_next_format_token(self, idx):
        while len(self.fmt) > idx:
            if self.fmt[idx] in self.format_codes[:-1]:  # ignore final X
                return self.fmt[idx]
            idx += 1
        return None

    def get(self, line, header_to_index):
        fname, mname, lname, sname = '', '', '', ''
        if self.name and self.fmt:
            name = self.get_data(self.name, line, header_to_index)
            curr = []
            idx = -1  # gets incremented in first step
            idx, value = self._update_index_and_value(idx)
            for letter in name:
                if len(self.fmt) <= idx or letter != self.fmt[idx]:
                    curr.append(letter)
                else:  # found end of current section
                    if value:
                        if value in 'L':
                            lname += ''.join(curr)
                        elif value in 'Mm':
                            mname += ''.join(curr)
                        elif value in 'Ff':
                            fname += ''.join(curr)
                        elif value in 'Ss':
                            fname += ''.join(curr)
                    curr = []
                    idx, value = self._update_index_and_value(idx)
            if value:
                # if value is lower-cased, find next non-lowercased value
                while value in 'fms':
                    val = self._get_next_format_token(idx)
                    if val:
                        value = val
                    else:  # no next uppercase value, so treat final as uppercase
                        value = value.upper()
                if value == 'L':
                    lname += ''.join(curr)
                elif value == 'M':
                    mname += ''.join(curr)
                elif value == 'F':
                    fname += ''.join(curr)
                elif value == 'S':
                    fname += ''.join(curr)

        if self.fname:
            fname = self.get_data(self.fname, line, header_to_index)
        if self.mname:
            mname = self.get_data(self.mname, line, header_to_index)
        if self.lname:
            lname = self.get_data(self.lname, line, header_to_index)
            # strip last name suffix?
            last_names = lname.split()
            if len(last_names) > 0 and last_names[-1].upper() in self.strip_lname_suffix:
                lname = ' '.join(last_names[:-1])
            elif self.strip_lname_suffix_attached:
                for suf in self.strip_lname_suffix_attached:
                    cand = last_names[-1].upper().rstrip(suf)
                    if cand != last_names[-1]:
                        lname = ' '.join(last_names[:-1] + [cand])
                        break

        if self.sname:
            sname = self.get_data(self.sname, line, header_to_index)
        return lname, fname, mname[0] if len(mname) > 0 else '', sname


class SSN(Attribute):
    def __init__(self, ssn):
        super().__init__()
        self.ssn = ssn

    def get(self, line, header_to_index):
        ssn = ''
        if self.ssn:
            ssn = self.get_data(self.ssn, line, header_to_index)
            if hasattr(ssn, 'isdigit'):  # this might already be a number
                ssn = ''.join(c for c in ssn if c.isdigit())
            else:
                ssn = str(ssn)
        return ssn


class BirthDate(Attribute):
    def __init__(self, date=None, year=None, month=None, day=None, fmt=None):
        super().__init__()
        self.date = date
        self.year = year
        self.month = month
        self.day = day
        self.fmt = fmt

    def get(self, line, header_to_index):
        year, month, day = '', '', ''
        if self.date:
            date = self.get_data(self.date, line, header_to_index)
            if isinstance(date, (dt_date, datetime)):  # loading process sometimes creates python datetime
                dt = date
            elif self.fmt:
                dt = datetime.strptime(date, self.fmt)
            elif DATEUTIL_IMPORT:
                dt = dparser.parse(date, default=datetime.max)
                if dt == datetime.max:
                    logging.warning('dateutil was unable to parse birthdate: "{}"'.format(date))
                dt = None
            else:
                raise ValueError(
                    'Unable to parse birthdate. Please install dateutil package or provide a datetime format.')
            if dt:
                year = dt.year
                month = dt.month
                day = dt.day
        if self.year:
            year = self.get_data(self.year, line, header_to_index)
        if self.month:
            month = self.get_data(self.month, line, header_to_index)
        if self.day:
            day = self.get_data(self.day, line, header_to_index)
        return str(year), str(month), str(day)


class Sex(Attribute):
    def __init__(self, sex=None, fmt=None):
        """Specify column with sex and optional format information

        **Format**
            - Specify "MALE,FEMALE", so if "MALE" is 1 and "FEMALE" is 2, specify "1,2"
            - By default, assumes with NDI format of "1,2" or "M,F"
        """
        super().__init__()
        self.sex = sex
        self.fmt = '1M', '2F'
        if fmt:
            self.fmt = fmt.split(',')
            if len(self.fmt) != 2:
                raise ValueError('Unrecognized format for sex: "{}", try "0,1" or "F,M"'.format(fmt))

    def get(self, line, header_to_index):
        sex = ''
        if self.sex:
            sex = str(self.get_data(self.sex, line, header_to_index)).upper()
            if sex in self.fmt[0]:
                sex = 'M'
            elif sex in self.fmt[1]:
                sex = 'F'
            else:
                sex = ''
        return sex


class State(Attribute):
    def __init__(self, state, same_state_for_all=None):
        super().__init__()
        self.state = state
        self.same_state_for_all = same_state_for_all

    def get(self, line, header_to_index):
        if self.same_state_for_all:
            state = self.same_state_for_all.upper()
        elif not self.state:
            return ''
        else:
            state = str(self.get_data(self.state, line, header_to_index)).upper()

        if not state.strip():
            return ''
        elif state in STATES_TO_CODES:
            return STATES_TO_CODES[state]
        else:
            return STATES_TO_CODES['REMAINDER OF WORLD']


class AttributeMapping(Attribute):
    def __init__(self, attr, default_mapping, mapping=None):
        super(AttributeMapping, self).__init__()
        self.attr = attr
        default_mapping = default_mapping
        if mapping:
            self.mapping = {x: y for x, y in zip(mapping, sorted(set(default_mapping.values())))}
        else:
            self.mapping = default_mapping

    def get(self, line, header_to_index):
        if not self.attr:
            return ''
        attr = str(self.get_data(self.attr, line, header_to_index))
        if attr in self.mapping:
            return self.mapping[attr]
        else:
            return ''


class DeathAge(Attribute):
    def __init__(self, age, units_for_all):
        super(DeathAge, self).__init__()
        self.age = age
        self.units_for_all = units_for_all

    def get(self, line, header_to_index):
        if not self.age:
            return '', None
        age = str(self.get_data(self.age, line, header_to_index))
        if self.units_for_all:
            return age, self.units_for_all
        else:
            return age, None
