import argparse
import glob
import pickle

from demo import read_pkl, read_pass_from_pkl
from demo import read_docx, read_pass_from_docx, decompose_docx


def extract_passages(baseinpath, outpath):
    data = {}

    loi_path = "{}/Loi_PICKLE/".format(baseinpath)
    regle_path = "{}/Reglement_PICKLE/".format(baseinpath)
    directive_path = "{}/Directive_MSWORD/".format(baseinpath)
    guide_path = "{}/Guide_MSWORD/".format(baseinpath)

    loi_files = glob.glob("{}/*.pkl".format(loi_path))
    regle_files = glob.glob("{}/*.pkl".format(regle_path))
    directive_files = glob.glob("{}/*.docx".format(directive_path))
    guide_files = glob.glob("{}/*.docx".format(guide_path))
    # loi files
    for file in loi_files:
        docid = file.split("/")[-1]
        docid = docid.split(".")[0]
        docno_prefix = "Loi"
        passages = read_pass_from_pkl(file)
        passage_id = 0
        for passage_text in passages:
            docno = docno_prefix + "-" + docid + "-" + str(passage_id)
            data[docno] = {'text': passage_text, 'label': ""}
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
            data[docno] = {'text': passage_text, 'label': ""}
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
            data[docno] = {'text': passage_text, 'label': ""}
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
            data[docno] = {'text': passage_text, 'label': ""}
            passage_id += 1
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseinpath", type=str, default="")
    parser.add_argument("--outpath", type=str, default="")
    args = parser.parse_args()
    passage = extract_passages(args.baseinpath, args.outpath)
    with open(args.outpath, 'wb') as f:
        pickle.dump(passage, f)


if __name__ == '__main__':
    main()
