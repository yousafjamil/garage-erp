frappe.ui.form.on("Quotation", {
	setup(frm) {
		frm.set_query("vehicle", () => ({ filters: frm.doc.party_name ? { customer: frm.doc.party_name } : {} }));
	},
	refresh(frm) {
		if (frm.doc.docstatus !== 1 || frm.doc.approval_status !== "Pending") return;
		const record = (decision) => {
			const d = new frappe.ui.Dialog({
				title: __(decision),
				fields: [
					{ fieldname: "approved_by", fieldtype: "Data", label: __("Decision given by (customer name)"), reqd: decision === "Customer Approved" ? 1 : 0 },
					{ fieldname: "comments", fieldtype: "Small Text", label: __("Customer comments") },
				],
				primary_action_label: __("Save"),
				primary_action(v) {
					frappe.call({
						method: "garage_management.api.repair_job.record_approval",
						args: { quotation: frm.doc.name, decision, approved_by: v.approved_by, comments: v.comments },
					}).then(() => { d.hide(); frm.reload_doc(); });
				},
			});
			d.show();
		};
		frm.add_custom_button(__("Customer Approved"), () => record("Customer Approved"), __("Customer Decision"));
		frm.add_custom_button(__("Customer Rejected"), () => record("Customer Rejected"), __("Customer Decision"));
	},
});
