// Print / PDF / Email buttons on every document, and the one-step "Receive Payment" box.
const GARAGE_PRINT = {
	"Quotation": "Quotation Print",
	"Sales Invoice": "Tax Invoice Print",
	"Service Job Card": "Job Card Print",
	"Customer Statement": "Statement Print",
	"Payment Entry": "Receipt Print",
};

Object.entries(GARAGE_PRINT).forEach(([doctype, format]) => {
	frappe.ui.form.on(doctype, {
		refresh(frm) {
			if (frm.is_new() || frm.doc.docstatus === 2) return;
			const pdf = `/api/method/frappe.utils.print_format.download_pdf?doctype=${encodeURIComponent(doctype)}`
				+ `&name=${encodeURIComponent(frm.doc.name)}&format=${encodeURIComponent(format)}&no_letterhead=0`;
			frm.add_custom_button(__("Print"), () => frm.print_doc()).addClass("btn-primary");
			frm.add_custom_button(__("Download PDF"), () => window.open(pdf, "_blank"));
			frm.add_custom_button(__("Email"), () => frm.email_doc());
		},
	});
});

// opts: { company?, customer, invoice?, after? }  - pays this customer's oldest unpaid invoices first (or just `invoice`).
window.garage_receive_payment = function (opts) {
	const d = new frappe.ui.Dialog({
		title: __("Receive Payment"),
		fields: [
			{ fieldname: "company", fieldtype: "Link", options: "Company", label: __("Business"), reqd: 1, default: opts.company, read_only: opts.company ? 1 : 0,
				onchange() { refresh_due(); } },
			{ fieldname: "due", fieldtype: "Currency", label: __("Customer owes"), read_only: 1 },
			{ fieldname: "amount", fieldtype: "Currency", label: __("Amount received"), reqd: 1 },
			{ fieldname: "mode", fieldtype: "Select", label: __("Paid by"), reqd: 1, options: "Cash\nCard\nBank Transfer\nCheque\nOther", default: "Cash" },
			{ fieldname: "date", fieldtype: "Date", label: __("Date"), default: frappe.datetime.get_today() },
			{ fieldname: "reference", fieldtype: "Data", label: __("Reference (cheque / transfer no, optional)") },
		],
		primary_action_label: __("Save Payment"),
		primary_action(v) {
			frappe.call({
				method: "garage_management.api.payments.receive_customer_payment", freeze: true,
				args: { company: v.company, customer: opts.customer, amount: v.amount, mode_of_payment: v.mode, reference_no: v.reference,
					posting_date: v.date, invoice: opts.invoice },
			}).then((r) => {
				d.hide();
				const left = r.message.balance_due;
				frappe.show_alert({ message: __("Payment saved. Balance still due: {0}", [format_currency(left)]), indicator: "green" }, 8);
				opts.after && opts.after(r.message);
			});
		},
	});
	const refresh_due = () => {
		const company = d.get_value("company");
		if (!company) return;
		frappe.call({ method: "garage_management.api.payments.get_due", args: { company, customer: opts.customer, invoice: opts.invoice } })
			.then((r) => { d.set_value("due", r.message); if (!d.get_value("amount")) d.set_value("amount", r.message); });
	};
	d.show();
	refresh_due();
};

frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		if (frm.doc.docstatus !== 1 || !(frm.doc.outstanding_amount > 0)) return;
		frm.add_custom_button(__("Receive Payment"), () => window.garage_receive_payment({
			company: frm.doc.company, customer: frm.doc.customer, invoice: frm.doc.name, after: () => frm.reload_doc() }))
			.removeClass("btn-default").addClass("btn-success");
	},
});

frappe.ui.form.on("Customer", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Receive Payment"), () => window.garage_receive_payment({ customer: frm.doc.name, after: () => frm.reload_doc() }))
			.removeClass("btn-default").addClass("btn-success");
		frm.add_custom_button(__("New Statement"), () => frappe.new_doc("Customer Statement", { customer: frm.doc.name }));
	},
});
