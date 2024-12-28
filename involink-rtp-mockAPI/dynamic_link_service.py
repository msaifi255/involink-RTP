# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException
import uuid

app = FastAPI()

# In-memory database for dynamic links
dynamic_links = {}

@app.post("/CreateLink")
async def create_link(data: dict):
    rtp_ref_no = data.get("RTPRefNo")
    if not rtp_ref_no:
        raise HTTPException(status_code=400, detail="RTPRefNo is required")

    # Generate a unique ID for the dynamic link
    unique_id = str(uuid.uuid4())
    pay_now_link = f"https://dynamic-link-service.com/PayNow/{unique_id}"

    # Store the mapping of unique_id to RTPRefNo
    dynamic_links[unique_id] = {"RTPRefNo": rtp_ref_no, "Status": "Pending"}

    return {"PayNowLink": pay_now_link}

@app.get("/ValidateLink/{unique_id}")
async def validate_link(unique_id: str):
    if unique_id not in dynamic_links:
        raise HTTPException(status_code=404, detail="Invalid or expired link")

    # Retrieve the RTPRefNo associated with the unique_id
    rtp_ref_no = dynamic_links[unique_id]["RTPRefNo"]
    return {"RTPRefNo": rtp_ref_no}

@app.post("/Complete/{unique_id}")
async def complete_link(unique_id: str):
    if unique_id not in dynamic_links:
        raise HTTPException(status_code=404, detail="Invalid or expired link")

    # Mark the RTP as completed
    dynamic_links[unique_id]["Status"] = "Completed"
    rtp_ref_no = dynamic_links[unique_id]["RTPRefNo"]

    return {"RTPRefNo": rtp_ref_no, "Status": "Completed"}