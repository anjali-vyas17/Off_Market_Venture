import frappe
from frappe.model.document import Document

class UnlistedDealLedger(Document):
	def validate(self):
		self.calculate_totals()
		self.validate_roles()

	def calculate_totals(self):
		qty = float(self.quantity or 0)
		s_rate = float(self.seller_rate or 0)
		b_rate = float(self.buyer_rate or 0)

		# 1. Seller Gross Cost
		self.seller_gross_cost = round(qty * s_rate, 2)

		# 2. Buyer Gross Value
		self.buyer_gross_value = round(qty * b_rate, 2)

		# 3. Stamp Duty 0.015% (Sec 9A)
		self.stamp_duty = round(self.buyer_gross_value * 0.00015, 2)

		# 4. TCS Value 0.10% (Sec 206C(1H))
		if self.tcs_applicable == "YES":
			t_rate = float(self.tcs_rate or 0.10) / 100.0
			self.tcs_value = round(self.buyer_gross_value * t_rate, 2)
		else:
			self.tcs_value = 0.00

		# 5. Total Net Due From Buyer
		self.total_net_due = round(self.buyer_gross_value + self.stamp_duty + self.tcs_value, 2)

		# 6. Net Deal Arbitrage Profit
		brokerage = float(self.brokerage_split or 0)
		expenses = float(self.direct_expenses or 0)
		gross_spread = self.buyer_gross_value - self.seller_gross_cost
		self.net_arbitrage = round(gross_spread - brokerage - expenses, 2)

	def validate_roles(self):
		# Prevent agents from submitting directly if they only have Stock Agent role
		if self.docstatus == 1 and frappe.session.user != "Administrator":
			roles = frappe.get_roles(frappe.session.user)
			if "Stock Agent" in roles and "Stock Team Lead" not in roles and "Stock Admin" not in roles:
				frappe.throw("Stock Agents cannot submit deals. Please request a Team Lead review.")

def on_submit_deal(doc, method):
	frappe.msgprint(f"Deal {doc.name} successfully submitted and locked by {frappe.session.user}.")
