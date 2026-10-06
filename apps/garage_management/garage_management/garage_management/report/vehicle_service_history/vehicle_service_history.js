frappe.query_reports["Vehicle Service History"] = {
	filters: [
  {
    "fieldname": "vehicle",
    "label": "Vehicle",
    "fieldtype": "Link",
    "options": "Garage Vehicle"
  },
  {
    "fieldname": "customer",
    "label": "Customer",
    "fieldtype": "Link",
    "options": "Customer"
  },
  {
    "fieldname": "plate_number",
    "label": "Plate No",
    "fieldtype": "Data"
  },
  {
    "fieldname": "from_date",
    "label": "From Date",
    "fieldtype": "Date"
  },
  {
    "fieldname": "to_date",
    "label": "To Date",
    "fieldtype": "Date"
  }
],
};
