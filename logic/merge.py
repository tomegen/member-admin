from collections import namedtuple

from model import schema
from model.club_file import cell_key
from model.columns import normalize
from store.sheet import COLUMNS_BY_FIELD, cell_value

COMPARED = [column.field for column in schema.MEMBER_COLUMNS if column.field != "nr"]
ATTRIBUTES = {"phone": "phone_number"}   # field -> attribute of Member, where they differ
NEW, CHANGED, SAME, SIMILAR = "neu", "geändert", "unverändert", "ähnlich"

# heading is shown; current (in the file) and incoming are cell keys
Difference = namedtuple("Difference", "field heading current incoming")


def key(field, value):
    return cell_key(cell_value(COLUMNS_BY_FIELD[field], value))


def member_values(member):
    return {field: getattr(member, ATTRIBUTES.get(field, field)) for field in COMPARED}


def name_key(values):
    return normalize(values.get("last_name") or ""), normalize(values.get("first_name") or "")


# one person of a list compared with the member file: kind NEW, CHANGED, SAME or SIMILAR (same name, but not sure
# it is the same person: shown, not taken by default). take = add it (NEW, SIMILAR); chosen = fields to take over
class MergeItem:

    def __init__(self, kind, values, member=None, differences=(), note=""):
        self.kind = kind
        self.values = values
        self.member = member
        self.differences = list(differences)
        self.note = note
        self.take = kind == NEW
        self.chosen = {difference.field for difference in self.differences if not difference.current}

    @property
    def nr(self):
        return None if self.member is None else self.member.nr

    def name(self):
        return ((self.values.get("first_name") or "") + " " + (self.values.get("last_name") or "")).strip()


# the members of the file by nr, by name and birthday and by name; members without nr cannot be matched
class FileIndex:

    def __init__(self, members):
        self.members = [member for member in members if member.nr is not None]
        self.by_nr = {member.nr: member for member in self.members}
        self.by_name = {}
        for member in self.members:
            self.by_name.setdefault(name_key(member_values(member)), []).append(member)

    # (member or None, note, similar?): by nr if the name fits too (another program may count differently),
    # else by name and birthday; without birthday by a unique name
    def find(self, values, by_number=False):
        name = name_key(values)
        member = self.by_nr.get(values.get("nr")) if by_number else None
        if member is not None and name_key(member_values(member)) == name:
            return member, "", False
        same_name = self.by_name.get(name, [])
        birthday = key("birthday", values.get("birthday"))
        if birthday:
            exact = [member for member in same_name if key("birthday", member.birthday) == birthday]
            if len(exact) == 1:
                return exact[0], "", False
            if same_name:
                return None, "Gleicher Name wie Nr " + ", ".join(str(m.nr) for m in same_name) + \
                    ", aber anderer Geburtstag – bitte prüfen.", True
            return None, "", False
        if len(same_name) == 1:
            return same_name[0], "nur über den Namen zugeordnet (kein Geburtstag in der Liste)", False
        if same_name:
            return None, "Mehrere Mitglieder mit diesem Namen – bitte prüfen.", True
        return None, "", False


# compares the incoming people with the file: ([MergeItem], [Member only in the file]). incoming are
# (values, fields): the fields that the list really has (estimated or default values are not compared).
# An empty value of the list never empties a value of the file
def compare(incoming, members, by_number=False):
    index = FileIndex(members)
    items, used = [], set()
    for values, fields in incoming:
        member, note, similar = index.find(values, by_number)
        if member is not None and member.nr in used:
            member, note, similar = None, "Diese Person steht mehrmals in der Liste – bitte prüfen.", True
        if member is None:
            items.append(MergeItem(SIMILAR if similar else NEW, values, note=note))
            continue
        used.add(member.nr)
        current = member_values(member)
        differences = []
        for field in COMPARED:
            if field not in fields:
                continue
            incoming_key, current_key = key(field, values.get(field)), key(field, current[field])
            if incoming_key and incoming_key != current_key:
                differences.append(Difference(field, COLUMNS_BY_FIELD[field].heading, current_key, incoming_key))
        items.append(MergeItem(CHANGED if differences else SAME, values, member, differences, note))
    only_in_file = [member for member in index.members if member.nr not in used]
    return items, only_in_file
