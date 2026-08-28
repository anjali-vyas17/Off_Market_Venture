import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"label": _("Agent / User"), "fieldname": "owner", "fieldtype": "Link", "options": "User", "width": 200},
		{"label": _("Total Deals Created"), "fieldname": "deal_count", "fieldtype": "Int", "width": 130},
		{"label": _("Total Qty Traded"), "fieldname": "total_qty", "fieldtype": "Float", "width": 130},
		{"label": _("Gross Turnover (₹)"), "fieldname": "turnover", "fieldtype": "Currency", "width": 160},
		{"label": _("Arbitrage Profit (₹)"), "fieldname": "total_arbitrage", "fieldtype": "Currency", "width": 160},
	]

	data = frappe.db.sql("""
		SELECT
			owner,
			COUNT(name) as deal_count,
			SUM(quantity) as total_qty,
			SUM(buyer_gross_value) as turnover,
			SUM(net_arbitrage) as total_arbitrage
		FROM `tabUnlisted Deal Ledger`
		WHERE docstatus = 1
		GROUP BY owner
		ORDER BY total_arbitrage DESC
	""", as_dict=True)

	return columns, data
