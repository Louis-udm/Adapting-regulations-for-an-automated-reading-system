#%%
import os, pickle
from glob import glob
from document import Document, Paragraph, Table
from utils import *

#%%
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

print('Start label passages.pkl...')
# opening the pickle
with open('passages.pkl', 'rb') as fp:
    passages = pickle.load(fp)
for k in passages.keys():
    text=passages[k]['text']
    roles_matched=', '.join(get_matched_roles(matcher,text))
    print(k,':',roles_matched)
    passages[k]['label']=roles_matched
    # if roles_matched is None or roles_matched.strip()=='':
    #     print('\n------------------\n',k,':\n',text)

with open('passages_labeled.pkl', 'wb') as fp:
    pickle.dump(passages,fp)
