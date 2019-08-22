import enum
from copy import deepcopy

class TextLabel(enum.Enum):
    Nothing = 0
    Paragraph = 1
    HistoricalNote = 2
    SubSection = 3
    Header = 4


class Text:

    def __init__(self, text: str, tid: str, label: TextLabel, order:int):
        self.text = text
        self.tid = tid
        self.label = label
        self.order = order
        self.roles = None


class Section:

    def __init__(self, subsection_lst: list, historical_note_lst: list):
        self.subsection_lst = subsection_lst
        self.historical_note_lst = historical_note_lst
        self.roles = None


class Chapter:
    def __init__(self, tid: str, header, section_lst: list):
        self.tid = tid
        self.header = header
        self.section_lst = section_lst
        self.roles = None


def flatten_list(nested_list):
    """Flatten an arbitrarily nested list, without recursion (to avoid
    stack overflows). Returns a new list, the original list is unchanged.
    >> list(flatten_list([1, 2, 3, [4], [], [[[[[[[[[5]]]]]]]]]]))
    [1, 2, 3, 4, 5]
    >> list(flatten_list([[1, 2], 3]))
    [1, 2, 3]
    """
    nested_list = deepcopy(nested_list)

    while nested_list:
        sublist = nested_list.pop(0)

        if isinstance(sublist, list):
            nested_list = sublist + nested_list
        else:
            yield sublist