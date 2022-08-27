# Copyright (c) 2022, Raaj Tailor and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today

class PriceUpdateTool(Document):
	@frappe.whitelist()
	def create_pricelist(self):
		dealer = "Selling Price 1 (Dealer)"
		retail = "Selling Price 2 (Retail)"
		price3 = "Selling Price 3 (Branch)"
		for item in self.price_list:
			count = 1
			while count <= 3:
				if count == 1:
					price_list = dealer
					rate = item.dealer_price
				elif count == 2:
					price_list = retail
					rate = item.retail
				elif count == 3:
					price_list = price3
					rate = item.pricelist3

				if frappe.db.exists("Item Price", {"item_code": item.item_code, "price_list": price_list}):
					ip_id = frappe.db.get_value("Item Price", {"item_code": item.item_code, "price_list": price_list}, 'name')
					frappe.db.set_value("Item Price", ip_id, 'valid_upto', today())

				new_itemprice = frappe.new_doc("Item Price")
				new_itemprice.item_code = item.item_code
				new_itemprice.price_list = price_list
				new_itemprice.price_list_rate = rate
				new_itemprice.valid_from = today()
				new_itemprice.save(ignore_permissions = True)

				count = count + 1

		frappe.msgprint("All Price List added Successfully!")
