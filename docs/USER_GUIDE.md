# User guide — daily garage workflow

Sign in at your ERP address. The **Garage** workspace is the home page: today's jobs, cars in the garage, jobs waiting
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

## Searching
Type in the top search bar: customer name or phone, plate, VIN, job/quotation/invoice number, part name or code.

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
