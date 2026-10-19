from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

DOC_FIELDS = lambda after: [
    dict(fieldname="vehicle_no", label="Vehicle / Reference", fieldtype="Data", insert_after=after, in_list_view=1,
         in_global_search=1, allow_on_submit=1, description="Shown after the customer name, e.g. 76191 - Pickup, or the trailer / route"),
    dict(fieldname="job_card", label="Job Card", fieldtype="Link", options="Service Job Card", read_only=1, insert_after="vehicle_no"),
    dict(fieldname="doc_note", label="Note (printed on the document)", fieldtype="Small Text", allow_on_submit=1,
         insert_after="job_card"),
]


def create():
    create_custom_fields({
        "Quotation": DOC_FIELDS("party_name"),
        "Sales Invoice": DOC_FIELDS("customer_name") + [
            dict(fieldname="lpo_ref", label="LPO Ref No", fieldtype="Data", insert_after="doc_note", allow_on_submit=1)],
        "Customer": [
            dict(fieldname="garage_phone", label="Mobile / Phone", fieldtype="Data", options="Phone", insert_after="customer_type",
                 description="Used to find the customer by phone number.", in_list_view=1),
            dict(fieldname="garage_email", label="Email", fieldtype="Data", options="Email", insert_after="garage_phone"),
            dict(fieldname="doc_address", label="Address (printed on documents)", fieldtype="Data", insert_after="garage_email",
                 description="e.g. Abu Dhabi UAE"),
        ],
        "Company": [
            dict(fieldname="print_style", label="Document Style", fieldtype="Select", options="Garage\nTransport", default="Garage",
                 insert_after="company_name", description="Which layout the quotations, invoices and job cards use."),
            dict(fieldname="arabic_name", label="Name (Arabic)", fieldtype="Data", insert_after="print_style"),
            dict(fieldname="bank_details", label="Bank / Account Details (printed on invoices)", fieldtype="Small Text",
                 insert_after="arabic_name"),
            dict(fieldname="quotation_vat_text", label="Quotation VAT wording", fieldtype="Data", insert_after="bank_details",
                 default="5 % Vat will be applicable at bill as per UAE Law"),
            dict(fieldname="quotation_note", label="Quotation note", fieldtype="Small Text", insert_after="quotation_vat_text"),
            dict(fieldname="invoice_note", label="Invoice note", fieldtype="Small Text", insert_after="quotation_note"),
        ],
    }, update=True)
