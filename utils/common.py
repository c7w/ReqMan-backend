import re

def extract_sr_pattern(title: str):
    res = re.match(r"\[SR.\d{3}.\d{3}(?=(.[I/F/B])?])", title.strip())
    if res is None:
        return None
    return res.group(0)[1:]
