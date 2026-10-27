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

// "Details" button on every row of the Customers list: one screen with the contact data, balances per business and the latest documents.
window.garage_customer_details = function (name) {
	frappe.call({
		method: "garage_management.api.customer.get_details", args: { customer: name }, freeze: true,
		callback: (r) => {
			const d = r.message, c = d.customer, money = (v) => format_currency(v, "AED");
			const esc = frappe.utils.escape_html;
			const rows = d.companies.map((x) => `<tr><td>${esc(x.company)}</td><td class="text-right" style="white-space:nowrap">${x.quotations} / ${money(x.quoted)}</td>
				<td class="text-right" style="white-space:nowrap">${x.invoices} / ${money(x.invoiced)}</td><td class="text-right" style="white-space:nowrap">${money(x.paid)}</td>
				<td class="text-right" style="white-space:nowrap"><b style="color:${x.owes > 0 ? "#c0392b" : "#27ae60"}">${money(x.owes)}</b></td></tr>`).join("");
			const recent = d.recent.map((x) => `<tr><td><a href="${frappe.utils.get_form_link(x.doctype, x.name)}">${esc(x.name)}</a></td><td>${__(x.doctype)}</td>
				<td>${esc(x.company)}</td><td class="text-right">${money(x.grand_total)}</td><td>${x.docstatus ? "" : __("Draft")}</td></tr>`).join("");
			const dlg = new frappe.ui.Dialog({
				title: c.customer_name, size: "large",
				fields: [{ fieldtype: "HTML", fieldname: "body", options: `
					<p style="line-height:1.7">${c.tax_id ? `<b>TRN:</b> ${esc(c.tax_id)}<br>` : ""}${c.doc_address ? `<b>${__("Address")}:</b> ${esc(c.doc_address)}<br>` : ""}
					${c.garage_phone ? `<b>${__("Phone")}:</b> ${esc(c.garage_phone)}<br>` : ""}${c.garage_email ? `<b>Email:</b> ${esc(c.garage_email)}` : ""}</p>
					<table class="table table-bordered" style="font-size:13px"><thead><tr><th>${__("Business")}</th><th class="text-right">${__("Quotations")}</th>
					<th class="text-right">${__("Invoices")}</th><th class="text-right">${__("Received")}</th><th class="text-right">${__("Still owes")}</th></tr></thead>
					<tbody>${rows || `<tr><td colspan="5" class="text-muted">${__("No quotations or invoices yet")}</td></tr>`}</tbody></table>
					<h6>${__("Latest documents")}</h6>
					<table class="table table-condensed" style="font-size:13px"><tbody>${recent || `<tr><td class="text-muted">${__("Nothing yet")}</td></tr>`}</tbody></table>` }],
				primary_action_label: __("New Quotation"),
				primary_action: () => { dlg.hide(); frappe.new_doc("Quotation", { quotation_to: "Customer", party_name: name }); },
				secondary_action_label: __("Open customer"),
				secondary_action: () => { dlg.hide(); frappe.set_route("Form", "Customer", name); },
			});
			dlg.show();
			const bar = $(`<div style="margin-top:10px"></div>`).appendTo(dlg.$wrapper.find(".modal-footer"));
			[[__("New Invoice"), () => frappe.new_doc("Sales Invoice", { customer: name })],
			 [__("New Statement"), () => frappe.new_doc("Customer Statement", { customer: name })],
			 [__("Receive Payment"), () => window.garage_receive_payment({ customer: name })]].forEach(([label, fn]) =>
				$(`<button class="btn btn-default btn-sm" style="margin-right:6px">${label}</button>`).appendTo(bar).on("click", () => { dlg.hide(); fn(); }));
		},
	});
};

(function () {
	// the Customers list settings come from ERPNext's own file, which loads later: add our button whenever they are set
	let store = frappe.listview_settings["Customer"];
	const button = { show: () => true, get_label: () => __("Details"), get_description: () => __("Everything about this customer"),
		action: (doc) => window.garage_customer_details(doc.name) };
	Object.defineProperty(frappe.listview_settings, "Customer", {
		configurable: true, enumerable: true,
		get: () => Object.assign(store || {}, { button }),
		set: (v) => { store = v; },
	});
})();
