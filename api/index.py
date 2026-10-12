"""Small queue API for the bank demo. State is held in memory for the MVP."""
from collections import deque
from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Banco Norte · API de turnos")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

lock = Lock()
waiting: deque[int] = deque()
desks: dict[int, int | None] = {number: None for number in range(1, 5)}
next_ticket = 1
last_called: tuple[int, int] | None = None


def snapshot() -> dict:
    return {
        "desks": [{"id": number, "current": ticket} for number, ticket in desks.items()],
        "waiting": list(waiting),
        "next": next_ticket,
        "lastCalled": {"ticket": last_called[0], "desk": last_called[1]} if last_called else None,
    }


@app.get("/api/state")
@app.get("/state")
def get_state():
    with lock:
        return snapshot()


@app.post("/api/tickets")
@app.post("/tickets")
def create_ticket():
    global next_ticket, last_called
    with lock:
        ticket = next_ticket
        next_ticket += 1
        free_desk = next((number for number, current in desks.items() if current is None), None)
        if free_desk is not None:
            desks[free_desk] = ticket
            last_called = (ticket, free_desk)
        else:
            waiting.append(ticket)
        return {"ticket": ticket, "desk": free_desk, "queued": free_desk is None, "state": snapshot()}


@app.post("/api/desks/{desk_id}/finish")
@app.post("/desks/{desk_id}/finish")
def finish_service(desk_id: int):
    global last_called
    with lock:
        if desk_id not in desks:
            raise HTTPException(status_code=404, detail="Mesa no encontrada")
        if desks[desk_id] is None:
            raise HTTPException(status_code=409, detail="La mesa ya está disponible")
        desks[desk_id] = waiting.popleft() if waiting else None
        ticket = desks[desk_id]
        if ticket is not None:
            last_called = (ticket, desk_id)
        return {"ticket": ticket, "desk": desk_id, "state": snapshot()}


@app.post("/api/reset")
@app.post("/reset")
def reset():
    global next_ticket, last_called
    with lock:
        waiting.clear()
        for number in desks:
            desks[number] = None
        next_ticket = 1
        last_called = None
        return snapshot()
