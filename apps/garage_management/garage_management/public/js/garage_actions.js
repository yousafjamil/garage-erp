// Big, obvious Print / PDF / Email buttons on every garage document.
const GARAGE_PRINT = {
	"Quotation": "Garage Quotation",
	"Sales Invoice": "Garage Tax Invoice",
	"Payment Entry": "Garage Payment Receipt",
	"Repair Job": "Garage Job Card",
	"Vehicle Check-In": "Garage Vehicle Check-In",
	"Vehicle Inspection": "Garage Vehicle Inspection",
};

Object.entries(GARAGE_PRINT).forEach(([doctype, format]) => {
	frappe.ui.form.on(doctype, {
		refresh(frm) {
			if (frm.is_new() || frm.doc.docstatus === 2) return;
			const base = "/api/method/frappe.utils.print_format.download_pdf";
			const pdf = `${base}?doctype=${encodeURIComponent(doctype)}&name=${encodeURIComponent(frm.doc.name)}`
				+ `&format=${encodeURIComponent(format)}&no_letterhead=0`;
			frm.add_custom_button(__("Print"), () => frm.print_doc()).addClass("btn-primary");
			frm.add_custom_button(__("Download PDF"), () => window.open(pdf, "_blank"));
			frm.add_custom_button(__("Email"), () => frm.email_doc());
		},
	});
});
