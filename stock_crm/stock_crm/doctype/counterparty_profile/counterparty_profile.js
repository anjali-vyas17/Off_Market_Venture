frappe.ui.form.on('Counterparty Profile', {

    // ── Auto-uppercase PAN as the user types ─────────────────────────────────
    refresh: function(frm) {
        frm.fields_dict['pan'].$input.on('input', function() {
            const pos = this.selectionStart;
            this.value = this.value.toUpperCase();
            this.setSelectionRange(pos, pos);   // keep cursor position
        });
    },

    // ── Validate on save/submit ──────────────────────────────────────────────
    validate: function(frm) {
        validate_mobile(frm);
        validate_pan(frm);
        validate_dp_id(frm);
        validate_client_id(frm);
    },

    // ── On submit ────────────────────────────────────────────────────────────
    on_submit: function(frm) {
        frappe.msgprint(__('Counterparty Profile submitted. Opening Unlisted Deal Ledger form...'));
        setTimeout(() => {
            frappe.new_doc('Unlisted Deal Ledger', {
                seller_profile: frm.doc.name
            });
        }, 1500);
    }
});

// ── Helper: Mobile Number – exactly 10 digits ────────────────────────────────
function validate_mobile(frm) {
    const mobile = (frm.doc.whatsapp || '').trim();
    if (!mobile) return;                          // field is optional

    const mobile_regex = /^\d{1,10}$/;           // only digits, max 10
    if (!mobile_regex.test(mobile)) {
        frappe.throw(__('WhatsApp Mobile must contain digits only and cannot exceed 10 digits.'));
    }
    if (mobile.length < 10) {
        frappe.throw(__('WhatsApp Mobile must be exactly 10 digits.'));
    }
}

// ── Helper: PAN Number – format AAAAANNNNA (5 alpha + 4 num + 1 alpha) ───────
function validate_pan(frm) {
    const pan = (frm.doc.pan || '').trim().toUpperCase();
    if (!pan) return;                             // reqd check handled by Frappe

    const pan_regex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    if (!pan_regex.test(pan)) {
        frappe.throw(__(
            'Invalid PAN Number "{0}". Format must be: 5 letters + 4 digits + 1 letter (e.g. BJATQ8876T).',
            [pan]
        ));
    }

    // Also auto-uppercase the value in the field
    if (frm.doc.pan !== pan) {
        frm.set_value('pan', pan);
    }
}

// ── Helper: DP ID – digits only, max 8 ──────────────────────────────────────
function validate_dp_id(frm) {
    const dp_id = (frm.doc.dp_id || '').trim();
    if (!dp_id) return;                           // field is optional

    if (!/^\d+$/.test(dp_id)) {
        frappe.throw(__('DP ID must contain digits only.'));
    }
    if (dp_id.length > 8) {
        frappe.throw(__('DP ID cannot exceed 8 digits.'));
    }
}

// ── Helper: Client ID / Beneficiary ID – digits only, max 8 ─────────────────
function validate_client_id(frm) {
    const client_id = (frm.doc.client_id || '').trim();
    if (!client_id) return;                       // field is optional

    if (!/^\d+$/.test(client_id)) {
        frappe.throw(__('Client ID / Beneficiary ID must contain digits only.'));
    }
    if (client_id.length > 8) {
        frappe.throw(__('Client ID / Beneficiary ID cannot exceed 8 digits.'));
    }
}
