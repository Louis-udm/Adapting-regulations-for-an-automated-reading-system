import os, subprocess
import json

def gen_query_param_file(query, index_path, mode="bm25", topk=50, query_param_path="/u/nieyifan/projects/CRM/app/query.param"):
    with open(query_param_path, 'w') as f_config:
        f_config.write('<parameters>\n')
        f_config.write('\t<index>' + index_path + '</index>\n')
        f_config.write('\t<query>\n')
        f_config.write('\t\t<number>' + str(1) + '</number>\n')
        f_config.write('\t\t<text>' + query + '</text>\n')
        f_config.write('\t</query>\n')
        f_config.write('\t<count>' + str(topk) + '</count>\n')
        f_config.write('\t<runID>runName</runID>\n')
        f_config.write('\t<trecFormat>true</trecFormat>\n')
        if mode == "bm25":
            print("INFO: ret_model: ", mode)
            rule = 'okapi,k1:1.2,b:0.75,k3:1000'
            f_config.write('\t<baseline>' + rule + '</baseline>\n')
        if mode == "lm":
            print("INFO: ret_model: ", mode)
            rule = 'method:dirichlet,mu:2500'
            f_config.write('\t<rule>' + rule + '</rule>\n')
        f_config.write('</parameters>\n')
        f_config.close()

def retrieve(query_file):
    cmd = "cd /u/nieyifan/indri5.3/bin/ \n {} {}".format("./IndriRunQuery", query_file)
    result = subprocess.check_output(cmd, shell=True)
    result = result.decode('utf-8') # convert bytes to string UTF-8
    result = result.split("\n")
    result = result[:-1]
    return result

def read_run(run):
    "1 Q0 Directive-0-454 1 7.12618 runName"
    runlist = []
    for line in run:
        fields = line.split()
        docno = fields[2]
        runlist.append(docno)
    return runlist

def show_docs(docno, index="/data/rali8/Tmp/nieyifan/CRM/AMF.idx/"):
    cmd1 = "cd /u/nieyifan/indri5.3/bin/ \n {} {} {} {} {}".format("./dumpindex", index, "di", "docno", docno)
    docid = subprocess.check_output(cmd1, shell=True)
    docid = docid.decode('utf-8')
    cmd2 = "cd /u/nieyifan/indri5.3/bin/ \n {} {} {} {}".format("./dumpindex", index, "dt", docid)
    doc_text = subprocess.check_output(cmd2, shell=True)
    doc_text = doc_text.decode('utf-8')
    return doc_text


def find_similar_terms(term, coll):
    """ given a query term (string) find related query expansion terms
        params: term: current query term
                coll: candidate expansion dict
        returns [dict] exp_terms = {'term': weight}
    """
    exp_terms = {}
    if coll.get(term) != None:
        e_terms = coll[term]['terms']
        e_weights = coll[term]['weights']
        for eterm, eweight in zip(e_terms, e_weights):
            if eterm != term:  # exclude the current original query term itself
                exp_terms[eterm] = eweight
    else:
        exp_terms[term + "s"] = 0
    return exp_terms
