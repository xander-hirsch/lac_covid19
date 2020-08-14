import re

DATE = re.compile('[A-Z][a-z]+ \d{2}, 20\d{2}')

NEW_DEATHS_CASES = re.compile(
    '([\d,]+)\s+new\s+deaths\s+and\s+([\d,]+)\s+new\s+cases')