frappe.ui.form.on('Material Request', {
	refresh(frm) {
		// your code here
	}
	
});

frappe.ui.form.on('Material Request Item', {
	refresh(frm) {
		// your code here
	},
	item_code: function(frm,cdt,cdn){
	    var row = locals[cdt][cdn];
	    frappe.db.get_doc('Item', row.item_code)
            .then(doc => {
                console.log(doc)
                console.log(doc.item_defaults[0].default_supplier);
                row.supplier_name = doc.item_defaults[0].default_supplier;
                frm.doc.supplier =  doc.item_defaults[0].default_supplier;
                frm.refresh_field("items");
            });
	}
});