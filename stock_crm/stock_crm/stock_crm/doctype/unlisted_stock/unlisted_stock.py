import frappe
from frappe.model.document import Document

class UnlistedStock(Document):
	def validate(self):
		if self.isin_number:
			self.isin_number = self.isin_number.strip().upper()
