import argparse
import glob

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


def convert_passage_level(baseinpath, outpath):
    """
    perform document retrieval
    treat all document as document, if having sections, treat sections as fields
    """
    loi_path = "{}/Loi_PICKLE/".format(baseinpath)
    regle_path = "{}/Reglement_PICKLE/".format(baseinpath)
    directive_path = "{}/Directive_MSWORD/".format(baseinpath)
    guide_path = "{}/Guide_MSWORD/".format(baseinpath)

    loi_files = glob.glob("{}/*.pkl".format(loi_path))
    regle_files = glob.glob("{}/*.pkl".format(regle_path))
    directive_files = glob.glob("{}/*.docx".format(directive_path))
    guide_files = glob.glob("{}/*.docx".format(guide_path))

    f_trec = open(outpath, 'w')
    # loi files
    for file in loi_files:
        docid = file.split("/")[-1]
        docid = docid.split(".")[0]
        docno_prefix = "Loi"
        passages = read_pass_from_pkl(file)
        passage_id = 0
        for passage_text in passages:
            docno = docno_prefix + "-" + docid + "-" + str(passage_id)
            _write_doc_trec(docno, passage_text, f_trec)
            passage_id += 1
    # regle files
    for file in regle_files:
        docid = file.split("/")[-1]
        docid = docid.split(".")[0]
        docno_prefix = "Reglement"
        passages = read_pass_from_pkl(file)
        passage_id = 0
        for passage_text in passages:
            docno = docno_prefix + "-" + docid + "-" + str(passage_id)
            _write_doc_trec(docno, passage_text, f_trec)
            passage_id += 1
    # directive files
    for file in directive_files:
        docid = file.split("/")[-1]
        docid = docid.split(".")[0]
        docno_prefix = "Directive"
        passages = decompose_docx(file)  # [[sent0, sent1,...], ...]
        passage_id = 0
        for passage in passages:
            passage_text = '\n'.join(passage)
            docno = docno_prefix + "-" + docid + "-" + str(passage_id)
            _write_doc_trec(docno, passage_text, f_trec)
            passage_id += 1
    # directive files
    for file in guide_files:
        docid = file.split("/")[-1]
        docid = docid.split(".")[0]
        docno_prefix = "Guide"
        passages = decompose_docx(file)
        passage_id = 0
        for passage in passages:
            passage_text = '\n'.join(passage)
            docno = docno_prefix + "-" + docid + "-" + str(passage_id)
            _write_doc_trec(docno, passage_text, f_trec)
            passage_id += 1
    f_trec.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseinpath", type=str, default="")
    parser.add_argument("--outpath", type=str, default="")
    args = parser.parse_args()
    convert_passage_level(args.baseinpath, args.outpath)


if __name__ == '__main__':
    main()
