import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# ============================================================
# 1. Path to your bot script and Python virtual environment
# ============================================================
BOT_FILE = "/home/test/Desktop/callbotic_bot/main.py"
VENV_PYTHON = "/home/test/Desktop/callbotic_bot/venv/bin/python"


# ============================================================
# 2. ASYNC FUNCTION TO RUN BOT WITH LIVE LOG
# ============================================================
async def run_bot():
    """
    Runs the bot inside the virtual environment asynchronously.
    Captures stdout, stderr, return code, and prints logs to console live.
    """
    process = await asyncio.create_subprocess_exec(
        VENV_PYTHON, BOT_FILE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout_lines = []
    stderr_lines = []

    # Read stdout and stderr concurrently
    async def read_stream(stream, container, prefix=""):
        while True:
            line = await stream.readline()
            if not line:
                break
            text = line.decode("utf-8").rstrip()
            print(f"{prefix}{text}")  # Print live to console
            container.append(text)

    await asyncio.gather(
        read_stream(process.stdout, stdout_lines, prefix="[BOT STDOUT] "),
        read_stream(process.stderr, stderr_lines, prefix="[BOT STDERR] ")
    )

    return "".join([line + "\n" for line in stdout_lines]), "".join([line + "\n" for line in stderr_lines]), await process.wait()


# ============================================================
# 3. API ENDPOINT TO RUN BOT
# ============================================================
@app.get("/run-bot")
async def execute_bot():
    """
    Run the bot when called remotely.
    """
    try:
        stdout, stderr, code = await run_bot()
        return JSONResponse(content={
            "status": "completed" if code == 0 else "error",
            "exit_code": code,
            "stdout": stdout,
            "stderr": stderr
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e)
        })


# ============================================================
# 4. HEALTH CHECK ENDPOINT
# ============================================================
@app.get("/ping")
async def ping():
    return {"message": "Agent running!"}

# ============================================================
# 5. RUNNING THE AGENT
# ============================================================
# Run via terminal:
# uvicorn agent:app --host 0.0.0.0 --port 9000
# ============================================================
