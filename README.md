## The Ninth Montreal Industrial Problem Solving Workshop
[The Ninth Montreal Industrial Problem Solving Workshop](http://www.crm.umontreal.ca/probindustriels/?lang=en) is organized jointly by the Centre de recherches mathématiques (CRM) and the Institute for Data Valorization (IVADO). The workshop will gather representatives from industry, academic mathematicians, graduate students, and postdoctoral fellows. Participants will work in teams, each of which studying a concrete problem submitted by a company or a public or quasi-public institution. One of the goals of the workshop (IPSW) is to provide companies and institutions with mathematical tools for solving problems. An IPSW also allows professors and students in the mathematical sciences (including data science, statistics, optimization, mathematical finance, natural language processing, etc.) to analyze and solve real-world problems. The organizers view the workshop as an “incubator” of collaborations and hope that the work initiated during the workshop will lead to collaborations lasting several months or years.

## Adapting-regulations-for-an-automated-reading-system
> submitted by the Autorité des Marchés Financiers

> Jian-Yun Nie and Zhibin Lu and Pan Du and Yifan Nie (RALI of Université de Montréal)

The mandate of the Autorité des Marchés Financiers (AMF) is to develop and monitor the application of financial sector regulations for Québec companies and foreign companies offering their financial products in Québec. These regulations are available on the AMF web site. As an example, here are the regulations for securities.

https://lautorite.qc.ca/en/professionals/regulations-and-obligations/securities/

These regulations have a structure similar to that of a piece of legislation and include in particular: (1) definitions of varied entities (for instance the definition of “derivative”); (2) some articles; (3) regulations and guidance; (4) references to other regulations or legislative pieces.

In order to abide by the regulations, the financial sector companies are invited to understand the regulations so as to ensure that they are correctly applied to their specific cases. At the present time this understanding exercise is mostly “manual,” whether one is looking for the relevant sections or ensuring that the company is complying with the law. Within each financial sector company there is a compliance department, which ensures that the company complies with all the regulations (whether the AMF regulations or those of other relevant institutions).

With the goal of lightening the regulatory burden, several projects have been launched in other countries by organizations similar to the AMF, in order to adapt regulations for an automated reading system. Here are two examples, from the United States and the United Kingdom (respectively).

http://www.finra.org/industry/special-notice-073018 

https://www.finextra.com/pressarticle/70869/corlytics-helps-create-intelligent-rule-book-for-fca

## Guid

### Requirements
- python 3.x
- spaCY 2.1
- indri lemur 5.3 (Compiled under Debian 9 Linux)
- flask

### Usage

0. Prerequisites: Indri, python3 (with json, pickle, flask)
1. (if not installed) Install indri open source search engine: https://sourceforge.net/projects/lemur/files/lemur/indri-5.3/
    or use pre-compiled linux binaries included in indri/bin/

2. Run tools/convert_to_trec.py to convert the docx, pkls files into trec text format in order to let indri build the index
    ```python
    cd tools/
    python convert_to_trec.py --baseinpath path_to_father_folder_of_docx/pkl_fils
    --outpath path_to_the_generated_trec_text_file
    ```

3. Build paragraph index by indri.
``` 
cd indri/bin/
./IndriBuildIndex indriparam.txt
```
where indriparam.txt is a pre-defined indexing paramter file, an example is provided in tools/indexparam.txt
indri website has detailed usage: https://sourceforge.net/p/lemur/wiki/IndriBuildIndex%20Parameters/

4. Classify scope of applicability for regulations:
```
python train_scope_label.py
```
We use the rule match functions of [*spaCY*](https://spacy.io/api/matcher). If the child section doesn't match a scope role, it will inherit the role of the parent chapter. Just run *python train_scope_label.py* will produce the labeled documents and dump to *pickle* files.
```
python label_passages_pkl.py
```
*label_passages_pkl.py* is used to add role label to the passages.pkl 

5.  Run web service (the app/ folder contains the backend codes, and app/templates contains webpages)
```
export FLASK_APP=service.py
flask run --port=8888 (or your desired port)
```
6. Launch the website: in your browser type: localhost:8888/index and press return
