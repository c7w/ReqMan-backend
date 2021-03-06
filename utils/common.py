import re


def extract_sr_pattern(title: str, proj, given=None):
    res = re.search(given if given else proj.remote_sr_pattern_extract, title.strip())
    if res is None:
        return None
    return res.group(0)


def extract_issue_pattern(title: str, proj, given=None):
    res = re.search(given if given else proj.remote_issue_iid_extract, title.strip())
    if res is None:
        return None
    return res.group(0)
