'''
Created on Aug 7, 2019

@author: nballas
@about: REST interface to the asyncio_sccp phone
to run: uvicorn http_sccp_controller:app --reload
'''

import asyncio
from fastapi import FastAPI
from asyncio_sccp import register_phone, place_call, hangup_call
from asyncio_sccp import get_received_phone_events, get_phone_status, get_phone_states
from starlette.responses import Response, JSONResponse
from sccpphone_errors import DeviceAlreadyRegistered, DeviceNotRegistered
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
app = FastAPI()

@app.post("/dial/{extension}")
async def dial(extension: int, response: Response):
    try:
        await place_call(extension)
    except DeviceNotRegistered as error:
        response.status_code = HTTP_404_NOT_FOUND
        return error.message

@app.post("/register/{host}/{port}/{device_name}")
async def register(host: str, port: int, device_name: str, response: Response):
    loop = asyncio.get_event_loop()
    try:
        await register_phone(host, port, device_name, loop)
    except DeviceAlreadyRegistered as error:
        response.status_code = HTTP_409_CONFLICT
        return error.message


@app.get("/history")
async def history():
    events = asyncio.Future()
    await get_received_phone_events(events)
    states = asyncio.Future()
    await get_phone_states(states)
    return {"events": events.result(), "callStates": states.result()}

@app.post("/hangup")
async def hangup():
    await hangup_call()

@app.get("/status")
async def status():
    status = asyncio.Future()
    await get_phone_status(status)
    return {"callInProgress": status.result()}

@app.post("/answer")
async def answer():
    return {"Hey": "What's up?"}
