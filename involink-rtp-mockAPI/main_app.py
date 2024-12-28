# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 22:50:48 2024

@author: user
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from xml.etree import ElementTree
import httpx

app = FastAPI()

# Configuration
MOCK_API_URL = "http://127.0.0.1:8001"
DYNAMIC_LINK_SERVICE_URL = "http://127.0.0.1:8002"


@app.post("/CreateRTP")
async def create_rtp(rtp_details: dict):
    # Step 1: Send RTP creation request to Mock API
    async with httpx.AsyncClient() as client:
        mock_api_response = await client.post(f"{MOCK_API_URL}/api/v1/RequestToPay", json=rtp_details)
        if mock_api_response.status_code != 200:
            raise HTTPException(status_code=mock_api_response.status_code, detail="Failed to create RTP in Mock API")
        rtp_data = mock_api_response.json()
        rtp_ref_no = rtp_data["RTPRefNo"]

    # Step 2: Request dynamic link from Dynamic Link Service
    async with httpx.AsyncClient() as client:
        link_response = await client.post(f"{DYNAMIC_LINK_SERVICE_URL}/CreateLink", json={"RTPRefNo": rtp_ref_no})
        if link_response.status_code != 200:
            raise HTTPException(status_code=link_response.status_code, detail="Failed to generate dynamic link")
        dynamic_link = link_response.json()["PayNowLink"]

    # Step 3: Return RTPRefNo and dynamic link
    return {
        "RTPRefNo": rtp_ref_no,
        "PayNowLink": dynamic_link
    }




'''
@app.get("/CheckStatus/{RTPRefNo}")
async def check_status(rtp_ref_no: str):
    # Fetch RTP status from Mock API
    async with httpx.AsyncClient() as client:
        status_response = await client.get(f"{MOCK_API_URL}/api/v1/RequestToPay/{rtp_ref_no}/Status")
        if status_response.status_code != 200:
            raise HTTPException(status_code=status_response.status_code, detail="Failed to fetch RTP status")
        return status_response.json()
'''

#Fixing the CheckStatus to Update the CheckStatus function in the Main App to properly handle RTPRefNo as a path parameter:
    
@app.get("/CheckStatus/{RTPRefNo}")
async def check_status(RTPRefNo: str):
    async with httpx.AsyncClient() as client:
        status_response = await client.get(f"{MOCK_API_URL}/api/v1/RequestToPay/{RTPRefNo}/Status")
        if status_response.status_code != 200:
            raise HTTPException(
                status_code=status_response.status_code,
                detail=f"Failed to fetch RTP status: {status_response.text}"
            )

        # Parse the XML response
        try:
            root = ElementTree.fromstring(status_response.text)
            namespace = {"ns": "urn:iso:std:iso:20022:tech:xsd:pain.002.001.07"}

            # Extract necessary fields
            msg_id = root.find(".//ns:MsgId", namespace).text
            grp_sts = root.find(".//ns:GrpSts", namespace).text

            # Return as JSON response
            return JSONResponse(content={"RTPRefNo": msg_id, "Status": grp_sts})
        except ElementTree.ParseError:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse XML response from Mock API"
            )


'''
@app.post("/CompleteRTP/{unique_id}")
async def complete_rtp(unique_id: str):
    # Validate the dynamic link
    async with httpx.AsyncClient() as client:
        validate_response = await client.get(f"{DYNAMIC_LINK_SERVICE_URL}/ValidateLink/{unique_id}")
        if validate_response.status_code != 200:
            raise HTTPException(status_code=validate_response.status_code, detail="Invalid or expired link")
        rtp_ref_no = validate_response.json()["RTPRefNo"]

    # Mark RTP as completed in Mock API
    async with httpx.AsyncClient() as client:
        complete_response = await client.post(f"{MOCK_API_URL}/api/v1/RequestToPay/{rtp_ref_no}/Complete")
        if complete_response.status_code != 200:
            raise HTTPException(status_code=complete_response.status_code, detail="Failed to complete RTP")
        return complete_response.json()
'''

'''
@app.post("/CompleteRTP/{unique_id}")
async def complete_rtp(unique_id: str):
    # Validate the dynamic link
    async with httpx.AsyncClient() as client:
        validate_response = await client.get(f"{DYNAMIC_LINK_SERVICE_URL}/ValidateLink/{unique_id}")
        if validate_response.status_code != 200:
            raise HTTPException(status_code=validate_response.status_code, detail="Invalid or expired link")
        rtp_ref_no = validate_response.json()["RTPRefNo"]

    # Mark RTP as completed in Mock API
    async with httpx.AsyncClient() as client:
        complete_response = await client.post(f"{MOCK_API_URL}/api/v1/RequestToPay/{rtp_ref_no}/Complete")
        if complete_response.status_code != 200:
            raise HTTPException(
                status_code=complete_response.status_code,
                detail=f"Failed to complete RTP: {complete_response.text}"
            )

        # Parse the XML response
        try:
            root = ElementTree.fromstring(complete_response.text)
            namespace = {"ns": "urn:iso:std:iso:20022:tech:xsd:pain.002.001.07"}

            # Extract necessary fields
            msg_id = root.find(".//ns:MsgId", namespace).text
            grp_sts = root.find(".//ns:GrpSts", namespace).text

            # Return as JSON response
            return {"RTPRefNo": msg_id, "Status": grp_sts}
        except ElementTree.ParseError:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse XML response from Mock API"
            )
'''

#Update the /CompleteRTP endpoint to handle already paid invoices.

@app.post("/CompleteRTP/{unique_id}")
async def complete_rtp(unique_id: str):
    # Validate the dynamic link
    async with httpx.AsyncClient() as client:
        validate_response = await client.get(f"{DYNAMIC_LINK_SERVICE_URL}/ValidateLink/{unique_id}")
        if validate_response.status_code != 200:
            raise HTTPException(status_code=404, detail="Invalid or expired link")
        rtp_ref_no = validate_response.json()["RTPRefNo"]

    # Check if the RTP is already completed in the Mock API
    async with httpx.AsyncClient() as client:
        status_response = await client.get(f"{MOCK_API_URL}/api/v1/RequestToPay/{rtp_ref_no}/Status")
        if status_response.status_code != 200:
            raise HTTPException(status_code=status_response.status_code, detail="Failed to fetch RTP status")

        # Parse the XML response
        root = ElementTree.fromstring(status_response.text)
        namespace = {"ns": "urn:iso:std:iso:20022:tech:xsd:pain.002.001.07"}
        grp_sts = root.find(".//ns:GrpSts", namespace).text

        if grp_sts == "Completed":  # Already paid
            return JSONResponse(
                content={
                    "status": "completed",
                    "message": "This invoice has already been paid.",
                    "invoice_url": f"/ViewInvoice/{unique_id}"
                },
                status_code=409
            )

    # Mark RTP as completed
    async with httpx.AsyncClient() as client:
        complete_response = await client.post(f"{MOCK_API_URL}/api/v1/RequestToPay/{rtp_ref_no}/Complete")
        if complete_response.status_code != 200:
            raise HTTPException(
                status_code=complete_response.status_code,
                detail="Failed to complete RTP"
            )

    # Successful completion
    return {
        "status": "success",
        "message": "Payment successful!",
        "invoice_url": f"/ViewInvoice/{unique_id}"
    }