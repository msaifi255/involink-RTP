# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from lxml import etree
from datetime import datetime

app = FastAPI()

# Mock Database
mock_db = {}

# Helper Functions
def get_timestamp():
    return datetime.utcnow().isoformat() + "Z"

def generate_pain001_xml(payload):
    """
    Generate ISO20022-compliant XML for pain.001 (Credit Transfer Request).
    """
    nsmap = {None: "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"}
    root = etree.Element("Document", nsmap=nsmap)

    cdt_trf = etree.SubElement(root, "CstmrCdtTrfInitn")
    grp_hdr = etree.SubElement(cdt_trf, "GrpHdr")
    etree.SubElement(grp_hdr, "MsgId").text = payload.get("ReferenceID", "Unknown")
    etree.SubElement(grp_hdr, "CreDtTm").text = get_timestamp()

    # Payment Information
    pmt_inf = etree.SubElement(cdt_trf, "PmtInf")
    etree.SubElement(pmt_inf, "PmtInfId").text = payload.get("ReferenceID", "Unknown")
    etree.SubElement(pmt_inf, "PmtMtd").text = "TRF"
    etree.SubElement(pmt_inf, "ReqdExctnDt").text = datetime.utcnow().date().isoformat()

    # Debtor Information
    dbtr = etree.SubElement(pmt_inf, "Dbtr")
    etree.SubElement(dbtr, "Nm").text = payload["PayerDetails"]["PayerName"]
    dbtr_acct = etree.SubElement(dbtr, "DbtrAcct")
    dbtr_id = etree.SubElement(dbtr_acct, "Id")
    etree.SubElement(dbtr_id, "IBAN").text = payload["PayerDetails"]["PayerAccount"]

    # Creditor Information
    cdtr = etree.SubElement(pmt_inf, "Cdtr")
    etree.SubElement(cdtr, "Nm").text = "Merchant"
    cdtr_acct = etree.SubElement(cdtr, "CdtrAcct")
    cdtr_id = etree.SubElement(cdtr_acct, "Id")
    etree.SubElement(cdtr_id, "IBAN").text = "IBAN987654321"

    # Transaction Amount
    amt = etree.SubElement(pmt_inf, "Amt")
    etree.SubElement(amt, "InstdAmt", Ccy=payload["Currency"]).text = str(payload["Amount"])

    # Remittance Information
    rmt_inf = etree.SubElement(pmt_inf, "RmtInf")
    etree.SubElement(rmt_inf, "Ustrd").text = payload.get("ReferenceID", "Unknown")

    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")


# API Endpoints

'''
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

    # Generate pain.001-compliant XML
    xml_response = generate_pain001_xml(payload)

    return Response(content=xml_response, media_type="application/xml")
'''

# Modified to return the RTPRefNo 
@app.post("/api/v1/RequestToPay")
async def create_request_to_pay(payload: dict):
    rtp_ref_no = f"RTP-{len(mock_db) + 1:03}"  # Generate a unique RTP reference number
    timestamp = get_timestamp()

    # Store request in mock database
    mock_db[rtp_ref_no] = {
        "Payload": payload,
        "Status": "Initiated",
        "Timestamp": timestamp
    }

    # Generate pain.001-compliant XML
    xml_response = generate_pain001_xml(payload)

    # Return both RTPRefNo and XML response
    return JSONResponse(
        content={
            "RTPRefNo": rtp_ref_no,
            "XMLMessage": xml_response.decode("utf-8")  # Decode XML bytes to string
        },
        media_type="application/json"
    )

'''
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
            <OrgnlMsgNmId>pain.001.001.03</OrgnlMsgNmId>
            <GrpSts>{status}</GrpSts>
        </OrgnlGrpInfAndSts>
    </CdtPmtStsRpt>
    </Document>"""
    return Response(content=response, media_type="application/xml")
'''

# Modified to return correct status
@app.get("/api/v1/RequestToPay/{RTPRefNo}/Status", response_class=Response)
async def check_rtp_status(RTPRefNo: str):
    if RTPRefNo not in mock_db:
        raise HTTPException(status_code=404, detail="RTP reference not found")

    status = mock_db[RTPRefNo]["Status"]
    response = f"""<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.002.001.07">
    <CdtPmtStsRpt>
        <GrpHdr>
            <MsgId>{RTPRefNo}</MsgId>
            <CreDtTm>{get_timestamp()}</CreDtTm>
        </GrpHdr>
        <OrgnlGrpInfAndSts>
            <OrgnlMsgId>{RTPRefNo}</OrgnlMsgId>
            <OrgnlMsgNmId>pain.001.001.03</OrgnlMsgNmId>
            <GrpSts>{status}</GrpSts>
        </OrgnlGrpInfAndSts>
    </CdtPmtStsRpt>
    </Document>"""
    return Response(content=response, media_type="application/xml")

'''
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
            <OrgnlMsgNmId>pain.001.001.03</OrgnlMsgNmId>
            <GrpSts>Completed</GrpSts>
        </OrgnlGrpInfAndSts>
    </CdtPmtStsRpt>
    </Document>"""
    return Response(content=response, media_type="application/xml")
'''

# Modified to interpret RTPRefNo as path Param

@app.post("/api/v1/RequestToPay/{RTPRefNo}/Complete", response_class=Response)
async def complete_rtp(RTPRefNo: str):
    if RTPRefNo not in mock_db:
        raise HTTPException(status_code=404, detail="RTP reference not found")

    # Update the RTP status in the mock database
    mock_db[RTPRefNo]["Status"] = "Completed"
    mock_db[RTPRefNo]["Timestamp"] = get_timestamp()

    # Generate the pain.002-compliant XML response
    response = f"""<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.002.001.07">
    <CdtPmtStsRpt>
        <GrpHdr>
            <MsgId>{RTPRefNo}</MsgId>
            <CreDtTm>{get_timestamp()}</CreDtTm>
        </GrpHdr>
        <OrgnlGrpInfAndSts>
            <OrgnlMsgId>{RTPRefNo}</OrgnlMsgId>
            <OrgnlMsgNmId>pain.001.001.03</OrgnlMsgNmId>
            <GrpSts>Completed</GrpSts>
        </OrgnlGrpInfAndSts>
    </CdtPmtStsRpt>
    </Document>"""
    return Response(content=response, media_type="application/xml")
