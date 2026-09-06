frappe.ui.form.on('Unlisted Deal Ledger', {
	refresh: function(frm) {
		// Quick Action Drawdown Buttons for Stock and Seller List
		frm.add_custom_button(__('📊 View Stocks'), function() {
			frappe.set_route('List', 'Unlisted Stock');
		}, __('Quick Actions'));

		frm.add_custom_button(__('👤 View Sellers'), function() {
			frappe.set_route('List', 'Counterparty Profile');
		}, __('Quick Actions'));

		// Show Print Formats on all saved records (both Draft and Submitted)
		if (!frm.is_new()) {
			frm.add_custom_button(__('📝 Deal Note'), function() {
				const url = frappe.urllib.get_full_url(
					`/printview?doctype=Unlisted%20Deal%20Ledger&name=${frm.doc.name}&format=Deal%20Note&no_letterhead=1`
				);
				window.open(url, '_blank');
			}, __('Print Formats'));

			frm.add_custom_button(__('📄 Deal Settlement Note (Niyom)'), function() {
				const url = frappe.urllib.get_full_url(
					`/printview?doctype=Unlisted%20Deal%20Ledger&name=${frm.doc.name}&format=Deal%20Settlement%20Advice&no_letterhead=1`
				);
				window.open(url, '_blank');
			}, __('Print Formats'));

			frm.add_custom_button(__('📈 Demat Shares Advice (altcase)'), function() {
				const url = frappe.urllib.get_full_url(
					`/printview?doctype=Unlisted%20Deal%20Ledger&name=${frm.doc.name}&format=Demat%20Shares%20Transfer%20Advice&no_letterhead=1`
				);
				window.open(url, '_blank');
			}, __('Print Formats'));

			frm.add_custom_button(__('💸 Payment Release Note (OMV)'), function() {
				const url = frappe.urllib.get_full_url(
					`/printview?doctype=Unlisted%20Deal%20Ledger&name=${frm.doc.name}&format=Payment%20Release%20Receipt&no_letterhead=1`
				);
				window.open(url, '_blank');
			}, __('Print Formats')).addClass('btn-primary');

			// Messages dropdown: Email & Notification
			if (frm.doc.docstatus === 1) {

				// ── Email 1: Payment Release → to Seller ──
				frm.add_custom_button(__('💸 Payment Release (Seller)'), function() {
					if (!frm.doc.seller_profile) {
						frappe.msgprint(__('No Seller Profile linked to this deal.'));
						return;
					}
					frappe.db.get_value('Counterparty Profile', frm.doc.seller_profile, ['email', 'entity_name'])
					.then(r => {
						let seller_email = r && r.message && r.message.email || '';
						let seller_name  = r && r.message && r.message.entity_name || frm.doc.seller_profile;
						new frappe.views.CommunicationComposer({
							doc: frm.doc,
							frm: frm,
							recipients: seller_email,
							subject: __('Payment Release — Deal {0}', [frm.doc.name]),
							message: __(
								'Dear {0},<br><br>' +
								'We are pleased to inform you that your payment has been successfully released against Deal <strong>{1}</strong>.<br><br>' +
								'Please find the Payment Release Note attached for your records.<br><br>' +
								'Best Regards,<br>Off Market Venture',
								[seller_name, frm.doc.name]
							),
							print_format: 'Payment Release Receipt',
							attach_document_print: true
						});
					});
				}, __('Messages'));

				// ── Email 2: Deal Settlement → to Buyer ──
				frm.add_custom_button(__('🤝 Deal Settlement (Buyer)'), function() {
					if (!frm.doc.buyer_profile) {
						frappe.msgprint(__('No Buyer Profile linked to this deal.'));
						return;
					}
					frappe.db.get_value('Counterparty Profile', frm.doc.buyer_profile, ['email', 'entity_name'])
					.then(r => {
						let buyer_email = r && r.message && r.message.email || '';
						let buyer_name  = r && r.message && r.message.entity_name || frm.doc.buyer_profile;
						new frappe.views.CommunicationComposer({
							doc: frm.doc,
							frm: frm,
							recipients: buyer_email,
							subject: __('Deal Settlement Confirmation — {0}', [frm.doc.name]),
							message: __(
								'Dear {0},<br><br>' +
								'We are pleased to confirm that your investment has been successfully executed and settled in full.<br><br>' +
								'<strong>Deal Reference:</strong> {1}<br>' +
								'<strong>Total Amount:</strong> ₹{2}<br><br>' +
								'Please find the Deal Settlement Note attached for your records.<br><br>' +
								'Should you have any questions, please reach out to your Relationship Manager.<br><br>' +
								'Best Regards,<br>Off Market Venture',
								[buyer_name, frm.doc.name, frm.doc.total_net_due || '']
							),
							print_format: 'Deal Settlement Advice',
							attach_document_print: true
						});
					});
				}, __('Messages'));

				// Notification option
				frm.add_custom_button(__('🔔 Notification'), function() {
					frappe.prompt([
						{
							fieldname: 'user',
							label: __('Send To (User)'),
							fieldtype: 'Link',
							options: 'User',
							reqd: 1
						},
						{
							fieldname: 'message',
							label: __('Message'),
							fieldtype: 'Small Text',
							reqd: 1,
							default: __('Regarding Deal: {0} — please review.', [frm.doc.name])
						}
					], function(values) {
						frappe.call({
							method: 'frappe.client.insert',
							args: {
								doc: {
									doctype: 'Notification Log',
									subject: __('Deal Notification: {0}', [frm.doc.name]),
									email_content: values.message,
									for_user: values.user,
									type: 'Alert',
									document_type: frm.doctype,
									document_name: frm.doc.name,
									from_user: frappe.session.user
								}
							},
							callback: function(r) {
								if (!r.exc) {
									frappe.show_alert({
										message: __('Notification sent to {0}', [values.user]),
										indicator: 'green'
									});
								}
							}
						});
					}, __('Send Notification'), __('Send'));
				}, __('Messages'));
			}
		}
	},

	seller_profile: function(frm) {
		if (frm.doc.seller_profile) {
			frappe.db.get_doc('Counterparty Profile', frm.doc.seller_profile).then(cp => {
				if (cp && cp.bank_accounts && cp.bank_accounts.length > 0) {
					const b = cp.bank_accounts[0];
					frm.set_value('seller_bank_account', `${b.bank_name} - Acc: ${b.account_number} (IFSC: ${b.ifsc_code})`);
				}
			});
		}
	},

	buyer_profile: function(frm) {
		if (frm.doc.buyer_profile) {
			frappe.db.get_doc('Counterparty Profile', frm.doc.buyer_profile).then(cp => {
				if (cp && cp.bank_accounts && cp.bank_accounts.length > 0) {
					const b = cp.bank_accounts[0];
					frm.set_value('buyer_bank_account', `${b.bank_name} - Acc: ${b.account_number} (IFSC: ${b.ifsc_code})`);
				}
			});
		}
	},

	quantity: function(frm) { frm.trigger('calculate_totals'); },
	seller_rate: function(frm) { frm.trigger('calculate_totals'); },
	buyer_rate: function(frm) { frm.trigger('calculate_totals'); },
	tcs_applicable: function(frm) { frm.trigger('calculate_totals'); },
	tcs_rate: function(frm) { frm.trigger('calculate_totals'); },
	brokerage_split: function(frm) { frm.trigger('calculate_totals'); },
	direct_expenses: function(frm) { frm.trigger('calculate_totals'); },
	referral_fee: function(frm) { frm.trigger('calculate_totals'); },

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

		// 4. TCS Value 0.10% (Sec 206C(1H)) - Auto calculated
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
		const referral = flt(frm.doc.referral_fee || 0);
		const gross_spread = buyer_gross - seller_gross;
		const net_arb = flt((gross_spread - brokerage - expenses - referral).toFixed(2));
		frm.set_value('net_arbitrage', net_arb);
	},

	on_submit: function(frm) {
		frappe.msgprint(__('Deal submitted. Opening Active Leads form...'));
		setTimeout(function() {
			frappe.new_doc('Active Leads');
		}, 1500);
	}
});
