import frappe

def run():
	frappe.set_user("Administrator")
	
	# Complete Setup Wizard
	frappe.db.set_single_value("System Settings", "setup_complete", 1)
	frappe.db.set_single_value("System Settings", "language", "en")
	frappe.db.set_single_value("System Settings", "country", "India")
	frappe.db.set_single_value("System Settings", "time_zone", "Asia/Kolkata")
	frappe.db.set_single_value("System Settings", "currency", "INR")
	
	# Ensure Administrator first_name is set
	admin = frappe.get_doc("User", "Administrator")
	admin.first_name = "Administrator"
	admin.save(ignore_permissions=True)
	
	frappe.db.commit()
	print("SUCCESS: Setup Wizard completed for crm.local!")
