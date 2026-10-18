import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any

SYNTHETIC_RECEIPTS: List[Dict[str, Any]] = [
    {
        "source_filename": "aws-cloud-invoice-sep2026.pdf",
        "mime_type": "application/pdf",
        "raw_ocr_text": """Amazon Web Services, Inc.
P.O. Box 84023, Seattle, WA 98124-8423
INVOICE: #INV-98231019
Invoice Date: September 28, 2026
Account: Freelance Cloud Dev
Description: EC2, S3, Route 53 Web App Infrastructure
Subtotal: $42.18
Tax (0.00%): $0.00
TOTAL AMOUNT DUE: $42.18
Payment: Visa ending in 4102""",
        "expected": {
            "merchant": "Amazon Web Services",
            "document_type": "invoice",
            "invoice_number": "INV-98231019",
            "transaction_date": "2026-09-28",
            "currency": "USD",
            "subtotal": 42.18,
            "tax": 0.0,
            "total": 42.18,
            "category": "Software & SaaS",
            "payment_method": "Visa 4102",
            "reconciliation_status": "reconciled"
        }
    },
    {
        "source_filename": "starbucks-client-meeting.png",
        "mime_type": "image/png",
        "raw_ocr_text": """STARBUCKS STORE #10842
100 MARKET ST, SAN FRANCISCO, CA
10/02/2026  03:45 PM
1 Caffe Latte Grande      $5.25
1 Caramel Macchiato       $5.75
1 Blueberry Muffin        $2.50
SUBTOTAL:                $13.50
TAX 10%:                  $1.35
TOTAL:                   $14.85
Mastercard ****9921
Thank you for visiting!""",
        "expected": {
            "merchant": "Starbucks",
            "document_type": "receipt",
            "invoice_number": None,
            "transaction_date": "2026-10-02",
            "currency": "USD",
            "subtotal": 13.50,
            "tax": 1.35,
            "total": 14.85,
            "category": "Meals & Entertainment",
            "payment_method": "Mastercard 9921",
            "reconciliation_status": "reconciled"
        }
    },
    {
        "source_filename": "github-pro-subscription.pdf",
        "mime_type": "application/pdf",
        "raw_ocr_text": """GitHub, Inc.
88 Colin P Kelly Jr St, San Francisco, CA 94107
Receipt #GH-2026-88192
Date: 2026-08-15
Billed To: jane.developer@freelance.io
Item: GitHub Pro - Annual Developer Subscription
Subtotal: $48.00
Tax: $0.00
Total Paid: $48.00
Paid via PayPal""",
        "expected": {
            "merchant": "GitHub",
            "document_type": "receipt",
            "invoice_number": "GH-2026-88192",
            "transaction_date": "2026-08-15",
            "currency": "USD",
            "subtotal": 48.00,
            "tax": 0.0,
            "total": 48.00,
            "category": "Software & SaaS",
            "payment_method": "PayPal",
            "reconciliation_status": "reconciled"
        }
    },
    {
        "source_filename": "staples-design-sketchbooks.jpg",
        "mime_type": "image/jpeg",
        "raw_ocr_text": """STAPLES THE OFFICE SUPERSTORE
Store #0412
Date: 09/19/2026
Order #ST-99120
2x Moleskine Dot Grid Notebooks   $24.00
1x Micron Fineliner Pen Set 6pk    $6.00
SUBTOTAL:                         $30.00
SALES TAX (8%):                    $2.40
TOTAL:                            $32.40
CASH TENDERED:                    $40.00
CHANGE:                            $7.60""",
        "expected": {
            "merchant": "Staples",
            "document_type": "receipt",
            "invoice_number": "ST-99120",
            "transaction_date": "2026-09-19",
            "currency": "USD",
            "subtotal": 30.00,
            "tax": 2.40,
            "total": 32.40,
            "category": "Office Supplies",
            "payment_method": "Cash",
            "reconciliation_status": "reconciled"
        }
    },
    {
        "source_filename": "hetzner-cloud-europe.pdf",
        "mime_type": "application/pdf",
        "raw_ocr_text": """Hetzner Online GmbH
Industriestr. 25, 91710 Gunzenhausen, Germany
Rechnung / Invoice No. R00192849
Datum / Date: 01.10.2026
Server CPX31 Cloud Instance
Net Amount / Subtotal: €46.00
19% VAT: €8.74
Total Amount: €54.74
Status: Paid by SEPA Direct Debit""",
        "expected": {
            "merchant": "Hetzner Online",
            "document_type": "invoice",
            "invoice_number": "R00192849",
            "transaction_date": "2026-10-01",
            "currency": "EUR",
            "subtotal": 46.00,
            "tax": 8.74,
            "total": 54.74,
            "category": "Software & SaaS",
            "payment_method": "SEPA",
            "reconciliation_status": "reconciled"
        }
    },
    {
        "source_filename": "heathrow-express-transit.png",
        "mime_type": "image/png",
        "raw_ocr_text": """Heathrow Express
Paddington Station, London, UK
Booking Ref: HEX-440192
Date of Travel: 24/09/2026
Standard Single Ticket: £25.00
VAT (0%): £0.00
Total Paid: £25.00
Apple Pay (Visa 8812)""",
        "expected": {
            "merchant": "Heathrow Express",
            "document_type": "receipt",
            "invoice_number": "HEX-440192",
            "transaction_date": "2026-09-24",
            "currency": "GBP",
            "subtotal": 25.00,
            "tax": 0.0,
            "total": 25.00,
            "category": "Travel & Lodging",
            "payment_method": "Apple Pay",
            "reconciliation_status": "reconciled"
        }
    },
    {
        "source_filename": "reconciliation-mismatch-bistro.png",
        "mime_type": "image/png",
        "raw_ocr_text": """THE CORNER BISTRO
Receipt #CB-771
Date: 10/05/2026
Food & Beverage Subtotal: $20.00
City Tax: $2.00
TOTAL CHARGED: $28.50
(Tip was added on terminal)""",
        "expected": {
            "merchant": "The Corner Bistro",
            "document_type": "receipt",
            "invoice_number": "CB-771",
            "transaction_date": "2026-10-05",
            "currency": "USD",
            "subtotal": 20.00,
            "tax": 2.00,
            "total": 28.50,
            "category": "Meals & Entertainment",
            "payment_method": None,
            "reconciliation_status": "mismatch"
        }
    },
    {
        "source_filename": "illegible-taxi-receipt.png",
        "mime_type": "image/png",
        "raw_ocr_text": """METRO TAXI CAB
Cab ID: 419
Date: 09/25/2026
Meter Fare: **.** (smudged)
Tolls: $4.50
Subtotal: $18.50
Card: Amex 1004""",
        "expected": {
            "merchant": "Metro Taxi Cab",
            "document_type": "receipt",
            "invoice_number": None,
            "transaction_date": "2026-09-25",
            "currency": "USD",
            "subtotal": 18.50,
            "tax": None,
            "total": None,
            "category": "Travel & Lodging",
            "payment_method": "Amex 1004",
            "reconciliation_status": "mismatch"
        }
    },
    {
        "source_filename": "indian-gst-tech-solutions.pdf",
        "mime_type": "application/pdf",
        "raw_ocr_text": """Tech Solutions Pvt Ltd
Tax Invoice #INV-9988
Date: 2026-10-10
Client: Freelance Dev
Subtotal: ₹2300.00
GST (18%): ₹414.00
Promotional Discount: ₹114.00
Total Amount: ₹2600.00
Payment Mode: UPI / Net Banking""",
        "expected": {
            "merchant": "Tech Solutions Pvt Ltd",
            "document_type": "invoice",
            "invoice_number": "INV-9988",
            "transaction_date": "2026-10-10",
            "currency": "INR",
            "subtotal": 2300.00,
            "tax": 414.00,
            "discount": 114.00,
            "additional_charges": 0.00,
            "total": 2600.00,
            "category": "Software & SaaS",
            "payment_method": "UPI",
            "reconciliation_status": "reconciled"
        }
    },
    {
        "source_filename": "express-courier-surcharge.pdf",
        "mime_type": "application/pdf",
        "raw_ocr_text": """Flash Courier Delivery Services
Invoice #FC-5521
Date: 2026-09-12
Base Shipment Subtotal: $50.00
Standard Tax (8%): $4.00
Urgent Delivery Surcharge: $10.00
Total Charged: $64.00
Credit Card: Visa 2201""",
        "expected": {
            "merchant": "Flash Courier Delivery Services",
            "document_type": "invoice",
            "invoice_number": "FC-5521",
            "transaction_date": "2026-09-12",
            "currency": "USD",
            "subtotal": 50.00,
            "tax": 4.00,
            "discount": 0.00,
            "additional_charges": 10.00,
            "total": 64.00,
            "category": "Office Supplies",
            "payment_method": "Visa 2201",
            "reconciliation_status": "reconciled"
        }
    }
]
