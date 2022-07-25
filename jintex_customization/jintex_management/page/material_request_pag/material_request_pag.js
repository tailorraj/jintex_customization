frappe.pages['material-request-pag'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Material Request Page',
		single_column: true
	});

	new erpnext.ShowItems(page);
}

erpnext.ShowItems = class StockQuery {
	constructor(page) {
		this.page = page;
		this.make_form();
	}

	make_form() {
		this.form = new frappe.ui.FieldGroup({
			fields: [
				{
					fieldtype: 'Section Break'
				},
				{
					label: __('Search'),
					fieldname: 'item_code',
					fieldtype: 'Data',
					change: async () => {
						this.fetch_and_render()
					},
				},
				{
					fieldtype: 'Column Break'
				},
				{
					label: __('Group'),
					fieldname: 'item_group',
					fieldtype: 'Link',
					options: 'Item Group',
					change: async () => {
						this.fetch_and_render()
					},
				},
				{
					fieldtype: 'Column Break'
				},
				{
					label: __('Category'),
					fieldname: 'category',
					fieldtype: 'Select',
					options: ['','A', 'B', 'C'],
					change: async () => {
						this.fetch_and_render()
					},
				},
				{
					fieldtype: 'Column Break'
				},
				{
					label: __('Supplier'),
					fieldname: 'supplier',
					fieldtype: 'Link',
					options: 'Supplier',
					change: async () => {
						this.fetch_and_render()
					},
				},
				{
					fieldtype: 'Section Break'
				},
				{
					label:"Item",
					fieldtype: 'HTML',
					fieldname: 'get_items'
				},
				{
					fieldtype: 'Section Break'
				},
			],
			body: this.page.body
		});
		this.form.make();
		this.fetch_and_render();
	}
	fetch_and_render(){
		var item_code = this.form.get_value("item_code");
		var item_group = this.form.get_value("item_group");
		var category = this.form.get_value("category");
		var supplier = this.form.get_value("supplier");
		this.set_items(item_code, item_group, category, supplier)
	}

	async set_items(item_code, item_group, category, supplier){

		var res = await get_items(item_code, item_group, category, supplier)
		console.log(res)

		

		var html_content = '';
		html_content += '<div class="card-deck" style= "margin-top: 10px">';
		
		
		var j = 0;
		res.message.forEach(i =>{
			if((j % 3) == 0 && j != 0){
				html_content += '</div>' + 
				'<div class="card-deck" style= "margin-top: 10px">';
			}

			var stk_blr = 0
			if(i.banglore != null){
				stk_blr = i.banglore
			}

			var blr_reorder = 0
			if(i.blr_reorder != null){
				blr_reorder = i.blr_reorder
			}


			html_content += '<div class="card mb-3" style="max-width: 380px;">' +
				'<img class="card-img-top rounded" style="height: 280px;object-fit: contain; margin-top:5px;border:white;border-style:solid" src="' + i.image + '" class="card-img" alt="...">' +
			'<div class="row no-gutters bg-light position-relative">' +
			  '<div class="col-md-12">' +
				'<div class="card-body">' +
				// '<h5 class="card-title"><a href="item/'+ i.name +'" class="stretched-link"><strong>' + i.item_name + '</strong></a></h5>' +
				'<h5 class="card-title"><a href="item/'+ i.name +'"><strong>' + i.item_name + '</strong></a></h5>' +
				'<h6 class="card-subtitle mb-2 text-muted">Group: <strong>' + i.item_group + '</strong></h6>' +
				'<h6 class="card-subtitle mb-2 text-muted">Category: <strong>' + i.category + '</strong></h6>' +
				'<p class="card-text border-top border-bottom border-dark"> <span style="display: inline-block;"><strong>Purchase: CNY '+ parseFloat(i.cny_rate).toFixed(2) +'</strong><br />' +
				'<strong>Cost: Rs ' + parseFloat(i.last_purchase_rate).toFixed(2) + '</strong></span>';
			if(blr_reorder <= stk_blr){
				html_content += '<span style="display: inline-block;padding-left: 65px;"><span style="color:#007500; font-weight: bold;">Stock: ' + parseInt(stk_blr) + ' Pcs </span></span></p>';
			}else{
				html_content += '<span style="display: inline-block;padding-left: 65px;"><span style="color:#FF0000; font-weight: bold;">Stock: ' +  parseInt(stk_blr) + ' Pcs </span></span></p>';
			}

			let require_by = '-'
			if(i.po_name != '-'){
				let sc_datetime = new Date(i.po_name)
				require_by = sc_datetime.getDate() + "-" + (sc_datetime.getMonth() + 1) + "-" + sc_datetime.getFullYear()
			}
			
			html_content += '<p class="card-text border-bottom border-dark">' + 
				'<span>Reorder Level: '+ parseInt(blr_reorder) +' Pcs</span> <br />' +
				'<span><strong>Transit Date: '+ require_by +'</strong></span> <br />' +
				'<span><strong>Transit Quantity: '+ parseInt(i.po_qty) +' Pcs</strong></span>' +
				'</p>' +
				'<p class="card-text">' + 
				'<span>Default Supplier: '+ i.default_supplier +'</span> <br />' +
				'<span>Last Vendor: '+ i.pi_supplier +'</span> <br />' +
				'<span>Last Quantity: '+ parseInt(i.pi_qty) +' Pcs</span>' +
				'</p>';


			
			html_content +=
				// '<p class="card-text"><span style="display: inline-block;">Dealer Price: <strong>Rs ' + i.dealer + '</strong><br />' +
				// 'Retail Price: <strong>Rs ' + i.retail + '</strong><br />Price3: <strong>Rs 0</strong></span><span style="display: inline-block; padding-left: 50px;">Transit Date: <strong>' + i.po_name + '</strong><br /> Transit Qty: <strong>' + i.po_qty + '</strong><br />' +
				// '<a href="item/'+ i.name +'" class="btn btn-primary stretched-link">View Item</a>' +
				'</div>' +
				'</div>' +
				'</div>' +
				'<div class="row no-gutters bg-light position-relative">' +
				'<div class="col-md-12" style="display: grid;">' +
				' <label for="req_qty" style="margin-left: 20px;">Enter Qty:</label>' +
				'<input type="text" class="req_id" name="'+ i.name +'" style="width: 50px;margin-left: 90px;margin-top: -32px;">' +
				'<button data-id="' + i.name + '" class="btn btn-primary btn-lg" onclick="get_req(this)" style="margin: 10px auto;margin-top: -40px;margin-right: 20px;">Request</button> '+
				// '<a style="display: block; margin:10px" data-id="' + i.name + '" class="req_btn btn btn-primary">Request</a>' +
				
				'</div>' +
			  '</div>' +
			// '</div>' +
		  '</div>';
			
			j += 1;
		})

		html_content += '</div>';
		html_content += '<button onclick="topFunction()" id="to_top" title="Go to top" style="position: fixed; bottom: 20px; right: 30px; z-index: 99; font-size: 18px; border: medium none; outline: currentcolor none medium; background-color: red; color: white; cursor: pointer; padding: 5px; border-radius: 4px; display: none;">Top</button>';
		html_content += '<script>' +
		//Get the button
		'var mybutton = document.getElementById("to_top");' +

		// When the user scrolls down 20px from the top of the document, show the button
		'window.onscroll = function() {scrollFunction()};' +

		'\n\nfunction scrollFunction() {' +
		'if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {' +
			'mybutton.style.display = "block";' +
		'} else {' +
			'mybutton.style.display = "none";' +
		'}' +
		'}' +

		// When the user clicks on the button, scroll to the top of the document
		'\n\nfunction topFunction() {' +
		'document.body.scrollTop = 0;' +
		'document.documentElement.scrollTop = 0;' +
		'}' +
		'</script>';


			// '<tr>' +
			// 	'<td>Temp</td>' +
			// 	'<td>Temp_Serial</td>' +
			// 	'<td>Temp Qty</td>' +
			// 	'<td>temp Res</td>' +
				
			// '</tr>';

		this.form.get_field('get_items').html(html_content);		
	}
}

function get_items(item, item_group, category, supplier) {
	return new Promise(function(resolve, reject){
		try{
			frappe.call({
				'method': 'jintex_customization.jintex_management.page.material_request_pag.material_request_pag.get_items',
				'args': {
					'product_id': item,
					'item_group': item_group,
					'category': category,
					'supplier': supplier
				},
				callback: resolve
			});
		} catch (e) {reject(e);}
	});
}

function get_req(elem){
	var item =  $(elem).data("id");
	var str_input = "input[name='"+ item +"']"
	var qty =  document.querySelector(str_input).value; 

	console.log(qty)
	// var qty =  $(elem).data("qty");
	// console.log(item + " - " + qty)
	let pending_qty = 0
	frappe.call({
		'method': 'jintex_customization.jintex_management.page.material_request_pag.material_request_pag.check_purchase_material',
		'args': {
			'product_id':item
		},
		'freeze': 1,
		callback: function(res){
			console.log(res)
			// pending_qty = res.message
			if(res.message > 0){
				// frappe.msgprint("Quantity to be Received: " + res.message)
				pending_qty = res.message;
				frappe.confirm('Quantity to be Received: '+ pending_qty +'! Do you still want to proceed?',
				() => {
					create_material_request(item, qty)
				}, () => {
					// action to perform if No is selected
					// frappe.msgprint("Clicked No")
				})
			}
			else{
				create_material_request(item, qty)
			}
		}
	})

	

	// let d = new frappe.ui.Dialog({
	// 	title: 'Enter Quantity',
	// 	fields: [
	// 		{
	// 			label: 'Qty',
	// 			fieldname: 'qty',
	// 			fieldtype: 'Int'
	// 		}
	// 	],
	// 	primary_action_label: 'Submit',
	// 	primary_action(values) {
	// 		console.log(values.qty);
	// 		if(values.qty != null && values.qty != 0){
	// 			try{
	// 				frappe.call({
	// 					'method': 'jintex_customization.jintex_management.page.show_items.show_items.send_material_request',
	// 					'args': {
	// 						'product_id': item,
	// 						'qty': values.qty,
	// 					},
	// 					callback: function(res){
	// 						// console.log(res.message)
	// 						if(res.message == "Success"){
	// 							frappe.msgprint("Material Request Created Successfully!")
	// 						}
	// 					}
	// 				});
	// 			} catch (e) {reject(e);}
	// 		}
	// 		d.hide();
	// 	}
	// });
	
	// d.show();

	// try{
	// 	frappe.call({
	// 		'method': 'jintex_customization.jintex_management.page.show_items.show_items.send_material_request',
	// 		'args': {
	// 			'product_id': item,
	// 			'qty': qty,
	// 		},
	// 		callback: function(res){
	// 			// console.log(res.message)
	// 			if(res.message == "Success"){
	// 				frappe.msgprint("Material Request Created Successfully!")
	// 			}
	// 		}
	// 	});
	// } catch (e) {reject(e);}
}

function create_material_request(item, qty){
	try{
		frappe.call({
			'method': 'jintex_customization.jintex_management.page.show_items.show_items.send_material_request',
			'args': {
				'product_id': item,
				'qty': qty,
			},
			callback: function(res){
				// console.log(res.message)
				if(res.message == "Success"){
					frappe.msgprint("Material Request Created Successfully!")
				}
			}
		});
	} catch (e) {reject(e);}
}