frappe.ui.form.on('Unlisted Stock', {
    on_submit: function(frm) {
        frappe.msgprint(__('Unlisted Stock submitted. Opening Counterparty Profile form...'));
        setTimeout(() => {
            frappe.new_doc('Counterparty Profile');
        }, 1500);
    }
});
