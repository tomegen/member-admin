from collections import Counter

from importer.first_names import FEMALE_NAMES, MALE_NAMES
from model import schema

UMLAUTS = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "é": "e", "è": "e"})


# gender from the first part of the first name ("Hans-Peter" -> "hans"); "" if the name is not in the list
def gender_of_first_name(first_name):
    words = first_name.replace("-", " ").split()
    if not words:
        return ""
    name = words[0].casefold().translate(UMLAUTS)
    if name in MALE_NAMES:
        return "männlich"
    if name in FEMALE_NAMES:
        return "weiblich"
    return ""


# rows without gender get one: from the first name, else the most frequent gender of the list (the known ones,
# else the ones from first names). They are marked as estimated (row.estimated) and have to be confirmed
def estimate_genders(rows):
    missing = [row for row in rows if not row.values.get("gender")]
    by_name = {id(row): gender_of_first_name(row.values.get("first_name", "")) for row in missing}
    known = Counter(row.values["gender"] for row in rows if row.values.get("gender"))
    if not known:
        known = Counter(gender for gender in by_name.values() if gender)
    majority = known.most_common(1)[0][0] if known else ""
    for row in missing:
        gender = by_name[id(row)] or majority
        if gender in schema.GENDERS:
            row.values["gender"] = gender
            row.estimated.add("gender")
