import os, re, pickle
from glob import glob

from tqdm import tqdm
from bs4 import BeautifulSoup

from utils import *


def split_cp():
    input_dir = "Z:/data_by_task/arrangement/corpus"
    output_dir = "//reso.local/Autorite/Public Autorite/Partages Surintendances/SU_March_Valeurs/DP_Enc_Dérivés" \
                 "/Lab Fintech/ressource/Direction de la conformité - émetteurs et initiés/CP_2012_2019"
    data, counter, sz = [], 0, 0

    for filename in os.listdir(input_dir):
        for line in tqdm(open(os.path.join(input_dir, filename), encoding="utf-8")):
            data.append(line)
            sz += 1
            if sz == 3e6:
                open(os.path.join(output_dir, "%s.txt" % counter), "w", encoding="utf-8").write("".join(data))
                data, sz = [], 0
                counter += 1

    open(os.path.join(output_dir, "%s.txt" % counter), "w", encoding="utf-8").write("".join(data))


def parse_law():
    wrk_path = "O:/SU_March_Valeurs/Centre d'Excellence en Dérivés/Lab Fintech/Réglementation/Atelier CRM/"
    file_lst = [y for x in os.walk(wrk_path) for y in glob(os.path.join(x[0], '*html'))]

    for filename in file_lst:
        filename = r'%s' % filename
        print(filename)

        # prepare output_file path
        head, tail = os.path.split(filename)
        head = head.replace("\\français", "_PICKLE\\français").replace("\\anglais", "_PICKLE\\anglais")

        if not os.path.exists(head):
            os.makedirs(head)

        tail = tail.replace(".html", ".pkl")
        output_file = os.path.join(head, tail)
        if os.path.exists(output_file):
            continue

        law = []
        try:
            open(output_file, "wb")
            f = open(filename, encoding="utf-8").read()
        except:
            print("Error with filename name %s" % filename)
            continue
        soup = BeautifulSoup(f, "html.parser")
        for title in soup.find_all('div', {"id": re.compile(r'ga:l_.*')}):
            tid = title.attrs["id"]
            header = parse_header(title)
            section_lst = [parse_section(section) for section in title.find_all('div', {"class": "section"})]
            chapter = Chapter(tid, header, section_lst)
            law.append(chapter)


        with open(output_file, 'wb') as fp:
            pickle.dump(law, fp)


def parse_header(title):
    tid, text, int_ord = "", "", 0
    for header in title.find_all('div', {"class": "Heading"}):
        label = [lbl for lbl in header.find_all('div', {"class": re.compile(r'Label-group.*')})]
        if label:
            tid = label[0].text
            int_ord = int(label[0].attrs["integrity:order"])

        label = [lbl for lbl in header.find_all('div', {"class": re.compile(r'TitleText-group.*')})]
        if label: text = label[0].text

    header = Text(text, tid, TextLabel.Header, int_ord)
    return header


def parse_section(section):
    subsection_lst = []
    historical_note_lst = []

    # parse SubSection
    for subsection in section.find_all('div', {"class": "Subsection"}):
        paragraph_lst = parse_paragraph(subsection)
        subsection_lst.append(paragraph_lst)

    # parse HistoricalNote
    hsnote = section.select_one("div[class=HistoricalNote]")
    if hsnote:
        lst = [parsepan(span, str(tid), TextLabel.HistoricalNote) for tid, span in enumerate(hsnote.find_all('span'))]
        historical_note_lst = [item for item in lst if item]

    return Section(subsection_lst, historical_note_lst)


def parse_paragraph(subsection):
    paragraph_lst = []

    span = subsection.select_one("span[class=texte-courant]")
    paragraph_lst.append(parsepan(span, "0", TextLabel.SubSection))

    for paragraph in subsection.find_all('div', {"class": "Paragraph"}):
        # print(paragraph)
        tid = [lbl for lbl in paragraph.find_all('span', {"class": re.compile(r'Label\-.*')})][0]
        tid = tid.text.strip()[:-1]
        span = paragraph.select_one("span[class=texte-courant]")
        paragraph_lst.append(parsepan(span, tid, TextLabel.Paragraph))

    paragraph_lst = [item for item in paragraph_lst if item]
    return paragraph_lst


def parsepan(span, tid, label):
    if not span: return None
    if "integrity:order" not in span.attrs: span = span.span
    if not span or "integrity:order" not in span.attrs: return None
    int_ord = int(span.attrs["integrity:order"])
    item = Text(span.text, tid, label, int_ord)

    return item

parse_law()