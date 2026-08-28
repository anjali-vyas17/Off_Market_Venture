import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"label": _("Deal ID"), "fieldname": "name", "fieldtype": "Link", "options": "Unlisted Deal Ledger", "width": 140},
		{"label": _("Date"), "fieldname": "confirmation_date", "fieldtype": "Date", "width": 100},
		{"label": _("Stock Name"), "fieldname": "stock", "fieldtype": "Link", "options": "Unlisted Stock", "width": 160},
		{"label": _("Seller Profile"), "fieldname": "seller_profile", "fieldtype": "Link", "options": "Counterparty Profile", "width": 150},
		{"label": _("Seller Gross Cost"), "fieldname": "seller_gross_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Shares Credited?"), "fieldname": "shares_credited", "fieldtype": "Check", "width": 110},
		{"label": _("Payout Released?"), "fieldname": "payout_released", "fieldtype": "Check", "width": 110},
		{"label": _("Buyer Profile"), "fieldname": "buyer_profile", "fieldtype": "Link", "options": "Counterparty Profile", "width": 150},
		{"label": _("Total Net Due"), "fieldname": "total_net_due", "fieldtype": "Currency", "width": 130},
		{"label": _("Buyer Paid?"), "fieldname": "buyer_pmt_recd", "fieldtype": "Check", "width": 100},
		{"label": _("Shares Delivered?"), "fieldname": "shares_delivered", "fieldtype": "Check", "width": 110},
	]

	data = frappe.db.sql("""
		SELECT
			name, confirmation_date, stock,
			seller_profile, seller_gross_cost, shares_credited, payout_released,
			buyer_profile, total_net_due, buyer_pmt_recd, shares_delivered
		FROM `tabUnlisted Deal Ledger`
		WHERE docstatus = 1
			AND (shares_credited = 0 OR payout_released = 0 OR buyer_pmt_recd = 0 OR shares_delivered = 0)
		ORDER BY confirmation_date DESC
	""", as_dict=True)

	return columns, data
