from app import app

from app.indri_utils import show_docs

def render_ranked_documents(run_docnos, num_docs):
    html_secs = []
    html_secs.append("""<style> \n
    div.centering \n
    { \n
    margin: 0 auto; \n
    margin-left: auto; \n
    margin-right: auto; \n
    text-align:center; \n
    } \n
    </style>""")
    html_secs.append("""
    <div class="centering"> \n
    <img src="https://lautorite.qc.ca/typo3conf/ext/amf_site_lautorite/Resources/Public/Assets/img/logo-amf-header.png" alt="amf"> \n
    <h2> \n
      <span style="color: blue;"> Search Results </span> \n
    </h2> \n
    </div> \n
    """)
    for k in range(num_docs):
        html_secs.append("<p> " + show_docs(run_docnos[k]) + " </p>")
    html_file = "\n".join(html_secs)
    return html_file
