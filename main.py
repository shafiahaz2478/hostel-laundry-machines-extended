from urllib import response

from fastapi import FastAPI, HTTPException, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import functions

class Machine(BaseModel):
    name: str
    block: str
    kind: str
    cycle_minutes: int

class User(BaseModel):
    username: str
    password : str
    user_type: str
app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=["http://localhost:5173"],
                   allow_methods=["*"],
                   allow_headers=["*"])


@app.patch("/collect/{machine_id}")
def collect(machine_id: str,token = Header(None)):
    payloads = functions.verify_token(token, "access")
    if not payloads:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payloads["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Not Allowed")

    response = functions.collect_cloth(machine_id, payloads["user_id"])
    code = response["code"]
    if code == 200:
        return response["run"]
    raise HTTPException(code, detail=response["msg"])


@app.patch("/clear/{machine_id}")
def clear(machine_id: str, token = Header(None)):
    payloads = functions.verify_token(token, "access")
    if not payloads:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    response = functions.clear_machine(machine_id, payloads["user_id"])
    code = response["code"]
    if code == 200:
        return response["run"]
    raise HTTPException(code, detail=response["msg"])

@app.get("/runs/{roll_no}")
def running_run(token = Header(None)):
    payloads = functions.verify_token(token, "access")
    if not payloads:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payloads["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Not Allowed")
    response = functions.get_running_runs(payloads["user_id"])
    code = response["code"]
    if code == 200:
        return response["runs"]
    raise HTTPException(code, detail=response["msg"])

@app.get("/machines/{id}")
def get_machine_by_id(id: int,token = Header(None)): #E2
    payloads = functions.verify_token(token, "access")
    if not payloads:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


    response = functions.get_machine_by_id(id=id)
    code = response["code"]
    if code == 200:
        return response["machine"]
    raise HTTPException(code, detail=response["msg"])

@app.post("/machines")
def add_machine(machine:Machine,token = Header(None)): #E3
    payloads = functions.verify_token(token, "access")
    if not payloads:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payloads["user_type"] != "staff":
        raise HTTPException(status_code=403, detail="Not Allowed")
    response = functions.add_a_machine(machine.name, machine.block, machine.kind, machine.cycle_minutes)
    code = response["code"]
    if code == 200:
        return response["machine"]
    raise HTTPException(code,detail=response["msg"])

@app.get("/machines")
def get_all_machines(block=None,kind=None,token = Header(None)): #E1
    payloads = functions.verify_token(token, "access")
    if not payloads:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if block not in ["a","b","c","d", None]:
        raise HTTPException(status_code=422, detail="Invalid block")
    if kind not in ["washer","dryer",None]:
        raise HTTPException(status_code=422, detail="Invalid kind of machine")
    response = functions.get_all_machines(block=block, kind=kind)
    return response

@app.get("/attention")
def get_machines_needing_attention(token = Header(None)): #E9
    payloads = functions.verify_token(token, "access")
    if not payloads:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payloads["user_type"] != "staff":
        raise HTTPException(status_code=403, detail="Not Allowed")
    response = functions.get_machines_that_need_attention()
    return response

@app.post("/runs/{machine_id}")
def starting(machine_id,roll_no,token = Header(None)):
    payloads = functions.verify_token(token, "access")
    if not payloads:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    response = functions.start_machine(machine_id=machine_id, roll_no=roll_no)
    code = response["code"]
    if code == 200:
        return response["run"]
    raise HTTPException(code, detail=response["msg"])
@app.get("/usage")
def usage(token = Header(None)):
    payloads = functions.verify_token(token, "access")
    if not payloads:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payloads["user_type"] != "staff":
        raise HTTPException(status_code=403, detail="Not Allowed")
    response = functions.get_today_usage()
    code = response["code"]
    if code == 200:
        return response["usage"]
    raise HTTPException(code, detail=response["msg"])

@app.patch("/service/{machine_id}")
def changeservice(machine_id: str, in_service: int,token = Header(None)):
    payloads = functions.verify_token(token, "access")
    if not payloads:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payloads["user_type"] != "staff":
        raise HTTPException(status_code=403, detail="Not Allowed")
    response = functions.change_service(machine_id, in_service)
    code = response["code"]
    if code == 200:
        return response["machine"]

    raise HTTPException(code, detail=response["msg"])


@app.post("/login")
def login(username = Body() , password = Body()):
    response = functions.verify_login(username, password)
    if response["code"] == 200:
        return response["tokens"]
    raise HTTPException(status_code=response["code"], detail=response["msg"])

@app.post("/refresh")
def refresh(token= Header(None)):
    username = functions.verify_token(token , "refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"access_token": functions.create_token(username,"access")}

@app.post("/register")
def register(user : User):
    response =functions.register_user(user.username , user.password , user.user_type)
    if response["code"] == 200:
        return response["msg"]
    raise HTTPException(status_code=response["code"] , detail=response["msg"])