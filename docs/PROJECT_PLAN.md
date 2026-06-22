# QuoteFlow Pro Project Plan

## Product Vision

QuoteFlow Pro will be a professional quotation and business operations platform for companies that need to manage customers, products, stock, quotations, PDF offers, and orders from a single modern dashboard.

The product should feel like a real B2B SaaS platform, not a simple school project.

## Target Users

- Machinery sellers
- Spare parts sellers
- Technical service companies
- Small B2B companies
- Local businesses that prepare quotations for customers
- Equipment and product-based service providers

## Main Value

The main value of the product is simple:

A business can prepare a professional customer quotation quickly, export it as PDF, track its status, and convert it into an order.

## Main Modules

### 1. Authentication

- Register
- Login
- JWT authentication
- Protected dashboard

### 2. Company Workspace

- Company profile
- Workspace-based data separation
- Future multi-user support

### 3. Customers

- Customer list
- Customer detail
- Customer contact information
- Customer quotation history

### 4. Products and Stock

- Product list
- Product categories
- Unit price
- Stock quantity
- Low stock indicator
- Product search and filtering

### 5. Quotations

- Create quotation
- Add customer
- Add products
- Quantity and price calculation
- Discount support
- Tax/VAT support
- Notes and terms
- Quotation status tracking

### 6. PDF Export

- Professional PDF quotation layout
- Company information
- Customer information
- Product table
- Totals
- Notes and terms

### 7. Orders

- Convert accepted quotation into order
- Track order status
- Reduce stock when needed

### 8. Dashboard

- Total customers
- Total products
- Open quotations
- Accepted quotations
- Monthly quotation value
- Low stock products

### 9. Audit Logs

- Track important actions
- Quotation created
- Quotation updated
- PDF generated
- Order created

### 10. AI Assistant Later

AI features will be added after the core system is stable.

Possible AI features:

- Generate quotation note
- Generate customer message
- Improve product description
- Summarize pending quotations
- Suggest follow-up message

## Development Principles

- Professional code structure
- Step-by-step development
- No unnecessary complexity at the beginning
- Stable backend first
- Modern frontend after core API works
- Test important workflows
- Keep Git commits clean
- Use Cursor only for controlled tasks

## Development Phases

### Phase 1: Project Setup

- Repository setup
- README
- Project plan
- Backend/frontend folder structure

### Phase 2: Backend Foundation

- FastAPI setup
- Database setup
- Settings
- Health endpoint
- Alembic setup

### Phase 3: Authentication

- User model
- Register
- Login
- JWT token
- Protected endpoint

### Phase 4: Company Workspace

- Company model
- Company creation
- User-company relationship

### Phase 5: Customers

- Customer model
- Customer CRUD
- Customer search

### Phase 6: Products and Stock

- Product model
- Product CRUD
- Stock fields
- Product search and filtering

### Phase 7: Quotations

- Quote model
- Quote item model
- Create quote
- Quote totals
- Quote status

### Phase 8: PDF Quotation Export

- PDF generation
- Professional quotation template
- Download endpoint

### Phase 9: Orders

- Convert quote to order
- Order model
- Order status

### Phase 10: Frontend

- Next.js setup
- Login page
- Dashboard
- Customers page
- Products page
- Quotations page
- Orders page

### Phase 11: Docker and CI

- Docker Compose
- Backend Dockerfile
- Frontend Dockerfile
- GitHub Actions

### Phase 12: Final Documentation

- README update
- API documentation
- Screenshots
- Release tag
