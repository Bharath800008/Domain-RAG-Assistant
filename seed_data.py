"""Creates one admin user and indexes 2-3 sample HR-policy documents on first run.

Run once after installing backend deps and before starting the server:
    python seed_data.py
"""
import os

from database import Base, engine, SessionLocal
import models
from auth import hash_password
from config import settings
from rag.chunker import chunk_document
from rag.retriever import index_chunks

Base.metadata.create_all(bind=engine)

SAMPLE_DOCS = {
    "PTO_Policy.txt": """## Overview
This policy explains how paid time off (PTO) accrues and how to request it.

## Accrual
Full-time employees accrue 1.5 days of PTO per month, up to a maximum of 18 days per year.
Part-time employees accrue PTO on a pro-rated basis according to their scheduled hours.

## Requesting Time Off
Employees should submit PTO requests through the HR portal at least 5 business days in
advance for planned absences. Manager approval is required before time off is confirmed.

## Carryover
Up to 5 unused PTO days may be carried over into the following calendar year. Any
balance beyond 5 days is forfeited unless local law requires otherwise.

## Sick Leave
Sick leave is tracked separately from PTO and does not require advance notice. Employees
should notify their manager as soon as reasonably possible when taking sick leave.
""",
    "Remote_Work_Policy.txt": """## Eligibility
Employees may work remotely if their role does not require regular on-site presence and
their manager has approved a remote work arrangement.

## Equipment
The company provides a laptop and a one-time home office stipend of $300 for approved
remote employees. Additional equipment requests are reviewed on a case-by-case basis.

## Core Hours
Remote employees are expected to be available during core hours of 10am-3pm in their
local timezone for meetings and collaboration, regardless of their broader schedule.

## Security Requirements
Remote employees must use company-managed devices with disk encryption enabled and must
connect to internal systems only through the approved VPN client.

## Review
Remote work arrangements are reviewed every 12 months and may be adjusted based on
business needs, team structure, or performance.
""",
    "Code_of_Conduct.txt": """## Purpose
This Code of Conduct sets expectations for professional behavior for all employees,
contractors, and interns.

## Respect in the Workplace
Employees are expected to treat colleagues, clients, and partners with respect.
Harassment, discrimination, or retaliation of any kind will not be tolerated and should
be reported to HR immediately.

## Conflicts of Interest
Employees must disclose any outside employment, financial interest, or relationship
that could reasonably be seen as a conflict of interest with their role at the company.

## Confidentiality
Employees must protect confidential company information, including customer data,
source code, and internal strategy documents, both during and after employment.

## Reporting Violations
Concerns can be reported to a manager, HR, or through the anonymous ethics hotline.
Retaliation against anyone who reports a concern in good faith is strictly prohibited.
""",
}


def seed():
    db = SessionLocal()
    try:
        admin = db.query(models.User).filter(models.User.email == "admin@example.com").first()
        if not admin:
            admin = models.User(
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("Created admin user: admin@example.com / admin123")
        else:
            print("Admin user already exists, skipping creation.")

        existing_docs = {d.filename for d in db.query(models.Document).all()}
        os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)

        for filename, content in SAMPLE_DOCS.items():
            if filename in existing_docs:
                print(f"Skipping already-seeded document: {filename}")
                continue

            filepath = os.path.join(settings.DOCUMENTS_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            document = models.Document(
                filename=filename,
                filepath=filepath,
                filetype="txt",
                status="processing",
                uploaded_by=admin.id,
            )
            db.add(document)
            db.commit()
            db.refresh(document)

            records = chunk_document(content)
            count = index_chunks(db, document, records)
            document.chunk_count = count
            document.status = "indexed"
            db.commit()
            print(f"Indexed {filename} ({count} chunks)")

        print("\nSeed complete. You can now start the backend with: uvicorn main:app --reload")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
