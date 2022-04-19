import re


def extract_sr_pattern(title: str, proj):
    res = re.search(proj.remote_sr_pattern_extract, title.strip())
    if res is None:
        return None
    return res.group(0)


def extract_issue_pattern(title: str, proj):
    res = re.search(proj.remote_issue_iid_extract, title.strip())
    if res is None:
        return None
    return res.group(0)


def extract_local_sr_title(title: str, proj):
    res = re.search(proj.local_sr_title_pattern_extract, title.strip())
    if res is None:
        return None
    return res.group(0)
