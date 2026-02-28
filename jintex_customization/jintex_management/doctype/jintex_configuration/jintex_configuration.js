// Copyright (c) 2022, Raaj Tailor and contributors
// For license information, please see license.txt

frappe.ui.form.on('Jintex Configuration', {
	update_items: function(frm) {
		if (!frm.doc.enable_renaming)
			return;

		frappe.confirm(
			`This will rename all items in the background:<br><br>
			<ul>
				<li><strong>Item Name</strong> will be set to current Item Code</li>
				<li><strong>Item Code</strong> will be set to Jintex Item Code</li>
			</ul>
			<br>
			Progress will be logged in Error Log. Continue?`,
			() => {
				frappe.call({
					method: 'jintex_customization.jintex_management.doctype.jintex_configuration.jintex_configuration.start_item_rename_job',
					freeze: true,
					freeze_message: 'Starting background job...',
					callback: (r) => {
						if (r.message && r.message.success) {
							frappe.msgprint({
								title: __('Job Started'),
								indicator: 'green',
								message: __(r.message.message)
							});
							
							frappe.show_alert({
								message: __('Background job started. Check Error Log for progress.'),
								indicator: 'green'
							}, 5);
							
							// Optional: Open Error Log
							setTimeout(() => {
								frappe.set_route('List', 'Error Log', {
									'error': ['like', '%Item Rename%']
								});
							}, 2000);
						}
					},
					error: (r) => {
						frappe.msgprint({
							title: __('Error'),
							indicator: 'red',
							message: __('Failed to start background job. Please try again.')
						});
					}
				});
			}
		);
	}

});
