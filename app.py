"""
SSTI (Server-Side Template Injection) -> RCE  —  CLASSROOM LAB
==============================================================
Application Security demo. Runs ONLY on your own machine (localhost).
A deliberately vulnerable "Greeting Card Generator" so you can SAFELY
demonstrate how SSTI escalates from a harmless-looking input box all the
way to running operating-system commands on the server (Remote Code
Execution), and then show the fix.

Run:   python app.py
Open:  http://127.0.0.1:5000
"""

from flask import Flask, request, render_template, render_template_string

app = Flask(__name__)


# ---------- Landing page ----------
@app.route("/")
def home():
    return render_template("index.html")


# =====================================================================
#  VULNERABLE ENDPOINT  (this is the bug you demonstrate)
# =====================================================================
#  THE MISTAKE: user input is concatenated DIRECTLY into the template
#  SOURCE and handed to render_template_string(). Jinja2 then EXECUTES
#  whatever template syntax the user typed. That single line is the whole
#  vulnerability.
# ---------------------------------------------------------------------
@app.route("/vulnerable")
def vulnerable():
    name = request.args.get("name", "friend")

    # !!! DANGER: user input becomes part of the template that gets executed
    inner = render_template_string("Hello, " + name + "! Have a lovely day.")

    # The surrounding page is a normal, safe template. We inject the already
    # executed fragment with |safe so the demo output shows through.
    return render_template("vuln.html", rendered=inner, name_val=name)


# =====================================================================
#  SECURE ENDPOINT  (this is the fix you demonstrate)
# =====================================================================
#  THE FIX: user input is passed as DATA (a context variable), never as
#  template source. Jinja2 auto-escapes it and treats {{7*7}} as literal
#  text, so nothing is executed.
# ---------------------------------------------------------------------
@app.route("/secure")
def secure():
    name = request.args.get("name", "friend")
    return render_template("card.html", name=name)


if __name__ == "__main__":
    # debug=False so a payload can't pop the Werkzeug debugger; we want to
    # show the vulnerability itself, not a debug-console shortcut.
    import os
    host = os.environ.get("HOST", "127.0.0.1")  # Docker sets 0.0.0.0
    app.run(host=host, port=5000, debug=False)
