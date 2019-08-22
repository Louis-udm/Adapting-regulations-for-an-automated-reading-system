# Usage
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

4. Classify paragraphs with role labels:
\\TODO Zhibin Lv

5.  Run web service (the app/ folder contains the backend codes, and app/templates contains webpages)
```
export FLASK_APP=service.py
flask run --port=8888 (or your desired port)
```
6. Launch the website: in your browser type: localhost:8888/index and return
