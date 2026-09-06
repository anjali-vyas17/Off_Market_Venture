# Copyright (c) 2026, Administrator and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ActiveLeads(Document):
	pass


def after_insert(doc, method=None):
	"""Triggered after a new Active Leads record is inserted."""
	frappe.logger().info(f"Active Leads created: {doc.name}")


def on_submit(doc, method=None):
	"""Triggered when an Active Leads record is submitted."""
	frappe.logger().info(f"Active Leads submitted: {doc.name}")
