app_name = "stock_crm"
app_title = "Stock CRM"
app_publisher = "Off Market Venture"
app_description = "Share Market & Unlisted Equity CRM for Frappe Framework & ERPNext v15"
app_email = "admin@offmarketventure.com"
app_license = "mit"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/stock_crm/css/stock_crm.css"
# app_include_js = "/assets/stock_crm/js/stock_crm.js"

# Document Events
# ---------------
# Hook on_submit for Unlisted Deal Ledger to trigger audit logs or WhatsApp notifications
doc_events = {
	"Unlisted Deal Ledger": {
		"on_submit": "stock_crm.stock_crm.doctype.unlisted_deal_ledger.unlisted_deal_ledger.on_submit_deal",
	}
}

# Fixtures — sync standard records to DB on migrate
fixtures = [
	{"dt": "Number Card", "filters": [["module", "=", "Stock CRM"]]},
	{"dt": "Dashboard Chart", "filters": [["module", "=", "Stock CRM"]]},
	{"dt": "Dashboard", "filters": [["module", "=", "Stock CRM"]]},
]

# Required Apps
required_apps = ["frappe", "erpnext"]
