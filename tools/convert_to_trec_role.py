import argparse
import glob
import pickle

from demo import read_pkl, read_pass_from_pkl
from demo import read_docx, read_pass_from_docx, decompose_docx


def _write_doc_trec(docno, text, f_out):
    "write to file"
    f_out.write("<DOC>\n")
    f_out.write("<DOCNO> " + docno + " </DOCNO>\n")
    f_out.write("<TEXT>\n")
    f_out.write(text + "\n")
    f_out.write("</TEXT>\n")
    f_out.write("</DOC>\n")


def convert_passage_level(baseinpath, outpath, category):
    """
    perform document retrieval
    treat all document as document, if having sections, treat sections as fields
    """
    """
    loi_path = "{}/Loi_PICKLE/".format(baseinpath)
    regle_path = "{}/Reglement_PICKLE/".format(baseinpath)
    directive_path = "{}/Directive_MSWORD/".format(baseinpath)
    guide_path = "{}/Guide_MSWORD/".format(baseinpath)

    loi_files = glob.glob("{}/*.pkl".format(loi_path))
    regle_files = glob.glob("{}/*.pkl".format(regle_path))
    directive_files = glob.glob("{}/*.docx".format(directive_path))
    guide_files = glob.glob("{}/*.docx".format(guide_path))
    """
    f_trec = open(outpath, 'w')
    ## role map dict ##
    cat2role = {
        1: 'insurance representative',
        2: 'representative in insurance of person',
        3: 'group insurance representative',
        4: 'damage insurance agent',
        5: 'damage insurance broker',
        6: 'claims adjuster',
        7: 'financial planner',
        8: 'firm',
        9: 'independent representative',
        10: 'independent partnership'
    }

    with open(baseinpath, "rb") as f:
        data = pickle.load(f)
    for docno in data:
        target_role = cat2role[category]
        doc_role_raw = data[docno]['label'].split(",")  # [""] or ["individual"] or ["individual", " firm"]
        doc_role_clean = [r.strip() for r in doc_role_raw]
        if target_role in doc_role_clean:
            _write_doc_trec(docno, data[docno]['text'], f_trec)
    f_trec.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseinpath", type=str, default="")
    parser.add_argument("--outpath", type=str, default="")
    parser.add_argument("--category", type=int, default=0)
    args = parser.parse_args()
    convert_passage_level(args.baseinpath, args.outpath, args.category)


if __name__ == '__main__':
    main()
