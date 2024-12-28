# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 23:23:12 2024

@author: user
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx

app = FastAPI()

# Configuration
DYNAMIC_LINK_SERVICE_URL = "http://127.0.0.1:8002"
MAIN_APP_URL = "http://127.0.0.1:8000"

# Templates
templates = Jinja2Templates(directory="templates")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

'''
@app.get("/PayNow/{unique_id}", response_class=HTMLResponse)
async def pay_now(unique_id: str, request: Request):
    # Fetch RTP details from Dynamic Link Service
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DYNAMIC_LINK_SERVICE_URL}/ValidateLink/{unique_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Invalid or expired link")
        rtp_details = response.json()

    # Render payment page
    return templates.TemplateResponse(
        "pay_now.html",
        {
            "request": request,
            "RTPRefNo": rtp_details["RTPRefNo"],
            "unique_id": unique_id
        }
    )
'''

# Modify the pay_now function to include amount, currency, and payer_name in the context for rendering the pay_now.html template. 

@app.get("/PayNow/{unique_id}", response_class=HTMLResponse)
async def pay_now(unique_id: str, request: Request):
    # Fetch RTP details from Dynamic Link Service
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DYNAMIC_LINK_SERVICE_URL}/ValidateLink/{unique_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Invalid or expired link")
        rtp_details = response.json()

    # Example mock data for demo purposes
    # Replace with real data fetching logic
    payment_data = {
        "amount": "100.00",
        "currency": "USD",
        "payer_name": "John Doe",
    }

    # Render the payment page
    return templates.TemplateResponse(
        "pay_now.html",
        {
            "request": request,
            "RTPRefNo": rtp_details["RTPRefNo"],
            "unique_id": unique_id,
            **payment_data,  # Merge payment data into the context
        }
    )

'''
@app.post("/CompletePayment/{unique_id}")
async def complete_payment(unique_id: str):
    # Notify Main App to mark RTP as completed
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MAIN_APP_URL}/CompleteRTP/{unique_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to complete RTP")
        return {"message": "Payment completed successfully"}
'''
# Update the CompletePayment endpoint to render different templates based on the payment status:

'''
@app.post("/CompletePayment/{unique_id}")
async def complete_payment(unique_id: str, request: Request):
    # Notify Main App to mark RTP as completed
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MAIN_APP_URL}/CompleteRTP/{unique_id}")
        if response.status_code == 200:
            # Parse response and render success template
            data = response.json()
            return templates.TemplateResponse(
                "payment_success.html",
                {
                    "request": request,
                    "RTPRefNo": data["RTPRefNo"]
                }
            )
        elif response.status_code == 409:  # Example for already paid
            return templates.TemplateResponse(
                "payment_error.html",
                {
                    "request": request,
                    "error_message": "This invoice has already been paid."
                }
            )
        else:
            # Handle general errors
            return templates.TemplateResponse(
                "payment_error.html",
                {
                    "request": request,
                    "error_message": "Unexpected error occurred. Please try again later."
                }
            )
'''
# Dynamic Data Example

'''
@app.post("/CompletePayment/{unique_id}")
async def complete_payment(unique_id: str, request: Request):
    # Notify Main App to mark RTP as completed
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MAIN_APP_URL}/CompleteRTP/{unique_id}")
        if response.status_code == 200:
            # Example data to populate the invoice
            invoice_data = {
                "company_name": "Involink",
                "invoice_number": "947-C",
                "po_number": "166B",
                "invoice_date": "Nov 6, 2024",
                "due_date": "Nov 16, 2024",
                "balance_due": "R555.00",
                "logo_url": "https://cdn1.site-media.eu/images/0/11998013/Diagonal-B-transparent.png",
                "client_name": "Kokash Electro-Gadgets",
                "client_address": "Aya St, 10A",
                "client_city": "Amman, Abdoun 11213",
                "client_country": "Jordan",
                "client_email": "demo@involink.io",
                "items": [
                    {"name": "Website Analysis", "description": "Trend and data analysis", "unit_cost": "50.00", "quantity": 1, "line_total": "R50.00"},
                    {"name": "Website Maintenance", "description": "Content page SEO tracking", "unit_cost": "35.00", "quantity": 8, "line_total": "R280.00"},
                ],
                "subtotal": "R330.00",
                "discount": "R0.00",
            }
            return templates.TemplateResponse("invoice_success.html", {"request": request, **invoice_data})
        else:
            # Handle errors as before
            pass
'''

'''
@app.post("/CompletePayment/{unique_id}")
async def complete_payment(unique_id: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://127.0.0.1:8000/CompleteRTP/{unique_id}")
        if response.status_code == 200:
            # Example data for rendering the invoice template
            invoice_data = {
                "company_name": "Involink",
                "invoice_number": "947-C",
                "po_number": "166B",
                "invoice_date": "Dec 7, 2024",
                "due_date": "Dec 14, 2024",
                "balance_due": "R555.00",
                "logo_url": "https://cdn1.site-media.eu/images/0/11998013/Diagonal-B-transparent.png",
                "client_name": "Kokash Electro-Gadgets",
                "client_address": "Aya St, 10A",
                "client_city": "Amman, Abdoun 11213",
                "client_country": "Jordan",
                "client_email": "demo@involink.io",
                "items": [
                    {"name": "Website Analysis", "description": "Trend and data analysis", "unit_cost": "50.00", "quantity": 1, "line_total": "R50.00"},
                    {"name": "Website Maintenance", "description": "Content page SEO tracking", "unit_cost": "35.00", "quantity": 8, "line_total": "R280.00"},
                ],
                "subtotal": "R330.00",
                "discount": "R0.00",
            }
            return templates.TemplateResponse("invoice_success.html", {"request": request, **invoice_data})
        elif response.status_code == 409:  # Already paid case
            return templates.TemplateResponse(
                "payment_error.html",
                {"request": request, "error_message": "This invoice has already been paid."}
            )
        else:
            return templates.TemplateResponse(
                "payment_error.html",
                {"request": request, "error_message": "An unexpected error occurred. Please try again later."}
            )
'''

'''
@app.post("/CompletePayment/{unique_id}")
async def complete_payment(unique_id: str, request: Request):
    # Notify Main App to mark RTP as completed
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MAIN_APP_URL}/CompleteRTP/{unique_id}")
        if response.status_code == 200:
            # Payment successful
            return {
                "status": "success",
                "invoice_url": f"/ViewInvoice/{unique_id}"  # Provide a URL to view the invoice
            }
        elif response.status_code == 409:  # Already completed
            return {
                "status": "completed",
                "message": "This invoice has already been paid.",
                "invoice_url": f"/ViewInvoice/{unique_id}"  # Provide a URL to view the invoice
            }
        else:
            # Handle general errors
            return {"status": "error", "message": "An unexpected error occurred. Please try again later."}

'''
#In the web_app.py, ensure the CompletePayment endpoint correctly identifies and handles the following scenarios:

#Payment Successful
#Already Paid
#General Errors


@app.post("/CompletePayment/{unique_id}")
async def complete_payment(unique_id: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MAIN_APP_URL}/CompleteRTP/{unique_id}")
        
        # Parse the response from the Main App
        if response.status_code == 200:
            return {
                "status": "success",
                "message": "Payment successful!",
                "invoice_url": f"/ViewInvoice/{unique_id}"
            }
        elif response.status_code == 409:  # HTTP 409 Conflict: Already Paid
            return {
                "status": "completed",
                "message": "This invoice has already been paid.",
                "invoice_url": f"/ViewInvoice/{unique_id}"
            }
        else:
            # Catch-all for unexpected errors
            return {
                "status": "error",
                "message": "An unexpected error occurred. Please try again later."
            }


@app.get("/ViewInvoice/{unique_id}", response_class=HTMLResponse)
async def view_invoice(unique_id: str, request: Request):
    # Fetch invoice details (mocked or real)
    invoice_data = {
        "company_name": "Involink",
        "invoice_number": "947-C",
        "po_number": "166B",
        "invoice_date": "Dec 7, 2024",
        "due_date": "Dec 14, 2024",
        "balance_due": "R0.00",  # Balance is zero after payment
        "logo_url": "https://cdn1.site-media.eu/images/0/11998013/Diagonal-B-transparent.png",
        "client_name": "Kokash Electro-Gadgets",
        "client_address": "Aya St, 10A",
        "client_city": "Amman, Abdoun 11213",
        "client_country": "Jordan",
        "client_email": "demo@involink.io",
        "items": [
            {"name": "Website Analysis", "description": "Trend and data analysis", "unit_cost": "50.00", "quantity": 1, "line_total": "R50.00"},
            {"name": "Website Maintenance", "description": "Content page SEO tracking", "unit_cost": "35.00", "quantity": 8, "line_total": "R280.00"},
        ],
        "subtotal": "R330.00",
        "discount": "R0.00",
    }

    # Render the invoice template
    return templates.TemplateResponse("invoice_success.html", {"request": request, **invoice_data})
        