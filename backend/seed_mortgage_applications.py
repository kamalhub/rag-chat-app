#!/usr/bin/env python3
"""
Seed script: Create "Mortgage Application" collection with sample documents.
Each document has a unique documentID (UUID) and meaningful values based on M1i form structure.

Run: MONGODB_URI=mongodb://localhost:27017/rag uv run python seed_mortgage_applications.py
"""

import os
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load .env from backend/ or project root
load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

try:
    from pymongo import MongoClient
except ImportError:
    print("pymongo not installed. Run: uv sync")
    exit(1)


COLLECTION_NAME = "Mortgage Application"


def _get_client():
    uri = os.getenv("MONGODB_URI", "").strip()
    if not uri:
        print("Set MONGODB_URI in .env (e.g. mongodb://localhost:27017/rag)")
        return None
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def _sample_documents():
    """Return list of sample mortgage application documents with UUID documentIDs."""
    return [
        {
            "documentID": str(uuid.uuid4()),
            "application_type": "Full Mortgage Application",
            "reason_for_mortgage": "Your main residence",
            "created_at": datetime.now(datetime.UTC).isoformat(),
            "status": "Submitted",
            "applicants": [
                {
                    "title": "Mr",
                    "forenames": "James",
                    "surname": "Thompson",
                    "date_of_birth": "1985-03-15",
                    "nationality": "British",
                    "country_of_birth": "United Kingdom",
                    "national_insurance_number": "AB123456C",
                    "marital_status": "Married",
                    "uk_tax_resident": True,
                    "contact": {
                        "home_phone": "01632 960123",
                        "mobile": "07700 900123",
                        "email": "james.thompson@example.com",
                    },
                    "employment": {
                        "type": "Employed",
                        "employment_type": "Permanent",
                        "occupation": "Software Engineer",
                        "employer_name": "Tech Solutions Ltd",
                        "employer_address": "12 Innovation Park, Manchester, M1 4BT",
                        "length_of_service_years": 5,
                        "length_of_service_months": 3,
                        "gross_salary_annual": 52000,
                        "bonus_annual": 5000,
                        "income_frequency": "Monthly",
                    },
                    "address": {
                        "property_number": "42",
                        "street": "Oak Lane",
                        "town": "Manchester",
                        "postcode": "M16 8PQ",
                        "occupancy_status": "Private Tenant",
                        "moved_in_date": "2020-06-01",
                    },
                },
                {
                    "title": "Mrs",
                    "forenames": "Sarah",
                    "surname": "Thompson",
                    "date_of_birth": "1987-07-22",
                    "nationality": "British",
                    "country_of_birth": "United Kingdom",
                    "national_insurance_number": "CD789012E",
                    "marital_status": "Married",
                    "uk_tax_resident": True,
                    "contact": {
                        "home_phone": "01632 960123",
                        "mobile": "07700 900456",
                        "email": "sarah.thompson@example.com",
                    },
                    "employment": {
                        "type": "Employed",
                        "employment_type": "Permanent",
                        "occupation": "Primary School Teacher",
                        "employer_name": "Manchester City Council",
                        "employer_address": "Town Hall, Albert Square, Manchester M2 5DB",
                        "length_of_service_years": 8,
                        "length_of_service_months": 0,
                        "gross_salary_annual": 38500,
                        "bonus_annual": 0,
                        "income_frequency": "Monthly",
                    },
                    "address": {
                        "property_number": "42",
                        "street": "Oak Lane",
                        "town": "Manchester",
                        "postcode": "M16 8PQ",
                        "occupancy_status": "Private Tenant",
                        "moved_in_date": "2020-06-01",
                    },
                },
            ],
            "property": {
                "address": "15 Maple Drive",
                "postcode": "M20 4GH",
                "property_type": "Semi-detached",
                "property_description": "House",
                "number_of_bedrooms": 4,
                "tenure": "Freehold",
                "purchase_price": 285000,
                "construction_type": "Standard (brick walled/tiled roof)",
                "year_built": 1995,
                "new_build": False,
            },
            "mortgage_requirements": {
                "total_borrow_amount": 228000,
                "mortgage_term_years": 25,
                "repayment_type": "Repayment",
                "mortgage_type": "Fixed rate",
                "fixed_rate_term_years": 5,
                "interest_rate_percent": 4.25,
                "product_fee": 999,
                "add_fee_to_loan": False,
            },
            "deposit": {
                "total_deposit": 57000,
                "sources": [
                    {"source": "Savings account in UK or EEA", "amount": 45000},
                    {"source": "Gift", "amount": 12000},
                ],
            },
            "monthly_outgoings": {
                "childcare": 450,
                "personal_loans": 180,
                "credit_card_balance": 1200,
            },
            "credit_history": {
                "bankruptcy_last_6_years": False,
                "property_repossessed": False,
            },
        },
        {
            "documentID": str(uuid.uuid4()),
            "application_type": "Decision In Principle",
            "reason_for_mortgage": "Your main residence",
            "created_at": datetime.now(datetime.UTC).isoformat(),
            "status": "Pending",
            "applicants": [
                {
                    "title": "Ms",
                    "forenames": "Emma",
                    "surname": "Wilson",
                    "date_of_birth": "1992-11-08",
                    "nationality": "British",
                    "country_of_birth": "United Kingdom",
                    "national_insurance_number": "EF345678G",
                    "marital_status": "Single",
                    "uk_tax_resident": True,
                    "contact": {
                        "home_phone": "020 7946 0958",
                        "mobile": "07891 234567",
                        "email": "emma.wilson@example.com",
                    },
                    "employment": {
                        "type": "Employed",
                        "employment_type": "Permanent",
                        "occupation": "Marketing Manager",
                        "employer_name": "Digital Agency Ltd",
                        "employer_address": "45 Canary Wharf, London E14 5AB",
                        "length_of_service_years": 3,
                        "length_of_service_months": 6,
                        "gross_salary_annual": 48000,
                        "bonus_annual": 8000,
                        "income_frequency": "Monthly",
                    },
                    "address": {
                        "property_number": "Flat 7",
                        "street": "Riverside Court",
                        "town": "London",
                        "postcode": "E1 6AN",
                        "occupancy_status": "Living with relatives",
                        "moved_in_date": "2022-01-15",
                    },
                },
            ],
            "property": {
                "address": "8 Church Street",
                "postcode": "SW15 2PQ",
                "property_type": "Purpose built flat",
                "property_description": "Purpose built flat",
                "number_of_bedrooms": 2,
                "tenure": "Leasehold",
                "leasehold_unexpired_years": 95,
                "purchase_price": 395000,
                "construction_type": "Standard (brick walled/tiled roof)",
                "year_built": 2010,
                "new_build": False,
            },
            "mortgage_requirements": {
                "total_borrow_amount": 316000,
                "mortgage_term_years": 30,
                "repayment_type": "Repayment",
                "mortgage_type": "Fixed rate",
                "fixed_rate_term_years": 2,
                "interest_rate_percent": 5.49,
                "product_fee": 0,
                "add_fee_to_loan": False,
            },
            "deposit": {
                "total_deposit": 79000,
                "sources": [
                    {"source": "Savings account in UK or EEA", "amount": 79000},
                ],
            },
            "monthly_outgoings": {
                "childcare": 0,
                "personal_loans": 0,
                "credit_card_balance": 450,
            },
            "credit_history": {
                "bankruptcy_last_6_years": False,
                "property_repossessed": False,
            },
        },
        {
            "documentID": str(uuid.uuid4()),
            "application_type": "Full Mortgage Application",
            "reason_for_mortgage": "Your main residence",
            "created_at": datetime.now(datetime.UTC).isoformat(),
            "status": "Under Review",
            "applicants": [
                {
                    "title": "Mr",
                    "forenames": "David",
                    "surname": "Roberts",
                    "date_of_birth": "1978-05-30",
                    "nationality": "British",
                    "country_of_birth": "United Kingdom",
                    "national_insurance_number": "GH901234I",
                    "marital_status": "Divorced",
                    "uk_tax_resident": True,
                    "contact": {
                        "home_phone": "0117 496 0123",
                        "mobile": "07912 345678",
                        "email": "david.roberts@example.com",
                    },
                    "employment": {
                        "type": "Self Employed (Sole Trader)",
                        "employment_type": "Sub-Contractor Open Ended",
                        "occupation": "Electrician",
                        "employer_name": "Roberts Electrical Services",
                        "employer_address": "Unit 4, Industrial Estate, Bristol BS4 2AA",
                        "length_of_service_years": 12,
                        "length_of_service_months": 0,
                        "net_profit_latest_year": 42500,
                        "net_profit_previous_year": 39800,
                        "income_frequency": "Self-assessed",
                    },
                    "address": {
                        "property_number": "22",
                        "street": "Victoria Road",
                        "town": "Bristol",
                        "postcode": "BS6 5PQ",
                        "occupancy_status": "Owner Occupier",
                        "moved_in_date": "2015-09-01",
                    },
                },
            ],
            "property": {
                "address": "5 Mill Lane",
                "postcode": "BS8 2ST",
                "property_type": "Detached",
                "property_description": "House",
                "number_of_bedrooms": 3,
                "tenure": "Freehold",
                "purchase_price": 420000,
                "construction_type": "Standard (brick walled/tiled roof)",
                "year_built": 1982,
                "new_build": False,
            },
            "mortgage_requirements": {
                "total_borrow_amount": 252000,
                "mortgage_term_years": 20,
                "repayment_type": "Repayment",
                "mortgage_type": "Tracker rate",
                "tracker_rate_term_years": 2,
                "interest_rate_percent": 5.99,
                "product_fee": 1495,
                "add_fee_to_loan": True,
            },
            "deposit": {
                "total_deposit": 168000,
                "sources": [
                    {"source": "Equity", "amount": 168000},
                ],
            },
            "monthly_outgoings": {
                "childcare": 320,
                "personal_loans": 250,
                "credit_card_balance": 0,
            },
            "credit_history": {
                "bankruptcy_last_6_years": False,
                "property_repossessed": False,
            },
        },
    ]


def main():
    client = _get_client()
    if client is None:
        return 1

    try:
        client.admin.command("ping")
    except Exception as e:
        print(f"Cannot connect to MongoDB: {e}")
        return 1

    db = client["rag"]
    col = db[COLLECTION_NAME]

    # Ensure unique index on documentID
    col.create_index("documentID", unique=True)

    docs = _sample_documents()
    result = col.insert_many(docs)

    print(f"Created collection '{COLLECTION_NAME}' with {len(result.inserted_ids)} documents:")
    for d in docs:
        print(f"  - documentID: {d['documentID']} | {d['applicants'][0]['forenames']} {d['applicants'][0]['surname']} | {d['status']}")

    return 0


if __name__ == "__main__":
    exit(main())
