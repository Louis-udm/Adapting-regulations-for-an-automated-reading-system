from app import app
from flask import Flask, request, render_template, redirect, url_for
import os, subprocess, json, ast

from app.indri_utils import gen_query_param_file, retrieve, read_run, show_docs, find_similar_terms
from app.render_utils import render_ranked_documents


### global vars ###
new_query_terms = {}
expanded_query = ""

### Index ###
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/index', methods=['POST'])
def index_post():
    role = request.form.get("role", None)
    if role != None:
        globel_role = role
        if request.form.get('query_expansion'):
            return redirect(url_for('form2_post', messages=role))  # the endpoint for url_for should be the function name
        else:
            return redirect(url_for('form1_post', messages=role))  # the endpoint for url_for should be the function name
    return render_template('index.html')

### simple query textbox ###
@app.route('/query')
def form():
    return render_template('form.html')

@app.route('/query', methods=['POST'])
def form_post():
    query = request.form['query']
    processed_query = query.lower()
    gen_query_param_file(processed_query, index_path="/data/rali8/Tmp/nieyifan/CRM/AMF.idx/", mode="bm25")
    run = retrieve("/u/nieyifan/projects/CRM/app/query.param")
    run = read_run(run)
    doc_text = show_docs(run[0])
    return doc_text

### show top K documents ###
@app.route('/query1')
def form1():
    return render_template("form_topk.html")

@app.route('/query1', methods=['POST'])
def form1_post():
    role2cat = {  # role to category map
        'all': 0,
        'insurance representative': 1,
        'representative in insurance of person': 2,
        'group insurance representative': 3,
        'damage insurance agent': 4,
        'damage insurance broker': 5,
        'claims adjuster': 6,
        'financial planner': 7,
        'firm': 8,
        'independent representative': 9,
        'independent partnership': 10
    }
    role = request.args['messages']  # string role
    print("INFO: Role: ", role)
    query = request.form['query']
    topk = request.form['topk']
    topk = int(topk)
    processed_query = query.lower()
    cat_id = role2cat[role]
    if request.form.get('ret_model_bm25'):
        if role == "all":
            gen_query_param_file(processed_query, index_path="/data/rali8/Tmp/nieyifan/CRM/AMF.idx/", mode="bm25")
        else:
            gen_query_param_file(processed_query, index_path="/data/rali8/Tmp/nieyifan/CRM/AMF_{}.idx/".format(cat_id), mode="bm25")
    if request.form.get('ret_model_lm'):
        if role == "all":
            gen_query_param_file(processed_query, index_path="/data/rali8/Tmp/nieyifan/CRM/AMF.idx/", mode="lm")
        else:
            gen_query_param_file(processed_query, index_path="/data/rali8/Tmp/nieyifan/CRM/AMF_{}.idx/".format(cat_id), mode="lm")
    run = retrieve("/u/nieyifan/projects/CRM/app/query.param")
    run = read_run(run)
    num_docs = topk
    if len(run) < topk:
        num_docs = len(run)
    html = render_ranked_documents(run, num_docs)
    return html


### with query expension / query submission page ###
@app.route('/query2')
def form2():
    return render_template("form_topk_query_input.html")

@app.route('/query2', methods=['POST'])
def form2_post():
    role = request.args['messages']  # string role
    print("INFO: Role: ", role)
    query = request.form['query']
    topk = request.form['topk']
    topk = int(topk)
    if request.form.get('ret_model_bm25'):
        ret_model = "bm25"
    if request.form.get('ret_model_lm'):
        ret_model = "lm"
    ## load query expansion dict ##
    with open("/u/nieyifan/projects/CRM/data2/docu_topk.json", 'r') as f_js:
        q_exp_dict = json.load(f_js)
    processed_query = query.lower()
    query_terms = processed_query.split()
    all_exp_terms = {}  # containing all candidate expansion terms for all query terms
    for q_term in query_terms:
        exp_terms = find_similar_terms(q_term, q_exp_dict)
        print(exp_terms)
        all_exp_terms.update(exp_terms)
    msg_dict = {'role': role, 'query_terms': query_terms,
                'query': processed_query, 'ret_model': ret_model,
                'topk': topk, 'all_exp_terms': all_exp_terms}
    return redirect(url_for('form3_post', messages=msg_dict))  # the endpoint for url_for should be the function name

### with query expansion / expansion selection - search page ###

@app.route('/query3')
def form3():
    return render_template("form_topk_expansion.html")

@app.route('/query3', methods=['POST'])
def form3_post():
    role2cat = {  # role to category map
        'all': 0,
        'insurance representative': 1,
        'representative in insurance of person': 2,
        'group insurance representative': 3,
        'damage insurance agent': 4,
        'damage insurance broker': 5,
        'claims adjuster': 6,
        'financial planner': 7,
        'firm': 8,
        'independent representative': 9,
        'independent partnership': 10
    }
    global expanded_query
    global new_query_terms
    msg = request.args['messages']
    msg_dict = ast.literal_eval(msg)
    role = msg_dict['role']
    query = msg_dict['query']
    query_terms = msg_dict['query_terms']
    all_exp_terms = msg_dict['all_exp_terms']  # containing all candidate expansion terms for all query terms
    topk = msg_dict['topk']
    ret_model = msg_dict['ret_model']
    cat_id = role2cat[role]  # role/category id
    print("INFO: Role: ", role)
    print("INFO: query: ", query)
    print("INFO: all_exp_terms: ", all_exp_terms)
    print("INFO: topk: ", topk)
    print("INFO: ret_model: ", ret_model)
    #for q_term in query_terms:
    #    new_query_terms[q_term] = 1.0
    if request.form.get('action') == "init":
        expanded_query = ""
        print("INFO: expanded query cleared:", expanded_query)
        new_query_terms = {}
        for q_term in query_terms:
            new_query_terms[q_term] = 1.0
        print("INFO: new_query_terms init:", new_query_terms)
        return render_template('form_topk_expansion.html', query_text="You entered query: " + query, all_exp_terms=all_exp_terms)
    elif request.form.get('action') == "add":
        exp_item = request.form.get("exp_term")  # stock:0.7
        exp_item = exp_item.split(":")
        new_query_terms[exp_item[0]] = float(exp_item[1])
        print("INFO: new_query_terms: ", new_query_terms)
        exp_query_parts = []
        for term in new_query_terms:
            exp_query_parts.append(str(new_query_terms[term]) + " " + term)
        expanded_query = "#weight(" + " ".join(exp_query_parts) + ")"
        return render_template('form_topk_expansion.html', query_text="You entered query: " + query,
                               all_exp_terms=all_exp_terms, expanded_query=expanded_query)
    elif request.form.get('action') == "search":
        print(expanded_query)
        if ret_model == "bm25":
            return render_template("form_topk_expansion.html")
        elif ret_model == "lm":
            print("INFO: expanded query: ", expanded_query)
            if role == "all":
                gen_query_param_file(expanded_query, index_path="/data/rali8/Tmp/nieyifan/CRM/AMF.idx/", mode="lm")
            else:
                gen_query_param_file(expanded_query, index_path="/data/rali8/Tmp/nieyifan/CRM/AMF_{}.idx/".format(cat_id), mode="lm")
            run = retrieve("/u/nieyifan/projects/CRM/app/query.param")
            run = read_run(run)
            num_docs = topk
            if len(run) < topk:
                num_docs = len(run)
            html = render_ranked_documents(run, num_docs)
            return html
        else:
            return render_template("form_topk_expansion.html")
    else:
        return render_template("form_topk_expansion.html")
