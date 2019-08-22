# -*- coding: utf-8 -*-

# # # #
# train_scope_label.py
# @author Zhibin.LU
# @created 2019-08-21T23:35:17.757Z-04:00
# @last-modified 2019-08-22T15:08:23.610Z-04:00
# @website: https://louis-udm.github.io
# @description 
# Adapting-regulations-for-an-automated-reading-system
# in The Ninth Montreal Industrial Problem Solving Workshop
# # # #

#%%
import os, pickle
from glob import glob
from document import Document, Paragraph, Table
from utils import *

#%%
'''
Define the patterns of scope roles for matcher.
'''

import spacy
nlp = spacy.load("en_core_web_lg")
from spacy.matcher import Matcher
matcher = Matcher(nlp.vocab)

#%%
roles=['insurance representative',
    'representative in insurance of person',
    'group insurance representative',
    'damage insurance agent',
    'damage insurance broker',
    'claims adjuster',
    'financial planner',
    'firm','independent representative','independent partnership']

patterns = [
    [{"LEMMA": "insurance"}, {"LEMMA": "representative"}],
    [{"LEMMA": "representative"}, {"LEMMA": "in"}, {"LEMMA": "insurance"}, {"LEMMA": "of"}, {"LEMMA": "person"}],
    [{"LEMMA": "group"}, {"LEMMA": "insurance"}, {"LEMMA": "representative"}],
    [{"LEMMA": "damage"}, {"LEMMA": "insurance"}, {"LEMMA": "agent"}],
    [{"LEMMA": "damage"}, {"LEMMA": "insurance"}, {"LEMMA": "broker"}],
    [{"LEMMA": "claim"}, {"LEMMA": "adjuster"}],
    [{"LEMMA": "financial"}, {"LEMMA": "planner"}],
    [{"LEMMA": "firm"}],
    [{"LEMMA": "independent"}, {"LEMMA": "representative"}],
    [{"LEMMA": "independent"}, {"LEMMA": "partnership"}] ]

if len(matcher)==0:
    for r,p in zip(roles,patterns):
        matcher.add(r, None, p)

def get_matched_roles(matcher, text):
    matches = matcher(nlp(text.lower()))
    return list(set([nlp.vocab.strings[match_id] for match_id, start, end in matches]))

#%%
'''
Hierarchy documents label processing.
Label for pkl files .
'''

data_dir = "Distribution de produits et services financiers"

def label_pkl(filename):
    # opening the pickle
    with open(filename, 'rb') as fp:
        chapter_lst = pickle.load(fp)
    # File written in pkl format are list of chapters
    # format: chapter_lst[0].section_lst[0].subsection_lst[0][0].text
    for chap_id, chapter in enumerate(chapter_lst):
        # each chapter have a header and section list that
        # can be empty
        header = chapter.header
        section_lst = chapter.section_lst
        # print header id (e.g. CHAPTER I) and the title (e.g. SPECIAL PROVISION)
        # print(header.tid) #'CHAPTER I'
        # print(header.text) #'GENERAL PROVISIONS'
        header.roles=get_matched_roles(matcher,header.text)

        for section in section_lst:
            # print("Begin of Section", "\n")
            
            section_text=''
            # each section is composed of subsection_lst
            for subsection in section.subsection_lst:

                # a sub section can be a list of paragraph
                if isinstance(subsection, list):
                    for paragraph in subsection:
                        # print(paragraph.tid, paragraph.text)
                        section_text+='\n'+paragraph.text

                # or a single paragraph
                else:
                    # print(subsection.tid, subsection.text)
                    section_text+='\n'+subsection.text

            section.roles=get_matched_roles(matcher,section_text)
            # use the roles of father if the section has not roles
            if section.roles is None or len(section.roles)==0:
                section.roles=header.roles

            # Also each section has historical_note or simply footnotes
            # those refer to other part in the law or even to other law
            # for historical_note in section.historical_note_lst:
            #     print(historical_note.text)

            # print("End of Section", "\n")
    return chapter_lst

print("Reading file in pickle format")
file_lst = [y for x in os.walk(data_dir+"/Loi_PICKLE") for y in glob(os.path.join(x[0], '*pkl'))]
files_labeled={}
for filename in file_lst:
    print("Label the content of %s" % filename)
    files_labeled[filename.split('/')[-1]]=label_pkl(filename)
# with open('chapters_labeled.pkl', 'wb') as fp:
#     pickle.dump(chapters_labeled,fp)

#%%
'''
Label for Directive_MSWORD .
'''
def label_docx(filename):
    '''
    for a docx, return a 2-levels list: section->element.
    every section is a list that has some elements. a element include serval sentences.
    '''

    def cond(block):
        if any([run.font.size and run.font.bold for run in block.runs]): return True
        letter = [c for c in block.text if c.isalpha()]
        if len(letter) > 15 and len([c for c in letter if c.isupper()]) == len(letter): return True
        return False

    doc = Document(filename=filename, meta={})
    sections, par_lst = [], []
    
    for idx, block in enumerate(doc.story):
        if isinstance(block, Paragraph):
            if cond(block) and len(par_lst) > 4:
                sections.append(par_lst)
                par_lst = []
            if block.text:
                par_lst.append(block.text)

    if par_lst:
        sections.append(par_lst)
    
    # now we label only for the whole docx document
    # Can be changed to each section with its labels
    doc_text=' '.join([' '.join(sec) for sec in sections])
    roles=get_matched_roles(matcher,doc_text)

    return roles

print("Reading file in docx format")
file_lst = [y for x in os.walk(data_dir+"/Directive_MSWORD") for y in glob(os.path.join(x[0], '*docx'))]
docx_labeled={}
for filename in file_lst:
    print("Label the content of %s" % filename)
    docx_labeled[filename.split('/')[-1]]=label_docx(filename)
# with open('docx_labeled.pkl', 'wb') as fp:
#     pickle.dump(docx_labeled,fp)


#%%
'''
Check whether there rest some no-role sections.
'''
print('Check whether there rest some no-role sections...')
for chapter_lst in files_labeled.values():
    for chap_id, chapter in enumerate(chapter_lst):
        if chapter.header.roles is not None and len(chapter.header.roles)>0:
            # import pudb;pu.db
            section_lst = chapter.section_lst
            for section in section_lst:
                # print(section.roles)
                if section.roles is None or len(section.roles)==0:
                    section_text=''
                    # each section is composed of subsection_lst
                    for subsection in section.subsection_lst:
                        # a sub section can be a list of paragraph
                        if isinstance(subsection, list):
                            for paragraph in subsection:
                                # print(paragraph.tid, paragraph.text)
                                section_text+='\n'+paragraph.text
                        # or a single paragraph
                        else:
                            # print(subsection.tid, subsection.text)
                            section_text+='\n'+subsection.text
                    print('\n\n',chap_id, chapter.header.tid, chapter.header.roles, chapter.header.text)
                    print(section.roles, section_text)

print('Finish!')