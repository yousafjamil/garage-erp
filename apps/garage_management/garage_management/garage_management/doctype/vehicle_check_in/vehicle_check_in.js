frappe.ui.form.on("Vehicle Check-In", {
	setup(frm) {
		frm.set_query("vehicle", () => ({ filters: frm.doc.customer ? { customer: frm.doc.customer } : {} }));
	},
	refresh(frm) {
		if (frm.is_new()) return;
		if (!frm.doc.repair_job) {
			frm.add_custom_button(__("Repair Job"), () => {
				frappe.new_doc("Repair Job", {
					customer: frm.doc.customer, vehicle: frm.doc.vehicle, check_in: frm.doc.name,
					mileage: frm.doc.mileage, customer_complaint: frm.doc.customer_complaint,
					estimated_completion: frm.doc.estimated_completion, status: "Checked In",
				});
			}, __("Create"));
		}
		frm.add_custom_button(__("Inspection"), () => {
			frappe.new_doc("Vehicle Inspection", {
				customer: frm.doc.customer, vehicle: frm.doc.vehicle, check_in: frm.doc.name,
				repair_job: frm.doc.repair_job, mileage: frm.doc.mileage,
			});
		}, __("Create"));
	},
	vehicle(frm) {
		if (!frm.doc.vehicle) return;
		frappe.db.get_value("Garage Vehicle", frm.doc.vehicle, ["customer", "current_mileage"]).then((r) => {
			if (r.message.customer) frm.set_value("customer", r.message.customer);
			if (!frm.doc.mileage) frm.set_value("mileage", r.message.current_mileage);
		});
	},
});
