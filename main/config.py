import os
from dotenv import load_dotenv
load_dotenv()

MONTH = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

MONTH_DICT = {"F": "01", "G": "02", "H": "03", "J": "04", "K": "05", "M": "06", "N": "07", "Q": "08", "U": "09",
              "V": "10", "X": "11", "Z": "12"}

EXCHANGES = {
    "ES": "GLOBEX",
    "MNQ": "GLOBEX",
    "CL": "NYMEX",
    "GC": "NYMEX",
    "ZC": "ECBOT",
    "ZS": "ECBOT",
    "EUR": "GLOBEX",
    "GBP": "GLOBEX",
    "N225M": "OSE.JPN",
    "K200": "KSE",
}