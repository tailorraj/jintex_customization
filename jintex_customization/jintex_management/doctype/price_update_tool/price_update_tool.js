// Copyright (c) 2022, Raaj Tailor and contributors
// For license information, please see license.txt

frappe.ui.form.on('Price Update Tool', {
	refresh: function(frm) {
		frm.add_custom_button('Create Price List', 
		() => {
			console.log(frm.doc.price_list.length)
			if(frm.doc.price_list.length > 0){
				frappe.call({
					method: 'create_pricelist',
					doc: frm.doc,
					callback: function(res){
						console.log(res)
						if(res.message == 'Success'){
							frappe.msgprint("Price List Created Successfully")
						}
					}
				})
			}
			else{
				frappe.msgprint("No items in the table.")
			}
			// if(!frm.doc.price_list){
			// 	frappe.msgprint("Nothing Available")
			// }
			// else{
			// 	frappe.msgprint("Something Something")
			// }
		})
	}
});
