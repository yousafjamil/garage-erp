frappe.ui.form.on("Customer Statement", {
	setup(frm) {
		if (frm.is_new() && !frm.doc.company) frm.set_value("company", frappe.defaults.get_user_default("Company"));
		if (frm.is_new() && !frm.doc.from_date) {
			frm.set_value("from_date", frappe.datetime.month_start());
			frm.set_value("to_date", frappe.datetime.month_end());
		}
	},
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Refresh"), () => { frm.dirty(); frm.save(); });
		if (frm.doc.balance_due > 0) {
			frm.add_custom_button(__("Receive Payment"), () => window.garage_receive_payment({
				company: frm.doc.company, customer: frm.doc.customer, after: () => { frm.dirty(); frm.save(); } }))
				.removeClass("btn-default").addClass("btn-success");
		}
	},
});
