# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 02:05:19 2024

@author: user
"""

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from lxml import etree
from datetime import datetime

app = FastAPI()

# Mock Database
mock_db = {}

# Helper Functions
def get_timestamp():
    return datetime.utcnow().isoformat() + "Z"

def generate_iso20022_rtp(payload):
    """
    Generate ISO20022-compliant XML for RTP (pain.013).
    """
    nsmap = {"": "urn:iso:std:iso:20022:tech:xsd:pain.013.001.07"}
    root = etree.Element("Document", nsmap=nsmap)

    cdt_pmt = etree.SubElement(root, "CdtPmtActvtnReq")
    grp_hdr = etree.SubElement(cdt_pmt, "GrpHdr")
    etree.SubElement(grp_hdr, "MsgId").text = payload.get("ReferenceID", "Unknown")
    etree.SubElement(grp_hdr, "CreDtTm").text = get_timestamp()

    pmt_inf = etree.SubElement(cdt_pmt, "PmtInf")
    etree.SubElement(pmt_inf, "PmtInfId").text = payload.get("ReferenceID", "Unknown")
    etree.SubElement(pmt_inf, "PmtMtd").text = "TRF"
    etree.SubElement(pmt_inf, "ReqdExctnDt").text = datetime.utcnow().date().isoformat()

    # Debtor (Payer)
    dbtr = etree.SubElement(pmt_inf, "Dbtr")
    etree.SubElement(dbtr, "Nm").text = payload["PayerDetails"]["PayerName"]
    dbtr_acct = etree.SubElement(dbtr, "Acct")
    etree.SubElement(dbtr_acct, "Id").append(
        etree.Element("IBAN", text=payload["PayerDetails"]["PayerAccount"])
    )

    # Creditor (Receiver)
    cdtr = etree.SubElement(pmt_inf, "Cdtr")
    etree.SubElement(cdtr, "Nm").text = "Merchant"
    cdtr_acct = etree.SubElement(cdtr, "Acct")
    etree.SubElement(cdtr_acct, "Id").append(etree.Element("IBAN", text="IBAN987654321"))

    # Amount and Currency
    amt = etree.SubElement(pmt_inf, "Amt")
    etree.SubElement(amt, "InstdAmt", Ccy=payload["Currency"]).text = str(payload["Amount"])

    # Remittance Information
    rmt_inf = etree.SubElement(pmt_inf, "RmtInf")
    etree.SubElement(rmt_inf, "Ustrd").text = payload.get("ReferenceID", "Unknown")

    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")

# API Endpoints
@app.post("/api/v1/RequestToPay", response_class=Response)
async def create_request_to_pay(payload: dict):
    rtp_ref_no = f"RTP-{len(mock_db) + 1:03}"
    timestamp = get_timestamp()

    # Store request in mock database
    mock_db[rtp_ref_no] = {
        "Payload": payload,
        "Status": "Initiated",
        "Timestamp": timestamp
    }

    # Generate ISO20022-compliant XML
    xml_response = generate_iso20022_rtp(payload)

    return Response(content=xml_response, media_type="application/xml")

@app.get("/api/v1/RequestToPay/{RTPRefNo}/Status", response_class=Response)
async def check_rtp_status(rtp_ref_no: str):
    if rtp_ref_no not in mock_db:
        raise HTTPException(status_code=404, detail="RTP reference not found")

    status = mock_db[rtp_ref_no]["Status"]
    response = f"""<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.002.001.07">
    <CdtPmtStsRpt>
        <GrpHdr>
            <MsgId>{rtp_ref_no}</MsgId>
            <CreDtTm>{get_timestamp()}</CreDtTm>
        </GrpHdr>
        <OrgnlGrpInfAndSts>
            <OrgnlMsgId>{rtp_ref_no}</OrgnlMsgId>
            <OrgnlMsgNmId>pain.013.001.07</OrgnlMsgNmId>
            <GrpSts>{status}</GrpSts>
        </OrgnlGrpInfAndSts>
    </CdtPmtStsRpt>
    </Document>"""
    return Response(content=response, media_type="application/xml")

@app.post("/api/v1/RequestToPay/{RTPRefNo}/Complete", response_class=Response)
async def complete_rtp(rtp_ref_no: str):
    if rtp_ref_no not in mock_db:
        raise HTTPException(status_code=404, detail="RTP reference not found")

    mock_db[rtp_ref_no]["Status"] = "Completed"
    mock_db[rtp_ref_no]["Timestamp"] = get_timestamp()

    response = f"""<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.002.001.07">
    <CdtPmtStsRpt>
        <GrpHdr>
            <MsgId>{rtp_ref_no}</MsgId>
            <CreDtTm>{get_timestamp()}</CreDtTm>
        </GrpHdr>
        <OrgnlGrpInfAndSts>
            <OrgnlMsgId>{rtp_ref_no}</OrgnlMsgId>
            <OrgnlMsgNmId>pain.013.001.07</OrgnlMsgNmId>
            <GrpSts>Completed</GrpSts>
        </OrgnlGrpInfAndSts>
    </CdtPmtStsRpt>
    </Document>"""
    return Response(content=response, media_type="application/xml")
