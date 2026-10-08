# ERPNext vs custom — decision table

| Requirement | Decision | Implementation |
|---|---|---|
| Customers (+ phone/email/address/type/notes), customer history | Standard | ERPNext Customer; garage tab in its Connections (dashboard hook) |
| Suppliers, purchase orders/invoices, stock, warehouses, reorder levels | Standard | ERPNext Buying/Stock |
| Services and spare parts | Standard | Item (services = non-stock, parts = stock); groups *Services* / *Spare Parts*; VAT via Item Tax Template |
| Quotations, invoices, payments, VAT, accounting | Standard | Quotation / Sales Order / Sales Invoice / Payment Entry; UAE chart + VAT templates; 5% template is default (rate lives in the template) |
| Email, PDF, print formats | Standard + Print Format | SMTP in Email Account; 6 Jinja print formats (letterhead, TRN, Arabic/English titles) |
| Users, roles, permissions | Standard + custom roles | Roles *Garage Owner/Manager, Receptionist, Technician* + Role Profiles incl. Accountant & Inventory Manager (reuse Accounts/Stock roles) |
| Notifications | Standard | 6 Notification records + 1 daily low-stock job |
| Reports | Standard + 6 custom | Sales/Receivable/Stock/P&L standard; custom: Vehicle Service History, Jobs by Status, Technician Performance, Parts Used (most used), Services Performed (common/revenue), Low Stock Parts |
| Dashboard | Standard widgets | Workspace *Garage*: 11 Number Cards, 3 Charts, shortcuts |
| Vehicle (owner, plate, VIN, mileage, status…) | **Custom DocType** `Garage Vehicle` | ERPNext's own *Vehicle* is a fleet record with no customer link |
| Check-in (complaint, fuel, damage, keys, photos) | **Custom DocType** `Vehicle Check-In` | no standard equivalent |
| Inspection checklist (13 components × 4 results, photos) | **Custom DocType** `Vehicle Inspection` + child | no standard equivalent (Quality Inspection is for stock items) |
| Job card / repair job with statuses | **Custom DocType** `Repair Job` + **Workflow** | ERPNext Job Card is manufacturing-specific |
| Customer approval before repair | **Custom Fields** on Quotation + small API + gate in Repair Job | `record_approval`; manager override flag |
| Job → Quotation → Sales Order → Invoice (stock reduced by invoice) | Small API using ERPNext's own mappers | `api/repair_job.py` |
| Vehicle/Job link on Quotation, Order, Invoice | **Custom Fields** | `setup/custom_fields.py` |
| Manufacturing, Projects, Assets, Quality, CRM, HR, POS | Not necessary | hidden from menus (small garage); not uninstalled |
