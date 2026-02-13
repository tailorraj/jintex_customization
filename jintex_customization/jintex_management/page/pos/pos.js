frappe.pages['pos'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Point of Sale',
		single_column: true
	});
}
frappe.pages["pos"].on_page_show = function (wrapper) {
	load_pos_ui(wrapper);
};

function load_pos_ui(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	// Add full width class to page
	$(wrapper).find(".page-content").addClass("pos-full-width");

	frappe.require("pos.bundle.js").then(() => {
		new pos.ui.POSUI({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}
