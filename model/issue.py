# a problem found in the member list; row is the row number as shown in excel
class Issue:

    def __init__(self, row, name, active, message):
        self.row = row
        self.name = name
        self.active = active
        self.message = message
