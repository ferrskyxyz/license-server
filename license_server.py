from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import sqlite3, time

app = FastAPI()

CLIENT_SECRET = "Ferrskyxyz2025"  # ← GANTI, bebas
DB = "license.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS licenses(
            license_key TEXT PRIMARY KEY,
            device_id TEXT
        )
    """)
    return conn

class Check(BaseModel):
    license_key: str
    device_id: str

@app.post("/checkin")
def checkin(data: Check, x_client_secret: str = Header("")):
    if x_client_secret != CLIENT_SECRET:
        raise HTTPException(401, "Unauthorized")

    conn = get_db()
    cur = conn.execute(
        "SELECT device_id FROM licenses WHERE license_key=?",
        (data.license_key,)
    )
    row = cur.fetchone()

    if row is None:
        # pertama kali → ikat device
        conn.execute(
            "INSERT INTO licenses VALUES (?, ?)",
            (data.license_key, data.device_id)
        )
        conn.commit()
        return {"status": "registered"}

    if row[0] != data.device_id:
        raise HTTPException(403, "License used on another device")

    return {"status": "ok"}
