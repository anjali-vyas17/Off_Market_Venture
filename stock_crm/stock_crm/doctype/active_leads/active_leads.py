# Copyright (c) 2026, Administrator and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ActiveLeads(Document):
	def on_update(self):
		if getattr(self, "deal_id_no", None):
			if frappe.db.exists("Unlisted Deal Ledger", self.deal_id_no):
				ledger = frappe.get_doc("Unlisted Deal Ledger", self.deal_id_no)
				
				# 1st Email: Deal Confirmation Mail
				if ledger.docstatus == 1 and not self.get("deal_note_sent"):
					send_deal_confirmation_emails(self, ledger)
					self.db_set("deal_note_sent", 1, update_modified=False)
				
				# 2nd Email: Payout Confirmation (triggered by payout_released)
				if self.get("payout_released") and not self.get("email_2_sent"):
					send_payout_confirmation_email(self, ledger)
					self.db_set("email_2_sent", 1, update_modified=False)
				
				# 3rd Email: Follow-Up for Shares (triggered by shares_credited)
				if self.get("shares_credited") and not self.get("email_3_sent"):
					send_shares_followup_email(self, ledger)
					self.db_set("email_3_sent", 1, update_modified=False)
				
				# 4th Email: Payment Reminder (triggered by buyer_pmt_recd as per user instruction)
				if self.get("buyer_pmt_recd") and not self.get("email_4_sent"):
					send_buyer_payment_reminder_email(self, ledger)
					self.db_set("email_4_sent", 1, update_modified=False)
				
				# 5th Email: Shares Delivered (triggered by shares_delivered as per user instruction)
				if self.get("shares_delivered") and not self.get("email_5_sent"):
					send_shares_delivered_email(self, ledger)
					self.db_set("email_5_sent", 1, update_modified=False)
				
				# 6th Email & Status Update: Transaction Closed
				# Triggered either when all 4 checkboxes are checked, OR if Lead Status is manually set to Closed
				all_checked = (self.get("shares_credited") and self.get("payout_released") and 
							   self.get("buyer_pmt_recd") and self.get("shares_delivered"))
				
				if all_checked or self.get("lead_status") == "Closed":
					
					if self.get("lead_status") != "Closed":
						self.db_set("lead_status", "Closed", update_modified=False)
					
					if not self.get("email_6_sent"):
						send_transaction_closed_email(self, ledger)
						self.db_set("email_6_sent", 1, update_modified=False)

def after_insert(doc, method=None):
	"""Triggered after a new Active Leads record is inserted."""
	frappe.logger().info(f"Active Leads created: {doc.name}")

def on_submit(doc, method=None):
	"""Triggered when an Active Leads record is submitted."""
	frappe.logger().info(f"Active Leads submitted: {doc.name}")

def send_deal_confirmation_emails(active_lead, ledger):
	buyer = frappe.get_doc("Counterparty Profile", ledger.buyer_profile) if ledger.buyer_profile else None
	seller = frappe.get_doc("Counterparty Profile", ledger.seller_profile) if ledger.seller_profile else None
	stock = frappe.get_doc("Unlisted Stock", ledger.stock) if ledger.stock else None

	subject = f"Deal Confirmation — {ledger.name} | {stock.company_name if stock else ledger.stock} | {int(ledger.quantity or 0)} Shares"

	pdf_attachment = frappe.attach_print(
		doctype="Unlisted Deal Ledger",
		name=ledger.name,
		print_format="Deal Note",
		doc=ledger
	)
	attachments = [pdf_attachment]

	if buyer and buyer.email:
		buyer_html = get_confirmation_email_html(
			counterparty_name=buyer.entity_name,
			confirmation_date=frappe.utils.formatdate(ledger.confirmation_date, "dd-mm-yyyy"),
			deal_id=ledger.name,
			stock_name=stock.company_name if stock else ledger.stock,
			isin=ledger.isin_number or "",
			quantity=int(ledger.quantity or 0),
			rate=ledger.buyer_rate or 0,
			gross_value=ledger.buyer_gross_value or 0,
			stamp_duty=ledger.stamp_duty or 0,
			tcs_value=ledger.tcs_value or 0,
			net_amount=ledger.total_net_due or 0
		)
		frappe.sendmail(
			recipients=[buyer.email],
			subject=subject,
			message=buyer_html,
			attachments=attachments,
			reference_doctype="Active Leads",
			reference_name=active_lead.name
		)

	if seller and seller.email:
		seller_html = get_confirmation_email_html(
			counterparty_name=seller.entity_name,
			confirmation_date=frappe.utils.formatdate(ledger.confirmation_date, "dd-mm-yyyy"),
			deal_id=ledger.name,
			stock_name=stock.company_name if stock else ledger.stock,
			isin=ledger.isin_number or "",
			quantity=int(ledger.quantity or 0),
			rate=ledger.seller_rate or 0,
			gross_value=ledger.seller_gross_cost or 0,
			stamp_duty=0,
			tcs_value=0,
			net_amount=ledger.seller_gross_cost or 0
		)
		frappe.sendmail(
			recipients=[seller.email],
			subject=subject,
			message=seller_html,
			attachments=attachments,
			reference_doctype="Active Leads",
			reference_name=active_lead.name
		)

def get_confirmation_email_html(counterparty_name, confirmation_date, deal_id, stock_name, isin, quantity, rate, gross_value, stamp_duty, tcs_value, net_amount):
	return f"""
	<p>Dear {counterparty_name},</p>
	<p>This is to confirm that we have finalised the following transaction on {confirmation_date}:</p>
	<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 600px;">
		<tr><td style="width: 40%; background-color: #f8fafc;"><b>Particulars</b></td><td style="background-color: #f8fafc;"><b>Details</b></td></tr>
		<tr><td>Deal ID</td><td>{deal_id}</td></tr>
		<tr><td>Security</td><td>{stock_name}</td></tr>
		<tr><td>ISIN</td><td>{isin}</td></tr>
		<tr><td>Quantity</td><td>{quantity} shares</td></tr>
		<tr><td>Rate per Share</td><td>₹{'{:,.2f}'.format(rate)}</td></tr>
		<tr><td>Total Value</td><td>₹{'{:,.2f}'.format(gross_value)}</td></tr>
		<tr><td>Stamp Duty (0.015%)</td><td>₹{'{:,.2f}'.format(stamp_duty)}</td></tr>
		<tr><td>TCS (if applicable)</td><td>₹{'{:,.2f}'.format(tcs_value)}</td></tr>
		<tr><td>Total Payable/Receivable</td><td>₹{'{:,.2f}'.format(net_amount)}</td></tr>
	</table>
	<br>
	<p>Please find the detailed Deal Confirmation Note attached for your records, along with the applicable bank and DEMAT details for settlement.</p>
	<p>Kindly revert with your confirmation and the required KYC documents (PAN, CML copy, bank proof) at the earliest so we can proceed with settlement.</p>
	<p>Looking forward to a smooth transaction.</p>
	<p>Best Regards,<br>
	<b>Off Market Venture</b><br>
	Vasant Kunj, New Delhi – 110070<br>
	+91 99681 10807 · www.offmarketventure.co</p>
	"""

def send_payout_confirmation_email(active_lead, ledger):
	seller = frappe.get_doc("Counterparty Profile", ledger.seller_profile) if ledger.seller_profile else None
	stock = frappe.get_doc("Unlisted Stock", ledger.stock) if ledger.stock else None
	
	if not (seller and seller.email):
		return
		
	subject = f"Payment Released — {ledger.name} | {stock.company_name if stock else ledger.stock}"
	
	message = f"""
	<p>Dear {seller.entity_name},</p>
	<p>We're pleased to confirm that payment of ₹{'{:,.2f}'.format(ledger.seller_gross_cost or 0)} against Deal ID {ledger.name} 
	({stock.company_name if stock else ledger.stock}, {int(ledger.quantity or 0)} shares @ ₹{'{:,.2f}'.format(ledger.seller_rate or 0)}) has been remitted to your registered 
	bank account today, {frappe.utils.formatdate(frappe.utils.today(), "dd-mm-yyyy")}.</p>
	
	<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 600px;">
		<tr><td style="width: 40%; background-color: #f8fafc;"><b>Particulars</b></td><td style="background-color: #f8fafc;"><b>Details</b></td></tr>
		<tr><td>Deal ID</td><td>{ledger.name}</td></tr>
		<tr><td>Amount Paid</td><td>₹{'{:,.2f}'.format(ledger.seller_gross_cost or 0)}</td></tr>
		<tr><td>Mode</td><td>RTGS / NEFT / IMPS</td></tr>
		<tr><td>UTR / Reference No.</td><td></td></tr>
		<tr><td>Paid to A/c No.</td><td>{ledger.seller_bank_account or ''}</td></tr>
	</table>
	<br>
	<p>Kindly confirm receipt at your end, and please initiate the share transfer to our DEMAT account 
	(details below) at the earliest so we can complete the delivery leg.</p>
	
	<p><b>Our DEMAT Details: DP ID [OMV DP ID] | Client ID [OMV Client ID] | [OMV Depository]</b></p>
	
	<p>Thank you for the smooth transaction.</p>
	<p>Best Regards,<br>
	<b>Off Market Venture</b></p>
	"""
	
	frappe.sendmail(
		recipients=[seller.email],
		subject=subject,
		message=message,
		reference_doctype="Active Leads",
		reference_name=active_lead.name
	)

def send_shares_followup_email(active_lead, ledger):
	seller = frappe.get_doc("Counterparty Profile", ledger.seller_profile) if ledger.seller_profile else None
	stock = frappe.get_doc("Unlisted Stock", ledger.stock) if ledger.stock else None
	
	if not (seller and seller.email):
		return
		
	subject = f"Reminder — Share Transfer Pending | {ledger.name} | {stock.company_name if stock else ledger.stock}"
	
	message = f"""
	<p>Dear {seller.entity_name},</p>
	<p>As per Deal ID {ledger.name}, we have already released payment of ₹{'{:,.2f}'.format(ledger.seller_gross_cost or 0)} on 
	{frappe.utils.formatdate(frappe.utils.today(), "dd-mm-yyyy")} for {int(ledger.quantity or 0)} shares of {stock.company_name if stock else ledger.stock}.</p>
	
	<p>We note that the shares are yet to reflect in our DEMAT account. Kindly arrange the transfer at the 
	earliest, as any delay affects our delivery commitment to the buyer.</p>
	
	<p><b>Transfer to: DP ID [OMV DP ID] · Client ID [OMV Client ID] · Depository [OMV Depository]</b></p>
	
	<p>Please share the delivery instruction slip (DIS) or transfer confirmation/UTR once initiated so we can 
	track it on our end.</p>
	
	<p>Do let us know if you're facing any issue with the transfer — happy to assist.</p>
	
	<p>Best Regards,<br>
	<b>Off Market Venture</b></p>
	"""
	
	frappe.sendmail(
		recipients=[seller.email],
		subject=subject,
		message=message,
		reference_doctype="Active Leads",
		reference_name=active_lead.name
	)

def send_buyer_payment_reminder_email(active_lead, ledger):
	buyer = frappe.get_doc("Counterparty Profile", ledger.buyer_profile) if ledger.buyer_profile else None
	stock = frappe.get_doc("Unlisted Stock", ledger.stock) if ledger.stock else None
	bank = frappe.get_doc("Company Receiving Bank", ledger.company_receiving_bank) if ledger.company_receiving_bank else None
	
	if not (buyer and buyer.email):
		return
		
	subject = f"Payment Reminder — {ledger.name} | {stock.company_name if stock else ledger.stock} | Due ₹{'{:,.2f}'.format(ledger.total_net_due or 0)}"
	
	message = f"""
	<p>Dear {buyer.entity_name},</p>
	<p>This is a gentle reminder that payment against Deal ID {ledger.name} ({stock.company_name if stock else ledger.stock}, {int(ledger.quantity or 0)} 
	shares @ ₹{'{:,.2f}'.format(ledger.buyer_rate or 0)}) is currently pending.</p>
	
	<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 600px;">
		<tr><td style="width: 40%; background-color: #f8fafc;"><b>Particulars</b></td><td style="background-color: #f8fafc;"><b>Details</b></td></tr>
		<tr><td>Deal ID</td><td>{ledger.name}</td></tr>
		<tr><td>Total Amount Due</td><td>₹{'{:,.2f}'.format(ledger.total_net_due or 0)}</td></tr>
		<tr><td>Includes</td><td>Stamp Duty ₹{'{:,.2f}'.format(ledger.stamp_duty or 0)} + TCS ₹{'{:,.2f}'.format(ledger.tcs_value or 0)}</td></tr>
		<tr><td>Payment Due Date</td><td>Immediate</td></tr>
	</table>
	<br>
	<p><b>Please remit to: {bank.bank_name if bank else '[Bank Name]'} · A/c No. {bank.account_no if bank else '[Account No]'} · IFSC {bank.ifsc if bank else '[IFSC]'} · Branch {bank.branch if bank else '[Branch]'}</b></p>
	
	<p>Once processed, kindly share the UTR/transaction reference so we can confirm receipt and proceed 
	with share delivery to your DEMAT account without delay.</p>
	
	<p>Please treat this as urgent to avoid any delay in settlement.</p>
	
	<p>Best Regards,<br>
	<b>Off Market Venture</b></p>
	"""
	
	frappe.sendmail(
		recipients=[buyer.email],
		subject=subject,
		message=message,
		reference_doctype="Active Leads",
		reference_name=active_lead.name
	)

def send_transaction_closed_email(active_lead, ledger):
	buyer = frappe.get_doc("Counterparty Profile", ledger.buyer_profile) if ledger.buyer_profile else None
	seller = frappe.get_doc("Counterparty Profile", ledger.seller_profile) if ledger.seller_profile else None
	stock = frappe.get_doc("Unlisted Stock", ledger.stock) if ledger.stock else None
	
	subject = f"Transaction Closed — {ledger.name} | {stock.company_name if stock else ledger.stock} | Thank You"
	
	message = f"""
	<p>Dear [Counterparty Name],</p>
	<p>We're glad to confirm that Deal ID {ledger.name} for {int(ledger.quantity or 0)} shares of {stock.company_name if stock else ledger.stock} has 
	been successfully closed — payment and share delivery are complete on both legs.</p>
	
	<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 600px;">
		<tr><td style="width: 40%; background-color: #f8fafc;"><b>Particulars</b></td><td style="background-color: #f8fafc;"><b>Details</b></td></tr>
		<tr><td>Deal ID</td><td>{ledger.name}</td></tr>
		<tr><td>Security</td><td>{stock.company_name if stock else ledger.stock} (ISIN: {ledger.isin_number or ''})</td></tr>
		<tr><td>Quantity</td><td>{int(ledger.quantity or 0)}</td></tr>
		<tr><td>Final Settlement Date</td><td>{frappe.utils.formatdate(frappe.utils.today(), "dd-mm-yyyy")}</td></tr>
	</table>
	<br>
	<p>Thank you for your trust and prompt cooperation throughout this transaction. We look forward to 
	working with you again on future opportunities in unlisted/pre-IPO shares.</p>
	
	<p>For any records or copies of the Deal Note, feel free to reach out anytime.</p>
	
	<p>Warm Regards,<br>
	<b>Anshul Bhardwaj</b><br>
	<b>Off Market Venture</b><br>
	Vasant Kunj, New Delhi – 110070<br>
	+91 99681 10807 · www.offmarketventure.co</p>
	"""
	
	if buyer and buyer.email:
		buyer_message = message.replace("[Counterparty Name]", buyer.entity_name)
		frappe.sendmail(
			recipients=[buyer.email],
			subject=subject,
			message=buyer_message,
			reference_doctype="Active Leads",
			reference_name=active_lead.name
		)

	if seller and seller.email:
		seller_message = message.replace("[Counterparty Name]", seller.entity_name)
		frappe.sendmail(
			recipients=[seller.email],
			subject=subject,
			message=seller_message,
			reference_doctype="Active Leads",
			reference_name=active_lead.name
		)

def send_shares_delivered_email(active_lead, ledger):
	buyer = frappe.get_doc("Counterparty Profile", ledger.buyer_profile) if ledger.buyer_profile else None
	stock = frappe.get_doc("Unlisted Stock", ledger.stock) if ledger.stock else None
	
	if not (buyer and buyer.email):
		return
		
	subject = f"Shares Delivered — {ledger.name} | {stock.company_name if stock else ledger.stock} | {int(ledger.quantity or 0)} Shares"
	
	message = f"""
	<p>Dear {buyer.entity_name},</p>
	<p>We're happy to confirm that {int(ledger.quantity or 0)} shares of {stock.company_name if stock else ledger.stock} (ISIN: {ledger.isin_number or ''}) against Deal 
	ID {ledger.name} have been transferred to your DEMAT account today, {frappe.utils.formatdate(frappe.utils.today(), "dd-mm-yyyy")}.</p>
	
	<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 600px;">
		<tr><td style="width: 40%; background-color: #f8fafc;"><b>Particulars</b></td><td style="background-color: #f8fafc;"><b>Details</b></td></tr>
		<tr><td>Deal ID</td><td>{ledger.name}</td></tr>
		<tr><td>Quantity Delivered</td><td>{int(ledger.quantity or 0)}</td></tr>
		<tr><td>Delivered to DP ID</td><td>{buyer.dp_id or ''}</td></tr>
		<tr><td>Client ID</td><td>{buyer.client_id or ''}</td></tr>
	</table>
	<br>
	<p>Please verify the credit in your holdings statement and let us know if you notice any discrepancy 
	within 48 hours.</p>
	
	<p>Thank you for choosing Off Market Venture for this transaction.</p>
	
	<p>Best Regards,<br>
	<b>Off Market Venture</b></p>
	"""
	
	frappe.sendmail(
		recipients=[buyer.email],
		subject=subject,
		message=message,
		reference_doctype="Active Leads",
		reference_name=active_lead.name
	)
