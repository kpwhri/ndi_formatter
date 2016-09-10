STATES_TO_CODES = {
    "ALABAMA": "01", "AL": "01", "01": "01", 1: "01",
    "NEW JERSEY": "31", "NJ": "31", "31": "31", 31: "31",
    "ALASKA": "02", "AK": "02", "02": "02", 2: "02",
    "NEW MEXICO": "32", "NM": "32", "32": "32", 32: "32",
    "ARIZONA": "03", "AZ": "03", "03": "03", 3: "03",
    "NEW YORK": "33", "NY": "33", "33": "33", 33: "33",
    "ARKANSAS": "04", "AR": "04", "04": "04", 4: "04",
    "NORTH CAROLINA": "34", "NC": "34", "34": "34", 34: "34",
    "CALIFORNIA": "05", "CA": "05", "05": "05", 5: "05",
    "NORTH DAKOTA": "35", "ND": "35", "35": "35", 35: "35",
    "COLORADO": "06", "CO": "06", "06": "06", 6: "06",
    "OHIO": "36", "OH": "36", "36": "36", 36: "36",
    "CONNECTICUT": "07", "CT": "07", "07": "07", 7: "07",
    "OKLAHOMA": "37", "OK": "37", "37": "37", 37: "37",
    "DELAWARE": "08", "DE": "08", "08": "08", 8: "08",
    "OREGON": "38", "OR": "38", "38": "38", 38: "38",
    "DISTRICT OF COLUMBIA": "09", "DC": "09", "09": "09", 9: "09",
    "PENNSYLVANIA": "39", "PA": "39", "39": "39", 39: "39",
    "FLORIDA": "10", "FL": "10", "10": "10", 10: "10",
    "RHODE ISLAND": "40", "RI": "40", "40": "40", 40: "40",
    "GEORGIA": "11", "GA": "11", "11": "11", 11: "11",
    "SOUTH CAROLINA": "41", "SC": "41", "41": "41", 41: "41",
    "HAWAII": "12", "HI": "12", "12": "12", 12: "12",
    "SOUTH DAKOTA": "42", "SD": "42", "42": "42", 42: "42",
    "IDAHO": "13", "ID": "13", "13": "13", 13: "13",
    "TENNESSEE": "43", "TN": "43", "43": "43", 43: "43",
    "ILLINOIS": "14", "IL": "14", "14": "14", 14: "14",
    "TEXAS": "44", "TX": "44", "44": "44", 44: "44",
    "INDIANA": "15", "IN": "15", "15": "15", 15: "15",
    "UTAH": "45", "UT": "45", "45": "45", 45: "45",
    "IOWA": "16", "IA": "16", "16": "16", 16: "16",
    "VERMONT": "46", "VT": "46", "46": "46", 46: "46",
    "KANSAS": "17", "KS": "17", "17": "17", 17: "17",
    "VIRGINIA": "47", "VA": "47", "47": "47", 47: "47",
    "KENTUCKY": "18", "KY": "18", "18": "18", 18: "18",
    "WASHINGTON": "48", "WA": "48", "48": "48", 48: "48",
    "LOUISIANA": "19", "LA": "19", "19": "19", 19: "19",
    "WEST VIRGINIA": "49", "WV": "49", "49": "49", 49: "49",
    "MAINE": "20", "ME": "20", "20": "20", 20: "20",
    "WISCONSIN": "50", "WI": "50", "50": "50", 50: "50",
    "MARYLAND": "21", "MD": "21", "21": "21", 21: "21",
    "WYOMING": "51", "WY": "51", "51": "51", 51: "51",
    "MASSACHUSETTS": "22", "MA": "22", "22": "22", 22: "22",
    "PUERTO RICO": "52", "PR": "52", "52": "52", 52: "52",
    "MICHIGAN": "23", "MI": "23", "23": "23", 23: "23",
    "VIRGIN ISLANDS": "53", "VI": "53", "53": "53", 53: "53",
    "MINNESOTA": "24", "MN": "24", "24": "24", 24: "24",
    "GUAM": "54", "GU": "54", "54": "54", 54: "54",
    "MISSISSIPPI": "25", "MS": "25", "25": "25", 25: "25",
    "CANADA": "55", "CN": "55", "55": "55", 55: "55",
    "MISSOURI": "26", "MO": "26", "26": "26", 26: "26",
    "CUBA": "56", "CU": "56", "56": "56", 56: "56",
    "MONTANA": "27", "MT": "27", "27": "27", 27: "27",
    "MEXICO": "57", "MX": "57", "57": "57", 57: "57",
    "NEBRASKA": "28", "NE": "28", "28": "28", 28: "28",
    "REMAINDER OF WORLD": "59", "RW": "59", "59": "59", 59: "59",
    "NEVADA": "29", "NV": "29", "29": "29", 29: "29",
    "NEW HAMPSHIRE": "30", "NH": "30", "30": "30", 30: "30"
}

RACE_TO_CODES = {
    "1": "1", 1: "1", "WH": "1", "White": "1",
    "2": "2", 2: "2", "BL": "2", "Black": "2",
    "3": "3", 3: "3", "IN": "3", "Indian": "3",
    "4": "4", 4: "4", "CH": "4", "Chinese": "4",
    "5": "5", 5: "5", "FI": "5", "Filipino": "5",
    "6": "6", 6: "6", "JA": "6", "Japanese": "6",
    "7": "7", 7: "7", "HA": "7", "Hawaiian": "7",
    "Other Asian": "8",
    "8": "8", 8: "8", "OA": "8", "Pacific Islander": "8",
    "0": "0", 0: "0", "ON": "0", "Other nonwhite": "0"
}

MS_TO_CODES = {
    "1": "1", 1: "1", "S": "1", "Single": "1",
    "A": "1", "Annulled": "1",
    "P": "2", "Separated": "2",
    "C": "2", "Common-law marriage": "2",
    "2": "2", 2: "2", "M": "2", "Married": "2",
    "3": "3", 3: "3", "W": "3", "Widowed": "3",
    "4": "4", 4: "4", "D": "4", "Divorced": "4"
}
