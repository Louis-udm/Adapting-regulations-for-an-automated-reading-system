import os, subprocess

def gen_query_param_file(query, index_path, mode="bm25", topk=50, query_param_path="query.param"):
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
            rule = 'okapi,k1:1.2,b:0.75,k3:1000'
            f_config.write('\t<baseline>' + rule + '</baseline>\n')
        if mode == "lm":
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
    print(doc_text)
