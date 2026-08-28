import frappe
from frappe.model.document import Document

class CounterpartyProfile(Document):
	def validate(self):
		if self.pan:
			self.pan = self.pan.strip().upper()
