frappe.ui.form.on("Garage Vehicle", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Service History"), () => {
			frappe.set_route("query-report", "Vehicle Service History", { vehicle: frm.doc.name });
		});
		frm.add_custom_button(__("Check In"), () => {
			frappe.new_doc("Vehicle Check-In", { vehicle: frm.doc.name, customer: frm.doc.customer, mileage: frm.doc.current_mileage });
		}, __("Create"));
		frm.add_custom_button(__("Repair Job"), () => {
			frappe.new_doc("Repair Job", { vehicle: frm.doc.name, customer: frm.doc.customer, mileage: frm.doc.current_mileage });
		}, __("Create"));
	},
});
