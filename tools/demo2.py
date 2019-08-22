import os, pickle
from glob import glob

from document import Document, Paragraph, Table
from utils import *

# declare global variable for the demo
data_dir = "/u/nieyifan/projects/CRM/data2/"

ressource_lst = ["Distribution_de_produits"]

consitituion_lst = ["Reglement_PICKLE", "Loi_PICKLE", "Guide_MSWORD", "Directive_MSWORD"]
langauge_lst = ["anglais", "français"]


def read_consitituion(ressource, consitituion, langauge):
    def keep_file(filename):
        return ressource in filename and consitituion in filename and langauge in filename

    print("Reading file in pickle format")
    file_lst = [y for x in os.walk(data_dir) for y in glob(os.path.join(x[0], '*pkl'))]
    file_lst = [filename for filename in file_lst if keep_file(filename)]
    import ipdb
    ipdb.set_trace()
    for filename in file_lst:
        print("print the content of %s" % filename)
        read_pkl(filename)

    print("Reading file in docx format")
    file_lst = [y for x in os.walk(data_dir) for y in glob(os.path.join(x[0], '*docx'))]
    file_lst = [filename for filename in file_lst if keep_file(filename)]
    for filename in file_lst:
        print("print the content of %s" % filename)
        read_docx(filename)


def read_pkl(filename):

    # opening the pickle
    with open(filename, 'rb') as fp:
        chapter_lst = pickle.load(fp)

    # File written in pkl format are list of chapters
    for chap_id, chapter in enumerate(chapter_lst):
        # each chapter have a header and section list that
        # can be empty
        header = chapter.header
        section_lst = chapter.section_lst

        # print header id (e.g. CHAPTER I) and the title (e.g. SPECIAL PROVISION)
        print(header.tid)
        print(header.text)

        for section in section_lst:
            print("Begin of Section", "\n")

            # each section is composed of subsection_lst
            for subsection in section.subsection_lst:

                # a sub section can be a list of paragraph
                if isinstance(subsection, list):
                    for paragraph in subsection:
                        print(paragraph.tid, paragraph.text)

                # or a single paragraph
                else:
                    print(subsection.tid, subsection.text)

            # Also each section has historical_note or simply footnotes
            # those refer to other part in the law or even to other law
            for historical_note in section.historical_note_lst:
                print(historical_note.text)

            print("End of Section", "\n")


def read_docx(filename):
    doc = Document(filename=filename, meta={})


    # this function will print the document
    doc.print()

    # a docx file is a lst of blocks (Paragraph or Table)
    for idx, block in enumerate(doc.story):
        if isinstance(block, Paragraph):
            # a paragraph contains a list of Run
            for run in block.runs:
                # Run contains .text attribute
                text = run.text

                #and a Font class (attrs: blod, italic, etc ...)
                is_bold = run.font.bold

        elif isinstance(block, Table):
            # Table contains a rows attrbute ( a list of lists)
            # iterating on each row in the table
            for row in block.rows:
                # iterating on each cell in the row
                for run in row:
                    # Run contains .text attribute
                    text = run.text

                    # and a Font class (attrs: blod, italic, etc ...)
                    is_bold = run.font.bold


# demo to read .pkl files
read_consitituion("Valeurs mobilières", "Loi", "anglais")

# demo to read .docx file
#read_consitituion("Valeurs mobilières", "Règlement", "anglais")
