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
		
		frm.add_custom_button(__("Get Items"), function() {
			if(frm.doc.item_group){
			    frappe.db.get_list('Item', {
                fields: ['item_code', 'item_group'],
                filters: {
                    'item_group': frm.doc.item_group
                    }
                }).then(records => {
                    console.log(records);
                    frm.clear_table("price_list");
                    frm.refresh_fields("price_list");
                    for(var i in records){
                        let row = frappe.model.add_child(frm.doc,"Price Update Tool Item","price_list");
                            row.model = records[i].item_group;
                            row.item_code = records[i].item_code;
                    }
                    frm.refresh_field('price_list');
                });
			}
			else{
                frappe.db.get_list('Item', {
                fields: ['item_code', 'item_group']
                }).then(records => {
                    console.log(records);
                    frm.clear_table("price_list");
                    frm.refresh_fields("price_list");
                    for(var i in records){
                        let row = frappe.model.add_child(frm.doc,"Price Update Tool Item","price_list");
                            row.model = records[i].item_group;
                            row.item_code = records[i].item_code;
                    }
                    frm.refresh_field('price_list');
                })
            }
			
		});

		frm.add_custom_button(__("Clear Table"),function(){
			frm.clear_table("price_list");
            frm.refresh_fields("price_list");
		});
	},
	item_search(frm){
		if(frm.doc.item_search){
		  frappe.db.get_list('Item', {
				fields: ['item_code', 'item_group'],
				filters: {
					'item_name': ["like","%"+frm.doc.item_search+"%"]
					}
				}).then(records => {
					console.log(records);
					frm.clear_table("price_list");
					frm.refresh_fields("price_list");
					for(var i in records){
						let row = frappe.model.add_child(frm.doc,"Price Update Tool Item","price_list");
							row.model = records[i].item_group;
							row.item_code = records[i].item_code;
					}
					frm.refresh_field('price_list');
				});
	  }
	}
});

frappe.ui.form.on('Price Update Tool Item', {
	rmb_price(frm,cdt,cdn){
	    var row = locals[cdt][cdn];
	    frappe.model.set_value(cdt,cdn,'cost',(row.conversion*row.rmb_price));
	    frm.refresh_field('price_list');
	    var rmb_triggers = ["dealer_conversion","prime_conversion","retail_conversion","north_conversion"]
          rmb_triggers.forEach(function(element){
            if(row[element]){
              frm.script_manager.trigger(element, cdt, cdn);
            }
          })
	    
	},
	conversion(frm,cdt,cdn){
	    var row = locals[cdt][cdn];
	    frappe.model.set_value(cdt,cdn,'cost',(row.conversion*row.rmb_price));
	    frm.refresh_field('price_list');
	},
	dealer_conversion:function (frm,cdt,cdn){
	    var row = locals[cdt][cdn];
	    frappe.model.set_value(cdt,cdn,'dealer_price',(row.dealer_conversion*row.rmb_price));
	    frm.refresh_field('price_list');
	    console.log('frm trigger')
	},
	prime_conversion(frm,cdt,cdn){
	    var row = locals[cdt][cdn];
	    frappe.model.set_value(cdt,cdn,'prime_price',(row.prime_conversion*row.rmb_price));
	    frm.refresh_field('price_list');
	},
	retail_conversion(frm,cdt,cdn){
	    var row = locals[cdt][cdn];
	    frappe.model.set_value(cdt,cdn,'retail',(row.retail_conversion*row.rmb_price));
	    frm.refresh_field('price_list');
	},
	north_conversion(frm,cdt,cdn){
	    var row = locals[cdt][cdn];
	    frappe.model.set_value(cdt,cdn,'north_price',(row.north_conversion*row.rmb_price));
	    frm.refresh_field('price_list');
	},
	cost(frm,cdt,cdn){
	    var row = locals[cdt][cdn];
	    frappe.model.set_value(cdt,cdn,'ahmedabad_prices',(row.cost*1.08));
	    frm.refresh_field('price_list');
	},
	
	
});
