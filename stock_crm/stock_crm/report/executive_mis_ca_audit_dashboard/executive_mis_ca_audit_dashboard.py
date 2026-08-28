import frappe
from frappe import _
from datetime import date


# ─── Indian Financial Year helpers (Apr → Mar) ────────────────────────────────

def _fy_start_year():
	today = date.today()
	return today.year if today.month >= 4 else today.year - 1

def _fy_label(sy):
	return f"{sy}-{str(sy + 1)[-2:]}"          # e.g. "2026-27"

def _quarters():
	"""Return Q1–Q4 + Full Year rows for the current Indian FY."""
	sy = _fy_start_year()
	lb = _fy_label(sy)
	return [
		{"quarter": f"Q1  Apr–Jun {sy}",     "from_date": date(sy,   4,  1), "to_date": date(sy,   6, 30)},
		{"quarter": f"Q2  Jul–Sep {sy}",     "from_date": date(sy,   7,  1), "to_date": date(sy,   9, 30)},
		{"quarter": f"Q3  Oct–Dec {sy}",     "from_date": date(sy,  10,  1), "to_date": date(sy,  12, 31)},
		{"quarter": f"Q4  Jan–Mar {sy + 1}", "from_date": date(sy+1, 1,  1), "to_date": date(sy+1, 3, 31)},
		{"quarter": f"FULL YEAR {lb}",       "from_date": date(sy,   4,  1), "to_date": date(sy+1, 3, 31), "is_total": True},
	]


# ─── Main execute ──────────────────────────────────────────────────────────────

def execute(filters=None):
	columns   = get_columns()
	deal_data = get_data(filters)
	summary   = get_report_summary(deal_data)
	quarterly = get_quarterly_data()
	chart     = get_chart(quarterly)
	combined  = list(deal_data) + _build_block_b(quarterly)
	return columns, combined, None, chart, summary


# ─── Columns ──────────────────────────────────────────────────────────────────

def get_columns():
	return [
		{
			"label": _("Deal ID / Quarter"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Unlisted Deal Ledger",
			"width": 210,
		},
		{
			"label": _("Date / From Date"),
			"fieldname": "confirmation_date",
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"label": _("Stock Name"),
			"fieldname": "stock",
			"fieldtype": "Link",
			"options": "Unlisted Stock",
			"width": 160,
		},
		{
			"label": _("ISIN / To Date"),
			"fieldname": "isin_number",
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"label": _("Qty"),
			"fieldname": "quantity",
			"fieldtype": "Float",
			"width": 80,
		},
		{
			"label": _("Seller Profile"),
			"fieldname": "seller_profile",
			"fieldtype": "Link",
			"options": "Counterparty Profile",
			"width": 150,
		},
		{
			"label": _("Seller Gross (₹)"),
			"fieldname": "seller_gross_cost",
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"label": _("Buyer Profile"),
			"fieldname": "buyer_profile",
			"fieldtype": "Link",
			"options": "Counterparty Profile",
			"width": 150,
		},
		{
			"label": _("Buyer Gross (₹)"),
			"fieldname": "buyer_gross_value",
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"label": _("Stamp Duty 0.015% (₹)"),
			"fieldname": "stamp_duty",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("TCS 0.10% (₹)"),
			"fieldname": "tcs_value",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": _("Total Net Due (₹)"),
			"fieldname": "total_net_due",
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"label": _("Net Arb / Agg. Tax (₹)"),
			"fieldname": "net_arbitrage",
			"fieldtype": "Currency",
			"width": 160,
		},
	]


# ─── Deal data rows ────────────────────────────────────────────────────────────

def get_data(filters):
	conditions = ["docstatus = 1"]
	values = {}
	if filters and filters.get("from_date"):
		conditions.append("confirmation_date >= %(from_date)s")
		values["from_date"] = filters.get("from_date")
	if filters and filters.get("to_date"):
		conditions.append("confirmation_date <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	where = "WHERE " + " AND ".join(conditions)

	return frappe.db.sql(f"""
		SELECT
			name, confirmation_date, stock, isin_number, quantity,
			seller_profile, seller_gross_cost,
			buyer_profile, buyer_gross_value,
			stamp_duty, tcs_value, total_net_due, net_arbitrage,
			brokerage_split, direct_expenses
		FROM `tabUnlisted Deal Ledger`
		{where}
		ORDER BY confirmation_date DESC
	""", values, as_dict=True)


# ─── Quarterly aggregation ─────────────────────────────────────────────────────

def get_quarterly_data():
	quarters = _quarters()
	for q in quarters:
		row = frappe.db.sql("""
			SELECT
				COALESCE(SUM(stamp_duty), 0) AS stamp_duty,
				COALESCE(SUM(tcs_value),  0) AS tcs_value
			FROM `tabUnlisted Deal Ledger`
			WHERE docstatus = 1
			  AND confirmation_date >= %(fd)s
			  AND confirmation_date <= %(td)s
		""", {"fd": q["from_date"], "td": q["to_date"]}, as_dict=True)
		q["stamp_duty"] = row[0].stamp_duty if row else 0
		q["tcs_value"]  = row[0].tcs_value  if row else 0
		q["agg_tax"]    = q["stamp_duty"] + q["tcs_value"]
	return quarters


# ─── BLOCK B builder ──────────────────────────────────────────────────────────

def _build_block_b(quarterly):
	"""
	Appends a blank separator, a bold section-header row, then one row
	per quarter (Q1–Q4 + Full Year) with stamp duty, TCS, aggregate tax.
	Columns reused for BLOCK B:
	  name              → Quarter / Period label
	  confirmation_date → Date From
	  isin_number       → Date To  (plain Data field)
	  stamp_duty        → Stamp Duty total
	  tcs_value         → TCS total
	  net_arbitrage     → Aggregate Tax (Stamp + TCS)
	"""
	rows = []

	# blank spacer
	rows.append({"name": None})

	# BLOCK B section header
	rows.append({
		"name": "  BLOCK B  ▶  CA Quarterly Audit — Stamp Duty & TCS [Sec 206C(1H)] Summary",
		"bold": 1,
		"is_total_row": 1,
	})

	for q in quarterly:
		is_total = q.get("is_total", False)
		rows.append({
			"name":              q["quarter"],
			"confirmation_date": q["from_date"],
			"isin_number":       q["to_date"].strftime("%d/%m/%Y"),
			"stamp_duty":        q["stamp_duty"],
			"tcs_value":         q["tcs_value"],
			"net_arbitrage":     q["agg_tax"],
			"bold":              1 if is_total else 0,
			"is_total_row":      1 if is_total else 0,
		})
	return rows


# ─── Chart — Quarterly bar ────────────────────────────────────────────────────

def get_chart(quarterly):
	if not quarterly:
		return None
	# Exclude the Full Year summary row from chart labels
	qs = [q for q in quarterly if not q.get("is_total")]
	return {
		"data": {
			"labels": [q["quarter"] for q in qs],
			"datasets": [
				{"name": _("Stamp Duty (₹)"), "values": [q["stamp_duty"] for q in qs]},
				{"name": _("TCS (₹)"),        "values": [q["tcs_value"]  for q in qs]},
			],
		},
		"type":   "bar",
		"colors": ["#1a5e2e", "#c07a00"],
		"title":  _("CA Quarterly Audit — Stamp Duty & TCS [Sec 206C(1H)]"),
	}


# ─── Report Summary — BLOCK A KPI strip ──────────────────────────────────────
# These 7 values appear as the highlighted summary strip at the top of the
# report, matching BLOCK A of your Excel EXECUTIVE_MIS_DASHBOARD.

def get_report_summary(data):
	if not data:
		return []

	total_volume    = sum(d.buyer_gross_value         or 0 for d in data)
	total_arb       = sum(d.net_arbitrage             or 0 for d in data)
	total_brokerage = sum((d.get("brokerage_split")   or 0) for d in data)
	total_expenses  = sum((d.get("direct_expenses")   or 0) for d in data)
	total_stamp     = sum(d.stamp_duty                or 0 for d in data)
	total_tcs       = sum(d.tcs_value                 or 0 for d in data)

	return [
		{
			"value": total_volume,
			"label": _("Total Gross Transaction Volume"),
			"datatype": "Currency", "currency": "INR",
		},
		{
			"value": total_arb,
			"label": _("Gross Transaction Spreads (Buy–Sell)"),
			"datatype": "Currency", "currency": "INR",
			"indicator": "Green" if total_arb >= 0 else "Red",
		},
		{
			"value": total_brokerage,
			"label": _("Cumulative Brokerage Splits Paid"),
			"datatype": "Currency", "currency": "INR",
		},
		{
			"value": total_expenses,
			"label": _("Total Direct Deal Expenses"),
			"datatype": "Currency", "currency": "INR",
		},
		{
			"value": total_arb,
			"label": _("Net Realized Deal Arbitrage"),
			"datatype": "Currency", "currency": "INR",
			"indicator": "Green" if total_arb >= 0 else "Red",
		},
		{
			"value": total_stamp,
			"label": _("Total Stamp Duty Accrued [Sec 9A]"),
			"datatype": "Currency", "currency": "INR",
		},
		{
			"value": total_tcs,
			"label": _("Total TCS Collected [Sec 206C(1H)]"),
			"datatype": "Currency", "currency": "INR",
		},
	]
