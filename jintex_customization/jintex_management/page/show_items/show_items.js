frappe.pages['show-items'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Inventory Report Card View',
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
		this.set_items(item_code, item_group, category)
	}

	async set_items(item_code, item_group, category){

		var res = await get_items(item_code, item_group, category)
		console.log(res)

		

		var html_content = '';
		html_content += '<div class="card-deck" style= "margin-top: 10px">';
		
		
		var j = 0;
		res.message.forEach(i =>{
			if((j % 3) == 0 && j != 0){
				html_content += '</div>' + 
				'<div class="card-deck" style= "margin-top: 10px">';
			}
			var stk_amd = 0
			if(i.ahmedabad != null){
				stk_amd = i.ahmedabad
			}

			var stk_blr = 0
			if(i.banglore != null){
				stk_blr = i.banglore
			}

			var blr_reorder = 0
			if(i.blr_reorder != null){
				blr_reorder = i.blr_reorder
			}

			var amd_reorder = 0
			if(i.amd_reorder != null){
				amd_reorder = i.amd_reorder
			}

			// html_content +=	'<div class="card" style="width: 18rem;">' +
			// 	'<div class="card-body">' +
			// 	'<div class="d-flex flex-center me-5 pt-2"><img src="'+ i.image +'" alt="" width="125" height="125"></div>' +
			// 	'<div class="d-flex flex-column content-justify-center w-100">' +
			// 	'<h5 class="card-title">' + i.item_name + '</h5>' +
			// 	'<h6 class="card-subtitle mb-2 text-muted">Group: ' + i.item_group + '</h6>' +
			// 	'<h6 class="card-subtitle mb-2 text-muted">Category: ' + i.category + '</h6>' +
			// 	'<h6 class="card-subtitle mb-2 text-muted">Reorder Level: 20 Pcs</h6>' +
			// 	'<p class="card-text"> ' + i.bangalore_bin + '<br />' +
			// 	'Retail Price: Stock: ' + stk_blr + ' Pcs</p>' +
			// 	'<p class="card-text"> ' + i.ahmedabad_bin + '<br />' +
			// 	'Retail Price: Stock: ' + stk_amd + ' Pcs</p>' +
			// 	'<p class="card-text">Dealer Price: Rs ' + i.dealer + '<br />' +
			// 	'Retail Price: Rs ' + i.retail + '</p>' +
			// 	'</div>' +
			// 	'</div>' +
			// '</div>';

			html_content += '<div class="card mb-3" style="max-width: 380px;">' +
			// '<div class="row no-gutters">' +
			//   '<div class="col-md-4" style="margin-top: auto; margin-bottom: auto; padding-left: 20px">' +
				'<img class="card-img-top rounded" style="height: 280px;object-fit: contain; margin-top:5px;border:white;border-style:solid " src="' + i.image + '" class="card-img" alt="...">' +
			//   '</div>' +
			'<div class="row no-gutters bg-light position-relative">' +
			  '<div class="col-md-12">' +
				'<div class="card-body">' +
				'<h5 class="card-title"><a href="item/'+ i.name +'" class="stretched-link"><strong>' + i.item_name + '</strong></a></h5>' +
				'<h6 class="card-subtitle mb-2 text-muted">Group: <strong>' + i.item_group + '</strong></h6>' +
				'<h6 class="card-subtitle mb-2 text-muted">Category: <strong>' + i.category + '</strong></h6>' +
				'<h6 class="card-subtitle mb-2 text-muted">Aliases: <strong>' + i.aliases + '</strong></h6>' +
				'<h6 class="card-subtitle mb-2 text-muted">Sales Invoice: <strong>' + i.si_date + '</strong></h6>' +
				// '<h6 class="card-subtitle mb-2 text-muted">BLR Reorder Level: ' + blr_reorder + ' Pcs</h6>' +
				// '<h6 class="card-subtitle mb-2 text-muted">AMD Reorder Level: ' + amd_reorder + ' Pcs</h6>' +
				// '<h6 class="card-subtitle mb-2 text-muted">Transit Date: <strong>' + i.po_name + '</strong></h6>' +
				'<p class="card-text border-top border-bottom border-dark"> <span style="display: inline-block;font-size: 14px;"><strong>' + i.bangalore_bin + '</strong><br />';
			
			if(stk_blr >= blr_reorder){
				html_content += 
				'<span style="color:#007500; font-weight: bold;font-size: 14px;">Stock: ' + parseInt(stk_blr) + ' Pcs </span>';
			}
			else{
				html_content += 
				'<span style="color:#FF0000; font-weight: bold;font-size: 14px;">Stock: ' + parseInt(stk_blr) + ' Pcs </span>';
			}
			
			
			html_content += 
				'<br />BLR Reorder: ' + parseInt(blr_reorder) + ' Pcs</span><span style="display: inline-block;padding-left: 65px;font-size: 14px;"><strong>' + i.ahmedabad_bin + '</strong><br />';

			if(stk_amd >= amd_reorder){
				html_content += 
				'<span style="color:#007500; font-weight: bold;font-size: 14px;">Stock: ' + parseInt(stk_amd) + ' Pcs </span>';
			}
			else{
				html_content += 
				'<span style="color:#FF0000; font-weight: bold;font-size: 14px;">Stock: ' + parseInt(stk_amd) + ' Pcs </span>';
			}

			let require_by = '-'
			if(i.po_name != '-'){
				let sc_datetime = new Date(i.po_name)
				require_by = sc_datetime.getDate() + "-" + (sc_datetime.getMonth() + 1) + "-" + sc_datetime.getFullYear()
			}
			
			html_content +=
				'<br />AMD Reorder: ' + parseInt(amd_reorder) + ' Pcs </span></p>' +
				'<p class="card-text"><span style="display: inline-block;">Dealer Price: <strong>Rs ' + parseFloat(i.dealer).toFixed(2) + '</strong><br />' +
				'Retail Price: <strong>Rs ' + parseFloat(i.retail).toFixed(2) + '</strong><br />Price3: <strong>Rs 0</strong></span><span style="display: inline-block; padding-left: 24px;">Transit Date: <strong>' + require_by + '</strong><br /> Transit Qty: <strong>' + parseInt(i.po_qty) + '</strong><br />' +
				// '<a href="item/'+ i.name +'" class="btn btn-primary stretched-link">View Item</a>' +
				'</div>' +
				'</div>' +
				'</div>' +
				'<div class="row no-gutters bg-light position-relative">' +
				'<div class="col-md-12" style="display: grid;">' +
				'<button data-id="' + i.name + '" data-qty="10" class="btn btn-primary btn-lg" onclick="get_req(this)" style="margin: 10px auto;">Request</button> '+
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

function get_items(item, item_group, category) {
	return new Promise(function(resolve, reject){
		try{
			frappe.call({
				'method': 'jintex_customization.jintex_management.page.show_items.show_items.get_items',
				'args': {
					'product_id': item,
					'item_group': item_group,
					'category': category,
				},
				callback: resolve
			});
		} catch (e) {reject(e);}
	});
}

function get_req(elem){
	var item =  $(elem).data("id");
	// var qty =  $(elem).data("qty");
	// console.log(item + " - " + qty)

	pending_qty = 0

	frappe.call({
		'method': 'jintex_customization.jintex_management.page.show_items.show_items.check_purchase_material',
		'args': {
			'product_id':item
		},
		callback: function(res){
			console.log(res)
			// pending_qty = res.message
			if(res.message != '0'){
				frappe.msgprint("Quantity to be Received: " + res.message)
			}
		}
	})

	let d = new frappe.ui.Dialog({
		title: 'Enter Quantity',
		fields: [
			{
				label: 'Qty',
				fieldname: 'qty',
				fieldtype: 'Int'
			}
		],
		primary_action_label: 'Submit',
		primary_action(values) {
			console.log(values.qty);
			if(values.qty != null && values.qty != 0){
				try{
					frappe.call({
						'method': 'jintex_customization.jintex_management.page.show_items.show_items.send_material_request',
						'args': {
							'product_id': item,
							'qty': values.qty,
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
			d.hide();
		}
	});
	
	d.show();

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