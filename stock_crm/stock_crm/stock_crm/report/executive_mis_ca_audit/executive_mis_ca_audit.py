import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart, report_summary

def get_columns():
	return [
		{"label": _("Deal ID"), "fieldname": "name", "fieldtype": "Link", "options": "Unlisted Deal Ledger", "width": 140},
		{"label": _("Date"), "fieldname": "confirmation_date", "fieldtype": "Date", "width": 110},
		{"label": _("Stock Name"), "fieldname": "stock", "fieldtype": "Link", "options": "Unlisted Stock", "width": 180},
		{"label": _("ISIN"), "fieldname": "isin_number", "fieldtype": "Data", "width": 130},
		{"label": _("Quantity"), "fieldname": "quantity", "fieldtype": "Float", "width": 100},
		{"label": _("Seller Profile"), "fieldname": "seller_profile", "fieldtype": "Link", "options": "Counterparty Profile", "width": 150},
		{"label": _("Seller Gross (₹)"), "fieldname": "seller_gross_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Buyer Profile"), "fieldname": "buyer_profile", "fieldtype": "Link", "options": "Counterparty Profile", "width": 150},
		{"label": _("Buyer Gross (₹)"), "fieldname": "buyer_gross_value", "fieldtype": "Currency", "width": 130},
		{"label": _("Stamp Duty 0.015% (₹)"), "fieldname": "stamp_duty", "fieldtype": "Currency", "width": 140},
		{"label": _("TCS 0.10% (₹)"), "fieldname": "tcs_value", "fieldtype": "Currency", "width": 130},
		{"label": _("Total Net Due (₹)"), "fieldname": "total_net_due", "fieldtype": "Currency", "width": 140},
		{"label": _("Net Arbitrage (₹)"), "fieldname": "net_arbitrage", "fieldtype": "Currency", "width": 140},
	]

def get_data(filters):
	conditions = "WHERE docstatus = 1"
	if filters and filters.get("from_date"):
		conditions += f" AND confirmation_date >= '{filters.get('from_date')}'"
	if filters and filters.get("to_date"):
		conditions += f" AND confirmation_date <= '{filters.get('to_date')}'"

	return frappe.db.sql(f"""
		SELECT
			name, confirmation_date, stock, isin_number, quantity,
			seller_profile, seller_gross_cost,
			buyer_profile, buyer_gross_value,
			stamp_duty, tcs_value, total_net_due, net_arbitrage
		FROM `tabUnlisted Deal Ledger`
		{conditions}
		ORDER BY confirmation_date DESC
	""", as_dict=True)

def get_chart(data):
	if not data:
		return None
	labels = [d.name for d in data[:10]]
	net_arb = [d.net_arbitrage for d in data[:10]]
	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Net Arbitrage Profit"), "values": net_arb}]
		},
		"type": "bar",
		"colors": ["#10b981"]
	}

def get_report_summary(data):
	if not data:
		return []
	total_volume = sum(d.buyer_gross_value for d in data)
	total_stamp = sum(d.stamp_duty for d in data)
	total_tcs = sum(d.tcs_value for d in data)
	total_arbitrage = sum(d.net_arbitrage for d in data)

	return [
		{"value": total_volume, "label": _("Total Volume Traded"), "datatype": "Currency", "currency": "INR"},
		{"value": total_stamp, "label": _("Total Stamp Duty (Sec 9A)"), "datatype": "Currency", "currency": "INR"},
		{"value": total_tcs, "label": _("Total TCS (Form 27EQ)"), "datatype": "Currency", "currency": "INR"},
		{"value": total_arbitrage, "label": _("Net Arbitrage Profit"), "datatype": "Currency", "currency": "INR", "indicator": "Green" if total_arbitrage >= 0 else "Red"},
	]
