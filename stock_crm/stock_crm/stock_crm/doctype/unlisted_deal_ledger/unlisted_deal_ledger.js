frappe.ui.form.on('Unlisted Deal Ledger', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 1) {
			// Add 1-Click PDF Deal Confirmation Note button
			frm.add_custom_button(__('📄 Generate Deal Note PDF'), function() {
				const url = frappe.urllib.get_full_url(
					`/api/method/frappe.utils.print_format.download_pdf?doctype=Unlisted%20Deal%20Ledger&name=${frm.doc.name}&format=Deal%20Confirmation%20Note`
				);
				window.open(url, '_blank');
			}).addClass('btn-primary');

			// Add 1-Click Sales Invoice button
			frm.add_custom_button(__('🧾 Create Sales Invoice'), function() {
				frappe.model.with_doctype('Sales Invoice', function() {
					let invoice = frappe.model.get_new_doc('Sales Invoice');
					invoice.customer = frm.doc.buyer_profile;
					invoice.posting_date = frm.doc.confirmation_date;
					frappe.set_route('Form', 'Sales Invoice', invoice.name);
				});
			});
		}

		frm.trigger('calculate_totals');
	},

	quantity: function(frm) { frm.trigger('calculate_totals'); },
	seller_rate: function(frm) { frm.trigger('calculate_totals'); },
	buyer_rate: function(frm) { frm.trigger('calculate_totals'); },
	tcs_applicable: function(frm) { frm.trigger('calculate_totals'); },
	tcs_rate: function(frm) { frm.trigger('calculate_totals'); },
	brokerage_split: function(frm) { frm.trigger('calculate_totals'); },
	direct_expenses: function(frm) { frm.trigger('calculate_totals'); },

	calculate_totals: function(frm) {
		const qty = flt(frm.doc.quantity || 0);
		const s_rate = flt(frm.doc.seller_rate || 0);
		const b_rate = flt(frm.doc.buyer_rate || 0);

		// 1. Seller Gross Cost
		const seller_gross = flt((qty * s_rate).toFixed(2));
		frm.set_value('seller_gross_cost', seller_gross);

		// 2. Buyer Gross Value
		const buyer_gross = flt((qty * b_rate).toFixed(2));
		frm.set_value('buyer_gross_value', buyer_gross);

		// 3. Stamp Duty 0.015% (Sec 9A)
		const stamp_duty = flt((buyer_gross * 0.00015).toFixed(2));
		frm.set_value('stamp_duty', stamp_duty);

		// 4. TCS Value 0.10% (Sec 206C(1H))
		let tcs_val = 0.00;
		if (frm.doc.tcs_applicable === 'YES') {
			const t_rate = flt(frm.doc.tcs_rate || 0.10) / 100.0;
			tcs_val = flt((buyer_gross * t_rate).toFixed(2));
		}
		frm.set_value('tcs_value', tcs_val);

		// 5. Total Net Due From Buyer
		const total_due = flt((buyer_gross + stamp_duty + tcs_val).toFixed(2));
		frm.set_value('total_net_due', total_due);

		// 6. Net Deal Arbitrage Profit
		const brokerage = flt(frm.doc.brokerage_split || 0);
		const expenses = flt(frm.doc.direct_expenses || 0);
		const gross_spread = buyer_gross - seller_gross;
		const net_arb = flt((gross_spread - brokerage - expenses).toFixed(2));
		frm.set_value('net_arbitrage', net_arb);
	}
});
