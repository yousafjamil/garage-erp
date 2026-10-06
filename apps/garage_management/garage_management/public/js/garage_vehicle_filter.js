// Only offer the selected customer's vehicles on Sales Order / Sales Invoice.
["Sales Order", "Sales Invoice"].forEach((dt) =>
	frappe.ui.form.on(dt, {
		setup(frm) {
			frm.set_query("vehicle", () => ({ filters: frm.doc.customer ? { customer: frm.doc.customer } : {} }));
		},
	}));
