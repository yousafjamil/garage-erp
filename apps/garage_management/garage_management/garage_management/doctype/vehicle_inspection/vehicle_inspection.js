frappe.ui.form.on("Vehicle Inspection", {
	setup(frm) {
		frm.set_query("vehicle", () => ({ filters: frm.doc.customer ? { customer: frm.doc.customer } : {} }));
	},
	refresh(frm) {
		if (frm.is_new() && !(frm.doc.items || []).length) {
			frappe.call("garage_management.garage_management.doctype.vehicle_inspection.vehicle_inspection.default_checklist").then((r) => {
				(r.message || []).forEach((c) => frm.add_child("items", { component: c, result: "Good" }));
				frm.refresh_field("items");
			});
		}
	},
	vehicle(frm) {
		if (!frm.doc.vehicle) return;
		frappe.db.get_value("Garage Vehicle", frm.doc.vehicle, "customer").then((r) => {
			if (r.message.customer) frm.set_value("customer", r.message.customer);
		});
	},
});
