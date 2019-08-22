#%%
import os

def set_work_dir(local_path="stage/CRM_workshop", server_path="myprojects/CRM_workshop"):
    if os.path.exists(os.path.join(os.getenv("HOME"), local_path)):
        os.chdir(os.path.join(os.getenv("HOME"), local_path))
    elif os.path.exists(os.path.join(os.getenv("HOME"), server_path)):
        os.chdir(os.path.join(os.getenv("HOME"), server_path))
    else:
        raise Exception('Set work path error!')
set_work_dir()

import os, pickle
from glob import glob
from document import Document, Paragraph, Table
from utils import *

#%%

import spacy
nlp = spacy.load("en_core_web_lg")

testdoc = nlp(u"""representatives in insurance of persons or insurance representatives are a natural person who offers individual insurance products in insurance of persons or individual annuities from one or more insurers directly to the public, to a firm, to an independent representative or to an independent partnership.
A representative in insurance of persons is authorized to secure the adhesion of a person in respect of a group insurance or group annuity contract.
The following are not representatives in insurance of persons and for claims adjuster:
(1)  persons who, on behalf of an employer, a union, a professional order or an association or professional syndicate constituted under the Professional Syndicates Act (chapter S‐40), secure the adhesion of an employee of that employer or of a member of that union, professional order, association or professional syndicate in respect of a group contract in insurance of persons or a group annuity contract;
(2)  the members of a mutual benefit association who offer policies for the mutual benefit association.
We have Insurance Representatives
and Representative in Insurance of Persons
and Group Insurance Representatives
and Damage Insurance agents
and damage insurance brokers
and Claims Adjusters
and financial planners and
firms and independent representatives and independent partnerships.""".lower())

from spacy.matcher import Matcher
# from spacy.matcher import PhraseMatcher
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
    matches = matcher(nlp(text))
    return list(set([nlp.vocab.strings[match_id] for match_id, start, end in matches]))

# test
matches = matcher(testdoc)
for match_id, start, end in matches:
    string_id = nlp.vocab.strings[match_id]  # Get string representation
    span = testdoc[start:end]  # The matched span
    print(string_id, ':', start, end, span.text)



#%%
if False:
    print('Start label Yifan\'s passages.pkl...')
    # opening the pickle
    with open('passages.pkl', 'rb') as fp:
        passages = pickle.load(fp)
    for k in passages.keys():
        text=passages[k]['text']
        matches = matcher(nlp(text))
        roles_matched=', '.join(set([nlp.vocab.strings[match_id] for match_id, start, end in matches]))
        print(k,':',roles_matched)
        passages[k]['label']=roles_matched
        # if roles_matched is None or roles_matched.strip()=='':
        #     print('\n------------------\n',k,':\n',text)

    with open('passages_labeled.pkl', 'wb') as fp:
        pickle.dump(passages,fp)
#%%

if True:
    print('Start label hierarchy documents...')
    print("Reading Loi file in pickle format")
    # opening the pickle
    with open('Distribution de produits et services financiers/Loi_PICKLE/D-9.2 - Act respecting the distribution of financial products and services.pkl', 'rb') as fp:
        chapter_lst = pickle.load(fp)
    # chapter_lst[0].section_lst[0].subsection_lst[0][0].text
    for chap_id, chapter in enumerate(chapter_lst):
        # each chapter have a header and section list that
        # can be empty
        header = chapter.header
        section_lst = chapter.section_lst
        # import pudb;pu.db
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
            if section.roles is None or len(section.roles)==0:
                section.roles=header.roles

            # Also each section has historical_note or simply footnotes
            # those refer to other part in the law or even to other law
            # for historical_note in section.historical_note_lst:
            #     print(historical_note.text)

            # print("End of Section", "\n")
#%%
for chap_id, chapter in enumerate(chapter_lst):
    if chapter.header.roles is not None and len(chapter.header.roles)>0:
        print(chap_id, chapter.header.tid, chapter.header.roles, chapter.header.text)
        section_lst = chapter.section_lst
        for section in section_lst:
            print(section.roles)