// Lean forms: hide the accounting/sales-office clutter garage staff never use.
// Nothing is removed - "Show all fields" in the menu (top right) reveals everything again.
const GARAGE_SIMPLE = {
	"Quotation": {
		tabs: ["Address & Contact", "Terms", "More Info"],
		sections: ["Currency and Price List", "Pricing Rules", "Bundle Items", "Tax Breakup", "Taxes and Charges"],
		fields: ["naming_series", "order_type", "quotation_to", "scan_barcode", "tax_category", "shipping_rule", "incoterm", "named_place",
			"valid_till", "apply_discount_on", "coupon_code"],
	},
	"Sales Invoice": {
		tabs: ["Payments", "Address & Contact", "Terms", "More Info"],
		sections: ["Currency and Price List", "Totals (Company Currency)", "Tax Withholding Entry", "Tax Breakup", "Pricing Rules",
			"Packing List", "Time Sheet List"],
		fields: ["naming_series", "is_pos", "is_return", "is_debit_note", "scan_barcode", "set_posting_time", "update_stock", "cost_center",
			"project", "campaign", "apply_tds", "posting_time", "tax_category", "shipping_rule", "incoterm", "named_place", "due_date"],
	},
	"Customer": {
		tabs: ["Accounting", "Settings", "Sales Team", "Portal Users", "More Info"],
		sections: ["Defaults", "Loyalty Points"],
		fields: ["naming_series", "alias", "gender", "customer_group", "territory", "customer_name_in_arabic", "salutation"],
	},
	"Payment Entry": {
		tabs: [],
		sections: ["Writeoff", "Taxes and Charges", "Deductions or Loss", "Tax Withholding Entry", "More Information", "Auto Repeat"],
		fields: ["naming_series", "payment_type_section", "cost_center", "project"],
	},
};

const garage_advanced = () => { try { return localStorage.getItem("garage_show_all") === "1"; } catch (e) { return false; } };

function garage_apply_simple(frm, cfg) {
	if (garage_advanced()) return;
	const draft_only = (cfg.hide_when_draft || []);
	let tabs_changed = false;
	frm.meta.fields.forEach((df) => {
		const label = df.label || df.fieldname;
		const hide = (df.fieldtype === "Tab Break" && cfg.tabs.includes(label))
			|| (df.fieldtype === "Section Break" && (cfg.sections.includes(label) || (frm.doc.docstatus === 0 && draft_only.includes(label))))
			|| cfg.fields.includes(df.fieldname);
		if (!hide) return;
		if (df.fieldtype === "Tab Break") {
			const tab = (frm.layout.tabs || []).find((t) => t.df.fieldname === df.fieldname);
			if (tab) { tab.df.hidden = 1; tabs_changed = true; }
		} else {
			frm.set_df_property(df.fieldname, "hidden", 1);
			frm.toggle_display(df.fieldname, false);
		}
	});
	if (tabs_changed) frm.layout.refresh_tabs();
	// some controls (e.g. the naming series) re-appear after refresh, so hide their wrappers as well
	const hide_wrappers = () => cfg.fields.forEach((fn) => frm.fields_dict[fn] && frm.fields_dict[fn].$wrapper && frm.fields_dict[fn].$wrapper.hide());
	hide_wrappers();
	setTimeout(hide_wrappers, 400);
}

Object.entries(GARAGE_SIMPLE).forEach(([doctype, cfg]) => {
	frappe.ui.form.on(doctype, {
		refresh(frm) {
			garage_apply_simple(frm, cfg);
			if (frm.__garage_menu) return;
			frm.__garage_menu = true;
			const label = garage_advanced() ? __("Simple view") : __("Show all fields");
			frm.page.add_menu_item(label, () => {
				try { localStorage.setItem("garage_show_all", garage_advanced() ? "0" : "1"); } catch (e) {}
				window.location.reload();
			});
		},
	});
});
