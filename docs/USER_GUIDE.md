# User guide — daily garage workflow

Sign in at your ERP address; you land directly on the **Garage** page (no app launcher). It shows: today's jobs, cars in the garage, jobs waiting
for approval / in repair / ready, today's invoices, outstanding payments, monthly revenue, low-stock parts.

## The 10 steps
1. **Customer** — *Customers → New* (name, phone, email). One customer can own many cars.
2. **Vehicle** — *Garage Vehicle → New*: plate, VIN, make/model/year, owner. (Or open the customer → Connections → Garage Vehicle → +.)
3. **Check-In** — open the vehicle → **Create → Check In**. Mileage, fuel level, complaint, existing dents, keys/accessories, photos. Print the check-in form for the customer to sign.
4. **Inspection** — from the check-in or job: **Create → Inspection**. The 13-point checklist is pre-filled; set each to Good / Attention Needed / Repair Required / Critical, add notes and photos.
5. **Repair Job** — from the check-in: **Create → Repair Job** (starts as *Checked In*). Assign the technician; add **Services & Labor** and **Spare Parts** (rates fill in from the item; edit if needed).
6. **Quotation** — on the job: **Create → Quotation**, review, **Submit**, then **Print/Email** (PDF with letterhead). On the job, use *Actions → Send for Approval*.
7. **Customer approval** — on the submitted quotation: **Customer Decision → Customer Approved / Rejected** (enter who approved, comments). Approved → job becomes *Approved*. **Repair cannot start before this** (a Manager/Owner can override).
8. **Repair** — job *Actions*: Start Repair → Send to Quality Check → Quality Passed (Manager/Owner) → *Ready for Delivery*.
9. **Invoice & payment** — on the job: **Create → Invoice** (stock of parts is reduced when the invoice is submitted). Submit it, then on the invoice **Create → Payment** (Cash / Card / Bank Transfer / Other).
10. **Delivery** — job *Actions → Deliver Vehicle* (needs the invoice fully paid, unless overridden). Vehicle status becomes *Delivered*.

**Service history:** open any vehicle → **Service History** button (or Reports → Vehicle Service History): every job with
date, mileage, complaint, diagnosis, services, parts, technician, invoice, paid/outstanding.

## Making the system yours (no developer needed)
Open **Garage → Garage Settings** (Owner/Manager). Everything below updates the whole system and all printed/emailed documents when you press Save:
- **Identity:** garage name (English/Arabic), tagline, **logo** (login page, menu bar, browser tab), accent colour of document tables.
- **Letterhead:** upload your own **header** and **footer** images (full-width banners), or switch *Letterhead Style* to **Text** to build a simple header/footer from name, phones, email and address.
- **Quotation / Invoice / Job Card / Check-In / Receipt:** titles (English + Arabic), terms & conditions, **bank/payment details**, notes, the check-in declaration, a thank-you line, and how many days a quotation is valid.
Tip: tables and numbers come from the system and cannot be broken by editing these texts. For a completely different layout, duplicate the print format (Printing → Print Format) — see docs/PRINT_FORMATS.md.
The ERPNext/Frappe names and logos are removed from the screens, menus, emails and documents; the garage's own name and logo are shown instead.

## Customer 360
*Reports → Customer 360* → pick a customer (type name or phone): contact details, all their vehicles, every repair job,
**total spent** and **still owes**, last visit. Phone search works when the phone is saved on the customer's primary
Contact (use the "+ New Customer" popup and fill Mobile/Email).

## Searching
Type in the top search bar: customer name or phone, plate, VIN, job/quotation/invoice number, part name or code.

## What each person sees (Simple Mode)
Everyone signs in to the **Garage** home page with big buttons ("What would you like to do?") and a short left menu:
Home · New Check-In · Repair Jobs · Inspections · Customers · Vehicles · Quotations · Invoices · Payments · Parts & Services · Reports · Settings.
The menu only shows what the person is allowed to use (a receptionist has no Invoices/Payments/Settings; a technician lands directly on
**their own** jobs). Owner and Accountant also have the full accounting, stock and purchasing screens when needed. Nothing is deleted —
it is only kept out of the way.

## Simple screens
Quotation, Invoice, Customer, Item and Payment forms show only what a garage uses (the accounting, shipping, price-list, sales-team and tax-withholding
sections are hidden). Every document has big **Print**, **Download PDF** and **Email** buttons at the top, and a repair job shows a blue line saying
what to do next plus a big **Next** button. When someone really needs everything: open the **⋯ menu → Show all fields** (and **Simple view** to come back).
A new customer needs only **Name, Type, Mobile and Email** — the phone number then finds the customer in the search bar.

## Roles (Role Profiles)
| Profile | For | Can do |
|---|---|---|
| Garage Owner | owner | everything incl. accounting, purchasing, items, reports |
| Garage Manager | manager | jobs, customers, vehicles, quotations, invoices, payments, parts; override rules |
| Receptionist | front desk | customers, vehicles, check-in, quotations, job basics, delivery |
| Technician | mechanic | **only jobs assigned to them**: inspection, notes, services/parts on the job |
| Accountant | bookkeeper | invoices, payments, journals, financial reports (read-only on jobs) |
| Inventory Manager | parts/stock | items, stock, suppliers, purchase orders |

**Add a user:** *Settings → Users → New* → email, name → **Role Profile** (pick from the table) → Save → *Send Welcome Email* or set a password.
Technicians must be assigned on the job (*Technician* field) to see it.

## Money & VAT
Prices are entered **excluding VAT**; the default tax template adds VAT (rate configured in *Sales Taxes and Charges
Template*, not in code). Invoices show exact amounts (no rounding to whole dirhams). **Ask the accountant to confirm**:
VAT rate/treatment per item (standard / zero-rated / exempt), the company **TRN** (Company → Tax ID), financial-year
start, and the default accounts (receivable, income, cost of sales, cash, bank).

## Low stock
Set a minimum level on each part (*Item → Reorder / Safety Stock*). The dashboard card and report **Low Stock Parts**
show parts at or below it; owners, managers and inventory staff get a daily notification.

## Printing / emailing
Every document has a Print menu with the garage format (Quotation, Tax Invoice, Job Card, Vehicle Inspection,
Vehicle Check-In, Payment Receipt). Use the *Email* button on a document to send the PDF.
