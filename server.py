import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="PIYASH LEVEL UP Management Panel", version="1.0.0")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# In-memory process and log manager
active_processes: Dict[str, subprocess.Popen] = {}
process_logs: Dict[str, List[str]] = {}
MAX_LOG_LINES = 300

class AccountCreate(BaseModel):
    category: str  # "2_level" or "3_level"
    uid: int
    password: str
    name: str
    auto_start: bool = False

def load_accounts() -> List[dict]:
    if not os.path.exists(ACCOUNTS_FILE):
        default_accounts = [
            {
                "id": "acc-2lvl-1",
                "category": "2_level",
                "uid": 794006,
                "password": "MARUF",
                "name": "M4RUF Standard Bot",
                "created_at": int(time.time()),
                "status": "STOPPED"
            },
            {
                "id": "acc-3lvl-1",
                "category": "3_level",
                "uid": 4752927952,
                "password": "PIYASH_KVYDC_BY_STAR_GMR_FL7HG",
                "name": "PIYASH Lone Wolf Pump",
                "created_at": int(time.time()),
                "status": "STOPPED"
            }
        ]
        save_accounts(default_accounts)
        return default_accounts
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_accounts(accounts: List[dict]):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)

def append_log(account_id: str, line: str):
    if account_id not in process_logs:
        process_logs[account_id] = []
    timestamp = time.strftime("[%H:%M:%S] ")
    clean_line = line.strip()
    if clean_line:
        process_logs[account_id].append(timestamp + clean_line)
        if len(process_logs[account_id]) > MAX_LOG_LINES:
            process_logs[account_id].pop(0)

def log_reader_thread(account_id: str, proc: subprocess.Popen):
    import threading
    def _read_stream(stream):
        try:
            for raw_line in iter(stream.readline, b''):
                decoded = raw_line.decode('utf-8', errors='replace')
                append_log(account_id, decoded)
        except Exception:
            pass

    t_out = threading.Thread(target=_read_stream, args=(proc.stdout,), daemon=True)
    t_err = threading.Thread(target=_read_stream, args=(proc.stderr,), daemon=True)
    t_out.start()
    t_err.start()

def get_live_status(account: dict) -> str:
    acc_id = account["id"]
    if acc_id in active_processes:
        proc = active_processes[acc_id]
        ret = proc.poll()
        if ret is None:
            return "RUNNING"
        else:
            del active_processes[acc_id]
            return "CRASHED" if ret != 0 else "STOPPED"
    return account.get("status", "STOPPED")

@app.get("/api/accounts")
def get_accounts(category: Optional[str] = None):
    accounts = load_accounts()
    updated = False
    for acc in accounts:
        live_status = get_live_status(acc)
        if acc.get("status") != live_status:
            acc["status"] = live_status
            updated = True
    if updated:
        save_accounts(accounts)

    if category:
        filtered = [acc for acc in accounts if acc.get("category") == category]
        return filtered
    return accounts

@app.post("/api/accounts")
def create_account(payload: AccountCreate):
    accounts = load_accounts()
    new_id = f"acc-{int(time.time() * 1000)}"
    new_account = {
        "id": new_id,
        "category": payload.category,
        "uid": payload.uid,
        "password": payload.password,
        "name": payload.name or f"Bot-{payload.uid}",
        "created_at": int(time.time()),
        "status": "STOPPED"
    }
    accounts.append(new_account)
    save_accounts(accounts)

    if payload.auto_start:
        start_worker(new_id)

    return {"success": True, "account": new_account}

@app.delete("/api/accounts/{account_id}")
def delete_account(account_id: str):
    accounts = load_accounts()
    found = None
    for acc in accounts:
        if acc["id"] == account_id:
            found = acc
            break
    if not found:
        raise HTTPException(status_code=404, detail="Account not found")

    stop_worker(account_id)
    accounts = [acc for acc in accounts if acc["id"] != account_id]
    save_accounts(accounts)
    if account_id in process_logs:
        del process_logs[account_id]
    return {"success": True, "message": "Account removed"}

@app.post("/api/accounts/{account_id}/start")
def start_worker_api(account_id: str):
    success, msg = start_worker(account_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

@app.post("/api/accounts/{account_id}/stop")
def stop_worker_api(account_id: str):
    success, msg = stop_worker(account_id)
    return {"success": success, "message": msg}

def start_worker(account_id: str):
    accounts = load_accounts()
    account = next((a for a in accounts if a["id"] == account_id), None)
    if not account:
        return False, "Account not found"

    # Check if already running
    if account_id in active_processes and active_processes[account_id].poll() is None:
        return False, "Process is already running"

    category = account.get("category", "2_level")
    script_file = "level2_worker.py" if category == "2_level" else "level3_worker.py"
    script_path = os.path.join(os.path.dirname(__file__), script_file)

    if not os.path.exists(script_path):
        return False, f"Worker script not found: {script_file}"

    cmd = [
        sys.executable,
        script_path,
        "--uid", str(account["uid"]),
        "--password", str(account["password"]),
        "--name", str(account["name"])
    ]

    append_log(account_id, f"--- Starting {category} process [{script_file}] ---")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(__file__)
        )
        active_processes[account_id] = proc
        log_reader_thread(account_id, proc)

        account["status"] = "RUNNING"
        save_accounts(accounts)
        return True, f"Started worker PID {proc.pid}"
    except Exception as e:
        err_msg = f"Failed to launch worker: {e}"
        append_log(account_id, err_msg)
        account["status"] = "ERROR"
        save_accounts(accounts)
        return False, err_msg

def stop_worker(account_id: str):
    if account_id not in active_processes:
        return True, "Process is not running"

    proc = active_processes[account_id]
    append_log(account_id, "--- Sending termination signal ---")
    try:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)
    except Exception as e:
        append_log(account_id, f"Error during stop: {e}")

    if account_id in active_processes:
        del active_processes[account_id]

    accounts = load_accounts()
    for acc in accounts:
        if acc["id"] == account_id:
            acc["status"] = "STOPPED"
            break
    save_accounts(accounts)
    append_log(account_id, "--- Process stopped successfully ---")
    return True, "Worker stopped"

@app.get("/api/accounts/{account_id}/logs")
def get_logs(account_id: str):
    logs = process_logs.get(account_id, ["No logs recorded yet."])
    return {"account_id": account_id, "logs": logs}

@app.get("/api/stats")
def get_stats():
    accounts = load_accounts()
    total = len(accounts)
    running = sum(1 for a in accounts if get_live_status(a) == "RUNNING")
    l2_count = sum(1 for a in accounts if a.get("category") == "2_level")
    l3_count = sum(1 for a in accounts if a.get("category") == "3_level")
    l2_running = sum(1 for a in accounts if a.get("category") == "2_level" and get_live_status(a) == "RUNNING")
    l3_running = sum(1 for a in accounts if a.get("category") == "3_level" and get_live_status(a) == "RUNNING")

    return {
        "total_accounts": total,
        "running_accounts": running,
        "level_2_total": l2_count,
        "level_2_running": l2_running,
        "level_3_total": l3_count,
        "level_3_running": l3_running,
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }

# Static web files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "PIYASH LEVEL UP Panel API is online. Static UI initializing."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting PIYASH LEVEL UP Web Panel on port {port}...")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
