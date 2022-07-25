frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
		// your code here
	},
	validate(frm){
	   let arr1 = frm.doc.items;
	   
	   const result = [];
	   arr1.forEach(function (a) {
            if ( !this[a.item_group]) {
                this[a.item_group] = { item_group: a.item_group, qty: 0, amount: 0 };
                result.push(this[a.item_group]);
            } 
            this[a.item_group].qty += a.qty;
            this[a.item_group].amount += a.amount;
        }, Object.create(null));

        console.log(result);
        cur_frm.clear_table("calculation_of_item_group_");
        cur_frm.refresh_fields("calculation_of_item_group_");
        for (var i in result){
            console.log(result[i].item_group);
            
            var newrow = frappe.model.add_child(frm.doc, "Item Wise Calculation", "calculation_of_item_group_");
            newrow.item_group = result[i].item_group;
            newrow.total_quantity = result[i].qty;
            newrow.total_amount = result[i].amount;
        }
            cur_frm.script_manager.trigger("validate", newrow.doctype, newrow.name);
            frm.refresh_field('calculation_of_item_group_');
        
	 
	}
	
	
});

frappe.ui.form.on('Sales Invoice Item', {
	refresh(frm) {
		// your code here
	},
	
});