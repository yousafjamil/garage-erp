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

// One-step payment dialog (used on the invoice and on the repair job).
window.garage_receive_payment = function (invoice, outstanding, after) {
	const d = new frappe.ui.Dialog({
		title: __("Receive Payment"),
		fields: [
			{ fieldname: "amount", fieldtype: "Currency", label: __("Amount"), reqd: 1, default: outstanding },
			{ fieldname: "mode", fieldtype: "Select", label: __("Paid by"), reqd: 1, options: "Cash\nCard\nBank Transfer\nOther", default: "Cash" },
			{ fieldname: "reference", fieldtype: "Data", label: __("Reference (card slip / transfer no, optional)") },
		],
		primary_action_label: __("Save Payment"),
		primary_action(v) {
			frappe.call({
				method: "garage_management.api.payments.receive_payment",
				args: { invoice, amount: v.amount, mode_of_payment: v.mode, reference_no: v.reference },
				freeze: true,
			}).then((r) => {
				d.hide();
				after && after(r.message);
				frappe.confirm(__("Payment saved. Print the receipt?"), () =>
					window.open(`/printview?doctype=Payment%20Entry&name=${encodeURIComponent(r.message.payment_entry)}`
						+ `&format=Garage%20Payment%20Receipt&no_letterhead=0`, "_blank"));
			});
		},
	});
	d.show();
};

frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		if (frm.doc.docstatus !== 1 || !(frm.doc.outstanding_amount > 0)) return;
		const btn = frm.add_custom_button(__("Receive Payment"), () =>
			window.garage_receive_payment(frm.doc.name, frm.doc.outstanding_amount, () => frm.reload_doc()));
		btn.removeClass("btn-default").addClass("btn-success");
	},
});
