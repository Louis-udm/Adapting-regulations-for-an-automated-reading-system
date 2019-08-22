import re, zipfile, copy , xml.etree.ElementTree
from copy import deepcopy
from collections import Counter

import xlrd
from tabulate import tabulate

import utils



WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'
TABLE = WORD_NAMESPACE + 'tbl'
ROW = WORD_NAMESPACE + 'tr'
CELL = WORD_NAMESPACE + 'tc'
TAB = WORD_NAMESPACE + 'tab'
SPACING = WORD_NAMESPACE + 'spacing'

PARAFONT = WORD_NAMESPACE + 'pPr'
BOLD = WORD_NAMESPACE + 'b'
ITALIC = WORD_NAMESPACE + 'i'
UNDERLINE = WORD_NAMESPACE + 'u'
PSTYLE = WORD_NAMESPACE + 'pStyle'
BREAK = WORD_NAMESPACE + 'br'


RUNFONT = WORD_NAMESPACE + 'rPr'
SPIN = WORD_NAMESPACE + 'position' # stands for "superiors" and "inferiors"
SIZE = WORD_NAMESPACE + 'sz'


class Document:
    def __init__(self, filename=None, file_contents=None, meta=None, filetype="word"):
        """
        tree is the xml extracte from word/document.xml
        meta is a dico that contains meta data about the document
        """
        if not meta: meta={}

        if filename and filename.split(".")[-1].startswith("xls"):
            filetype = "excel"

        if filetype not in ["word", "excel"]:
            raise ValueError("Only support docx and excel")

        self._story, self._meta = globals()["_read_" + filetype](filename, file_contents, meta)

    def merge_blocks(self, to_merge:dict):
        rm = set()
        inv_map = {v: k for k, v in to_merge.items()}
        for prv, nxt in to_merge.items():
            if isinstance(self._story[prv], Table) or isinstance(self._story[nxt], Table):
                raise ValueError("One or both blocks is Table... Can't merge")

            while prv in rm:
                prv = inv_map[prv]

            self._story[prv].runs = self._story[prv].runs + self._story[nxt].runs
            self._story[prv].merge_runs()
            rm.add(nxt)

        self._story = [block for idx, block in enumerate(self._story) if idx not in rm]

    def repair_tables(self):
        self._story = _repair_tables(self._story)

    def set_indexes(self):
        for idx, block in enumerate(self._story):
            block.idx = idx

    def print(self):
        for block in self._story:
            print(block.print())

    @property
    def story(self):
        return self._story

    @property
    def meta(self):
        return self._meta

    def set_words(self, tc, to_lower=False):
        [block.set_words(tc, to_lower) for block in self._story]


class Table:
    def __init__(self, elem, parent_map):
        if elem is None:
            self._rows = None
        else:
            self._rows = [[Paragraph(cell, parent_map).to_run() for cell in row.iter(CELL)] for row in elem.iter(ROW)]

        self.words = []
        self._idx = -1

    def to_html(self, index=-1):
        rows = ["<tr> " + (" ".join(["<td> %s </td>" % cell.to_html() for cell in row]))+"</tr>" for row in self._rows]
        return "<a id=%s></a><table border='1'>\n" % index + ("\n".join(rows)) + "\n</table>"

    def print(self):
        return tabulate([[run.text for run in row] for row in self.rows], tablefmt="grid")

    def contains(self, pattern, exact_match=False, ignore_case=True):
        if ignore_case:
            pattern = pattern.lower()

        for cell in utils.flatten_list(self._rows):
            t = cell.text if not ignore_case else cell.text.lower()
            if exact_match and t == pattern:
                return True
            elif not exact_match and pattern in t:
                return True

        return False

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, table):
        self._rows = table

    def set_words(self, tc, to_lower=False):
        [[run.set_words(tc, to_lower) for run in row] for row in self._rows]
        self.words = [[run.words for run in row] for row in self._rows]

    @property
    def idx(self):
        return self._idx

    @idx.setter
    def idx(self, value):
        self._idx = value


class Paragraph:
    def __init__(self, elem, parent_map):
        self.is_enum = _par_is_enum(copy.deepcopy(elem))
        self._runs = [Run(el, parent_map) for el in elem.iter() if el.tag in [TEXT, TAB, SPACING]]

        if not len(self._runs):
            self._runs = [Run(None, None)]

        # remove no necessary spaces
        rm_id = [i+1 for i in range(len(self._runs) - 1)
                 if re.match(r'^.+\s$', self._runs[i].text) and self._runs[i + 1].text == " "]
        self._runs = [self._runs[i] for i in range(len(self._runs)) if i not in rm_id]

        # merge sucessive runs with the same font
        self.merge_runs()
        self.words = []
        self._idx = -1

    def merge_runs(self):
        lst = []
        last = self._runs[0]

        for i in range(1, len(self._runs)):
            cur = self._runs[i]
            if cur.font == last.font:
                last.text += cur.text
            else:
                lst.append(last)
                last = cur

        lst.append(last)

        self._runs = lst

    def to_run(self):
        if not len(self._runs):
            return
        # TODO preseve table runs
        # if len(self._runs) > 1:
        #     for r in self._runs:
        #         print(r.text)
        run = self._runs[0]
        run.text = self.text
        return run

    def contains(self, pattern, exact_match=False, ignore_case=True):
        if ignore_case:
            pattern = pattern.lower()

        t = self.text if not ignore_case else self.text.lower()
        if exact_match and t == pattern:
            return True
        elif not exact_match and pattern in t:
            return True

        return False

    def to_html(self, index=-1):
        return "<a id=%s></a><p>"%index + (' '.join([run.to_html() for run in self._runs]).strip()) + "</p>"

    def print(self):
        return self.text

    @property
    def text(self):
        return ''.join([run.text for run in self._runs]).strip()

    @property
    def runs(self):
        return self._runs

    @runs.setter
    def runs(self, value):
        self._runs = value

    def set_words(self, tc, to_lower=False):
        for run in self._runs:
            run.set_words(tc, to_lower)
            self.words += run.words

    @property
    def idx(self):
        return self._idx

    @idx.setter
    def idx(self, value):
        self._idx = value


class Run:
    def __init__(self, el, parent_map):
        self.font = Font()
        self.text = ""
        self.words = []

        if el is not None:
            if el.tag == TEXT and el.text:
                self.text = el.text
                self.font.set_font(el, parent_map)
                self.font.set_spif(parent_map[el])
            elif el.tag == TAB:
                self.text = "\t"
            elif el.tag == SPACING:
                self.text = " "
            elif el.tag == BREAK:
                self.text = "\n"

    def to_html(self):
        return self.font.to_html(self.text)

    @property
    def text(self):
        return self._text.replace("  ", " ")

    @text.setter
    def text(self, value):
        self._text = value

    def set_words(self, tc, to_lower=False):
        self.words = [m.group(0).translate(tc.table) for m in re.finditer(r'\b\w+\b', self.text)]
        if to_lower:
            self.words = [w.lower() for w in self.words]


class Font:
    def __init__(self):
        self._bold = False
        self._italic = False
        self._underline = False
        self._sup = False
        self._sub = False
        self._size = 0

    def set_font(self, elem, parent_map):
        parent = parent_map[elem]
        font_map = {"_bold": BOLD, "_italic": ITALIC, "_underline": UNDERLINE, "_size": SIZE}

        for key, value in font_map.items():
            setattr(self, key, bool(len([prp for prp in parent.iter(value)])))
            if not getattr(self, key):
                grand_parent = parent_map[parent]
                for prp in grand_parent.iter(value):
                    if key == "_size":
                        self._size = int(prp.attrib[WORD_NAMESPACE + "val"])
                    elif WORD_NAMESPACE + "val" in prp.attrib and prp.attrib[WORD_NAMESPACE + "val"] == '0':
                        setattr(self, key, True)
                        break

    def set_spif(self, parent):
        for prp in parent.iter():
            if prp.tag != RUNFONT: continue
            for p in prp.iter():
                if p.tag == SPIN:
                    pos = int(p.attrib[WORD_NAMESPACE + "val"])
                    setattr(self, "_sup", True) if pos > 0 else setattr(self, "_sub", True)
                elif p.tag == SIZE:
                    self._size = int(p.attrib[WORD_NAMESPACE + "val"])

    def to_html(self, span):
        for att, tag in [("bold", "b"), ("italic", "i"), ("underline", "u"),
                         ("sup", "sup"), ("sub", "sub")]:
            if getattr(self, att):
                span = "<%s>%s</%s>" % (tag, span, tag)

        if self.size:
            span = "<font size=\"%s\">%s</font>" % (self.size, span)

        return span

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def bold(self):
        return self._bold

    @property
    def italic(self):
        return self._italic

    @property
    def underline(self):
        return self._underline

    @property
    def sup(self):
        return self._sup

    @property
    def sub(self):
        return self._sub

    @property
    def size(self):
        return self._size


#################################
### Mehods to read docx/xlsx ####
#################################
def _read_word(filename, file_contents, meta):
    if filename:
        with zipfile.ZipFile(filename) as docx:
            tree = xml.etree.ElementTree.XML(docx.read('word/document.xml'))
    else:
        tree = file_contents

    parent_map = {c: p for p in tree.iter() for c in p}
    story = []

    for elem in tree.iter():
        if elem.tag == PARA and parent_map[elem].tag not in [CELL]:
            story.append(Paragraph(elem, parent_map))
        elif elem.tag == TABLE:
            story.append(Table(elem, parent_map))

    story = _adjust_doc(story)

    return story, meta


def _read_excel(filename, file_contents, meta):
    if filename:
        workbook = xlrd.open_workbook(filename, logfile=None)
    else:
        workbook = xlrd.open_workbook(file_contents=file_contents, logfile=None)
    story = []

    for worksheet in workbook.sheets():
        rows = []

        for row in range(0, worksheet.nrows):
            cells = []
            for col in range(0, worksheet.ncols):
                run = Run(None, None)
                run.text = worksheet.cell_value(row, col)
                if isinstance(run.text, float) and run.text.is_integer(): run.text = int(run.text)
                cells.append(run)
            rows.append(cells)

        table = Table(None, None)
        table.rows = rows
        story.append(table)

    meta["sheet_names"] = dict([(idx, sn) for idx, sn in enumerate(workbook.sheet_names())])
    return story, meta


######################################
##### methods used to pretreat docx ##
######################################
def _adjust_doc(story):
    remove_idx = []
    tab_run = Run(None, None)
    tab_run.text = "\t"

    for i in range(len(story) - 1):
        if isinstance(story[i], Paragraph) and isinstance(story[i+1], Table):
            text, table = story[i].text, story[i + 1].rows
            counter = 0
            for cell in utils.flatten_list(table):
                if cell.text in text:
                    counter += 1
                if counter == 3:
                    break

            if counter == 3:
                remove_idx.append(i)

        elif isinstance(story[i], Paragraph) and isinstance(story[i+1], Paragraph):
            text1, text2 = story[i].text, story[i+1].text
            if text1 == text2 and text1.strip():
                remove_idx.append(i)

            elif text2.strip() and re.match("^[\d\s]*$", text2) and "\t" in text2:
                story[i].runs = story[i].runs + [tab_run] + story[i + 1].runs
                remove_idx.append(i + 1)
                i += 1
            elif text2 in text1 and text2.count(" ") > 4:
                remove_idx.append(i + 1)
                i += 1

        if isinstance(story[i], Table):
            table = story[i].rows
            if all([not bool(cell.text.strip()) for cell in utils.flatten_list(table)]):
                remove_idx.append(i)

    return [block for i, block in enumerate(story) if i not in remove_idx]


def _repair_tables(story):
    tab_count = []

    for i, block in enumerate(story):

        if isinstance(block, Table):
            tab_count.append((i, -2))
        if isinstance(block, Paragraph):
            text = block.text
            if text == "":
                tab_count.append((i, -1))
            else:
                tab_count.append((i, text.count("\t")))

    n_idx = -1
    new_tables = {}

    for idx, t_count in tab_count:
        if n_idx > idx:
            continue

        if t_count > 0:
            n_idx, table = _find_table(story, idx, tab_count)
            if table is not None:
                new_tables[idx] = {"end": n_idx, "table": table}

    new_story = []
    end = -1
    for i in range(len(story)):
        if i < end:
            continue
        if i not in new_tables:
            new_story.append(story[i])
        else:
            end, table = new_tables[i]["end"], new_tables[i]["table"]
            new_story.append(table)

    return new_story


def _find_table(story, idx, tab_count):
    seq = []
    last_zero_idx = -1
    e_index = idx+1

    for i in range(idx, len(tab_count)):
        if tab_count[i][1] == -1:
            continue

        if tab_count[i][1] == 0:
            if i - last_zero_idx == 1:
                e_index = i
                break

            last_zero_idx = i

        if tab_count[i][1] == -2:
            e_index = i
            break

        seq.append(tab_count[i])

    if len(seq) < 3:
        return e_index, None

    col_num = Counter([item[1] for item in seq]).most_common()[0][0]
    rows = []

    for idx, tc in seq:
        run = story[idx].to_run()
        if tc != col_num:
            rows.append([run])
        else:
            parts = story[idx].text.split("\t")
            line = []
            for s in parts:
                c_run = deepcopy(run)
                c_run.text = s
                line.append(c_run)
            rows.append(line)

    table = Table(None, None)
    table.rows = rows
    return e_index, table


def _par_is_enum(elem):
    for e in elem.iter(PSTYLE):
        return True if e.attrib[WORD_NAMESPACE + "val"] == "ListParagraph" else False
    return False

