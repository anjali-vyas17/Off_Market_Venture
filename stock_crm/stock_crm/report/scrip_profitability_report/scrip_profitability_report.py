import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"label": _("Stock Name"), "fieldname": "stock", "fieldtype": "Link", "options": "Unlisted Stock", "width": 200},
		{"label": _("ISIN"), "fieldname": "isin_number", "fieldtype": "Data", "width": 140},
		{"label": _("Total Qty Traded"), "fieldname": "total_qty", "fieldtype": "Float", "width": 120},
		{"label": _("Total Buy Cost (₹)"), "fieldname": "total_buy_cost", "fieldtype": "Currency", "width": 140},
		{"label": _("Total Sell Value (₹)"), "fieldname": "total_sell_val", "fieldtype": "Currency", "width": 140},
		{"label": _("Net Arbitrage Profit (₹)"), "fieldname": "net_profit", "fieldtype": "Currency", "width": 160},
		{"label": _("Profit Margin (%)"), "fieldname": "profit_margin", "fieldtype": "Percent", "width": 120},
	]

	data = frappe.db.sql("""
		SELECT
			stock,
			isin_number,
			SUM(quantity) as total_qty,
			SUM(seller_gross_cost) as total_buy_cost,
			SUM(buyer_gross_value) as total_sell_val,
			SUM(net_arbitrage) as net_profit,
			CASE WHEN SUM(seller_gross_cost) > 0 THEN (SUM(net_arbitrage) / SUM(seller_gross_cost)) * 100 ELSE 0 END as profit_margin
		FROM `tabUnlisted Deal Ledger`
		WHERE docstatus = 1
		GROUP BY stock, isin_number
		ORDER BY net_profit DESC
	""", as_dict=True)

	return columns, data
