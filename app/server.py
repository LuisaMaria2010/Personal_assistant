from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import atexit

from app.bootstrap import bootstrap
from agents.scheduler_agent import AgentScheduler
from supervisor.events import EventType
from supervisor.state import AppState
from tools.feedback_tools import save_user_feedback


# =================================================
# BOOTSTRAP SOLO UNA VOLTA (processo unico)
# =================================================

ctx = bootstrap()

supervisor = ctx["supervisor"]
vector_storage = ctx["vector_storage"]

scheduler = AgentScheduler(supervisor)
scheduler.start()


# shutdown pulito
atexit.register(vector_storage.close)


app = FastAPI()


# =================================================
# UI minimale
# =================================================

HTML = HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<style>
body {
    font-family: Inter, Arial;
    background:#fafafa;
    max-width:600px;
    margin:40px auto;
}

/* chat layout */
#chat {
    display:flex;
    flex-direction:column;
    gap:12px;
}

/* bubbles */
.msg {
    padding:12px 16px;
    border-radius:18px;
    max-width:80%;
    line-height:1.4;
}

.bot {
    background:#f1f1f1;
    align-self:flex-start;
}

.user {
    background:#d9ecff;
    align-self:flex-end;
}

/* cards */
.card {
    background:white;
    padding:16px;
    border-radius:16px;
    box-shadow:0 4px 10px rgba(0,0,0,.08);
}

/* buttons */
button {
    padding:10px 14px;
    border:none;
    border-radius:10px;
    cursor:pointer;
    margin-top:10px;
}

.primary {
    background:#2563eb;
    color:white;
}

.secondary {
    background:#e5e7eb;
}

input[type=text] {
    padding:10px;
    border-radius:10px;
    border:1px solid #ddd;
    width:75%;
}
</style>
</head>

<body>

<h2>🧠 AI Coach</h2>

<div id="chat"></div>

<div id="inputBox">
    <input id="goalInput" placeholder="Scrivi il tuo goal..." />
    <button class="primary" onclick="sendGoal()">Invia</button>
</div>


<script>
// Loading overlay semplice
function showLoading(text="Caricamento..."){
    if(document.getElementById("loadingOverlay")) return;
    const overlay = document.createElement("div");
    overlay.id = "loadingOverlay";
    overlay.style.position = "fixed";
    overlay.style.top = 0;
    overlay.style.left = 0;
    overlay.style.width = "100vw";
    overlay.style.height = "100vh";
    overlay.style.background = "rgba(255,255,255,0.7)";
    overlay.style.display = "flex";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";
    overlay.style.zIndex = 9999;
    overlay.innerHTML = `<div style='padding:30px 40px;background:#fff;border-radius:16px;box-shadow:0 2px 10px #0002;font-size:1.2em;'>${text}</div>`;
    document.body.appendChild(overlay);
}

function hideLoading(){
    const overlay = document.getElementById("loadingOverlay");
    if(overlay) overlay.remove();
}
let currentGoal = "";
let currentGoalId = null;


/* ------------------- UI helpers ------------------- */

function bubble(text, cls="bot"){
    const d=document.createElement("div");
    d.className="msg "+cls;
    d.innerHTML=text;
    chat.appendChild(d);
}

let typingEl = null;

function showTyping(text="Coach sta scrivendo"){
    typingEl = document.createElement("div");
    typingEl.className = "msg bot";

    typingEl.innerHTML = `
        ${text}
        <span class="typing">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        </span>
    `;

    chat.appendChild(typingEl);
}

function hideTyping(){
    if(typingEl){
        typingEl.remove();
        typingEl = null;
    }
}

function card(html){
    const d=document.createElement("div");
    d.className="card";
    d.innerHTML=html;
    chat.appendChild(d);
}


/* ------------------- FLOW 1: PLAN ------------------- */

async function sendGoal(){
    const goal = goalInput.value;
    if(!goal) return;

    currentGoal = goal;

    bubble(goal,"user");

    const form=new URLSearchParams();
    form.append("goal",goal);

    showTyping();

    const res=await fetch("/plan-preview",{method:"POST",body:form});
    const plan=await res.json();

    hideTyping();

    let tasks=plan.tasks.map(t=>"• "+t.title).join("<br>");

    bubble("Ti propongo questo piano:<br><br>"+tasks+"<br><br>Ti va bene?");

    card(`
        <button class="primary" onclick="confirmPlan()">✅ Conferma</button>
        <button class="secondary" onclick="editPlan()">✏️ Modifica</button>
    `);
}


async function confirmPlan(){

    showLoading("Creo il piano personalizzato...");

    const form=new URLSearchParams();
    form.append("goal",currentGoal);

    try{
        showTyping("Sto creando il piano...");

        const res = await fetch("/confirm-plan",{method:"POST",body:form});
        const data = await res.json();
        currentGoalId = data.goal_id;   // 🔥 salva

        hideTyping();
        hideLoading();

        bubble("Perfetto! Piano salvato 🎉");
        showDailyButton();
    }
    catch(e){
        hideLoading();
        bubble("⚠️ Errore durante il salvataggio");
        console.error(e);
    }
}


function editPlan(){
    bubble("Ok, scrivi una nuova versione del goal ✏️");
}

function showDailyButton(){
    card(`
        <button class="primary" onclick="loadDaily()">
            👉 Vai al goal quotidiano
        </button>
    `);
}



/* ------------------- FLOW 2: DAILY ------------------- */

async function loadDaily(){

    showTyping();

    const res=await fetch(`/daily?goal_id=${currentGoalId}`);
    const data=await res.json();

    hideTyping();


    bubble(data.message);

    let tasksHTML=data.tasks.map(t=>
        `<label><input type="checkbox" value="${t.id}"> ${t.description}</label><br>`
    ).join("");

    card(`
        <h3>🎯 Oggi</h3>
        ${tasksHTML}
        <br><br>

        Difficoltà<br>
        <input id="diff" type="range" min="1" max="5"><br><br>

        Energia<br>
        <input id="energy" type="range" min="1" max="5"><br><br>

        <textarea id="note" placeholder="Note opzionali"></textarea><br>

        <button class="primary" onclick="finishDay(${data.goal_id})">
            Salva giornata
        </button>
    `);

}

async function finishDay(goalId){

    const checked=[...document.querySelectorAll("input[type=checkbox]:checked")]
        .map(x=>x.value)
        .join(",");

    const form=new URLSearchParams();
    form.append("goal_id",goalId);
    form.append("task_ids",checked);
    form.append("difficulty",diff.value);
    form.append("energy",energy.value);
    form.append("note",note.value);

    form.append("goal_id", currentGoalId);  // 🔥

    await fetch("/feedback",{method:"POST",body:form});

    bubble("Ottimo lavoro 🔥 Feedback salvato!");
    // Dopo il salvataggio, carica automaticamente il goal successivo
    setTimeout(loadDaily, 1200); // breve pausa per mostrare il messaggio
}

</script>

</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML


# =================================================
# ENDPOINTS
# =================================================

@app.post("/goal")
def create_goal(goal: str = Form(...)):
    supervisor.handle(
        AppState(
            event=EventType.NEW_GOAL,
            meta={"goal_text": goal}
        )
    )
    return {"status": "goal created"}


@app.get("/daily-ui", response_class=HTMLResponse)
def daily_ui():

    result = supervisor.handle(
        AppState(event=EventType.DAILY)
    )

    message = result["message"]
    tasks = result["tasks"]

    tasks_html = "".join(
        f'<label><input type="checkbox" value="{t["id"]}"> {t["description"]}</label><br>'
        for t in tasks
    )

    return f"""
    <html>
    <style>
    body {{
        font-family: Arial;
        max-width: 500px;
        margin: 30px auto;
    }}
    .bubble {{
        background:#f2f2f2;
        padding:12px;
        border-radius:14px;
        margin-bottom:15px;
    }}
    .card {{
        background:white;
        padding:15px;
        border-radius:12px;
        box-shadow:0 2px 6px rgba(0,0,0,.1);
    }}
    button {{
        margin-top:10px;
        padding:8px 12px;
    }}
    .typing {{
    display:inline-flex;
    gap:4px;
    align-items:center;
    }}
    .dot {{
        width:6px;
        height:6px;
        background:#888;
        border-radius:50%;
        animation:blink 1.4s infinite both;
    }}

    .dot:nth-child(2){{ animation-delay:.2s; }}
    .dot:nth-child(3){{ animation-delay:.4s; }}

    @keyframes blink {{
        0%{{ opacity:.2; }}
        20%{{ opacity:1; }}
        100%{{ opacity:.2; }}
    }}    
    </style>

    <body>

    <div class="bubble">
        {message}
    </div>

    <div class="card">
        <h3>🎯 Oggi</h3>
        {tasks_html}

        <br>
        Difficoltà <input type="range" min="1" max="5"><br>
        Energia <input type="range" min="1" max="5"><br>

        <button onclick="alert('Feedback salvato!')">Salva giornata</button>
    </div>

    </body>
    </html>
    """



# -------------------------
# PLAN preview (LLM only)
# -------------------------
@app.post("/plan-preview")
def preview(goal: str = Form(...)):
    return supervisor.planner.plan(goal)


# -------------------------
# CONFIRM + SAVE
# -------------------------
@app.post("/confirm-plan")
def confirm(goal: str = Form(...)):
    goal_id = supervisor.planner.execute(goal)
    return {"goal_id": goal_id}


# -------------------------
# DAILY
# -------------------------
@app.get("/daily")
def daily(
    goal_id: int = None
):
    result = supervisor.handle(AppState(
        event=EventType.DAILY,
        goal_id=goal_id))


    return {
        "goal": result.get("goal_text"),  
        "goal_id": result.get("goal_id"),
        "message": result["message"],
        "tasks": result["tasks"]
    }

# -------------------------
# FEEDBACK
# -------------------------

@app.post("/feedback")
def feedback(
    goal_id: int = Form(...),
    task_id: int = Form(...),
    done: bool = Form(...),
    difficulty: int = Form(...),
    energy: int = Form(...),
    note: str = Form("")
):
    """
    task_ids arriva come "1,2,3"
    """

    ids = [int(x) for x in task_id.split(",") if x]

    for t in ids:
        save_user_feedback(
            task_id=t,
            feedback={
                "done": True,
                "difficulty": difficulty,
                "energy": energy,
                "note": note
            }
        )

    return {"ok": True}

