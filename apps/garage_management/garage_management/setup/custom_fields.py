from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

GARAGE_LINK_FIELDS = lambda after: [
    dict(fieldname="garage_section", label="Garage", fieldtype="Section Break", insert_after=after, collapsible=0),
    dict(fieldname="vehicle", label="Vehicle", fieldtype="Link", options="Garage Vehicle", insert_after="garage_section",
         in_standard_filter=1, search_index=1),
    dict(fieldname="plate_number", label="Plate No", fieldtype="Data", fetch_from="vehicle.plate_number",
         read_only=1, insert_after="vehicle", in_global_search=1, allow_on_submit=1, in_list_view=1),
    dict(fieldname="garage_cb", fieldtype="Column Break", insert_after="plate_number"),
    dict(fieldname="repair_job", label="Repair Job", fieldtype="Link", options="Repair Job", read_only=1,
         insert_after="garage_cb", search_index=1, no_copy=0),
]

APPROVAL_FIELDS = [
    dict(fieldname="approval_section", label="Customer Approval", fieldtype="Section Break", insert_after="repair_job"),
    dict(fieldname="approval_status", label="Approval Status", fieldtype="Select",
         options="Pending\nCustomer Approved\nCustomer Rejected", default="Pending", read_only=1,
         allow_on_submit=1, in_standard_filter=1, no_copy=1, insert_after="approval_section", in_list_view=1),
    dict(fieldname="approval_date", label="Approval Date", fieldtype="Date", read_only=1, allow_on_submit=1,
         no_copy=1, insert_after="approval_status"),
    dict(fieldname="approval_cb", fieldtype="Column Break", insert_after="approval_date"),
    dict(fieldname="approved_by", label="Approved By", fieldtype="Data", read_only=1, allow_on_submit=1,
         no_copy=1, insert_after="approval_cb"),
    dict(fieldname="approved_amount", label="Approved Amount", fieldtype="Currency", read_only=1,
         allow_on_submit=1, no_copy=1, insert_after="approved_by"),
    dict(fieldname="customer_comments", label="Customer Comments", fieldtype="Small Text", read_only=1,
         allow_on_submit=1, no_copy=1, insert_after="approved_amount"),
]


CUSTOMER_FIELDS = [
    dict(fieldname="garage_phone", label="Mobile / Phone", fieldtype="Data", options="Phone", insert_after="customer_type",
         description="Used to find the customer by phone number.", in_list_view=1),
    dict(fieldname="garage_email", label="Email", fieldtype="Data", options="Email", insert_after="garage_phone"),
]


def create():
    fields = {
        "Customer": CUSTOMER_FIELDS,
        "Quotation": GARAGE_LINK_FIELDS("order_type") + APPROVAL_FIELDS,
        "Sales Order": GARAGE_LINK_FIELDS("order_type"),
        "Sales Invoice": GARAGE_LINK_FIELDS("posting_time"),
    }
    create_custom_fields(fields, update=True)
