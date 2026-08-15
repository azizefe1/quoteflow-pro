# QuoteFlow Pro

QuoteFlow Pro is a professional B2B quotation, customer, product, stock, and order management platform designed for small and medium-sized businesses.

The project focuses on helping businesses create professional quotations, manage customers, track products and stock, convert quotations into orders, and generate PDF quotation documents from a modern web dashboard.

## Project Goal

The goal of QuoteFlow Pro is to build a professional, marketable business operations platform that can be shown to real companies as a practical digital solution.

## Core Features

- User authentication
- Company / organization workspace
- Customer management
- Product and stock management
- Quotation creation
- Quotation item management
- PDF quotation export
- Quotation status tracking
- Convert quotation to order
- Order management
- Dashboard metrics
- Audit logs
- Role-based authorization
- Modern responsive frontend
- Docker-based deployment
- Automated tests and CI validation

## Planned Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- JWT authentication
- Pytest

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

### DevOps

- Docker
- Docker Compose
- GitHub Actions CI

## Product Direction

QuoteFlow Pro is not planned as a small demo project. It is planned as a professional SaaS-style business platform with a clean user experience, strong backend structure, and features that can provide real value to small and medium-sized companies.

## Status

Project initialization started.

## Windows Verification

From the project root, run the complete local verification flow in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

The script starts the Docker services, creates isolated verification databases,
runs Alembic migrations and backend tests, and validates the frontend with lint
and a production build. Results are saved to `verification-output.txt`.

To also rehearse the corrective migration against a SQL backup, pass the backup
path explicitly. The backup is restored only into the dedicated
`quoteflow_backup_verify` database:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify.ps1 `
  -BackupPath "C:\path\to\quoteflow_database_backup.sql"
```
