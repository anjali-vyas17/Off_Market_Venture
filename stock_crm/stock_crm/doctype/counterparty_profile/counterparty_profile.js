frappe.ui.form.on('Counterparty Profile', {
    on_submit: function(frm) {
        frappe.msgprint(__('Counterparty Profile submitted. Opening Unlisted Deal Ledger form...'));
        setTimeout(() => {
            frappe.new_doc('Unlisted Deal Ledger', {
                seller_profile: frm.doc.name
            });
        }, 1500);
    }
});
