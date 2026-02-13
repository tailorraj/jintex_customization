import frappe

def get_context(context):
    context.no_cache = 1

@frappe.whitelist()
def get_items(product_id=None, item_group=None, category=None, offset=0, limit=15):
    dealer_pricelist = frappe.db.get_single_value('Jintex Configuration', 'dealer_pricelist')
    retail_pricelist = frappe.db.get_single_value('Jintex Configuration', 'retail_pricelist')
    pricelist_3 = frappe.db.get_single_value('Jintex Configuration', 'pricelist_3')
    bangalore_warehouse = frappe.db.get_single_value('Jintex Configuration', 'bangalore_warehouse')
    ahmedabad_warehouse = frappe.db.get_single_value('Jintex Configuration', 'ahmedabad_warehouse')

    cond = ""
    if product_id:
        product_id = '%' + product_id + '%'
        # cond += "and (i.item_name like '" + product_id + "' or i.description like '" + product_id + "' or i.bangalore_bin like '" + product_id + "' or i.ahmedabad_bin like '" + product_id + "' or i.aliases like '" + product_id + "')"
        cond += "and (i.item_name like '" + product_id + "' or i.description like '" + product_id + "' or i.bangalore_bin like '" + product_id + "' or i.ahmedabad_bin like '" + product_id + "' or i.aliases like '" + product_id + "' or i.jintex_item_codes like '" + product_id + "')"
    
    if item_group:
        cond += " and" 
        cond += " i.item_group = '" + item_group + "'"
    
    if category:
        cond += " and" 
        cond += " i.category = '" + category + "'"


    return frappe.db.sql("""
        select
        i.name,
        i.item_name,
        i.jintex_item_codes,
        IFNULL(i.item_group, '-') as item_group,
        IFNULL(i.category, '-') as category,
        IFNULL(i.aliases, '-') as aliases,
        IFNULL(i.bangalore_bin, '-') as bangalore_bin,
        IFNULL(i.ahmedabad_bin, '-') as ahmedabad_bin,
        i.image,
        IFNULL((select ip.price_list_rate from `tabItem Price` ip where ip.price_list = '%(dealer_pricelist)s' and ip.item_code = i.name order by ip.creation desc limit 1), '0') as dealer,
        IFNULL((select ip.price_list_rate from `tabItem Price` ip where ip.price_list = '%(retail_pricelist)s' and ip.item_code = i.name  order by ip.creation desc limit 1), '0') as retail,
        IFNULL((select ip.price_list_rate from `tabItem Price` ip where ip.price_list = '%(price3_pricelist)s' and ip.item_code = i.name  order by ip.creation desc limit 1), '0') as price3,
        IFNULL((select b.actual_qty from `tabBin` b where b.warehouse = '%(bangalore_warehouse)s' and b.item_code = i.name  order by b.creation desc limit 1), '0') as banglore,
        IFNULL((select b.actual_qty from `tabBin` b where b.warehouse = '%(ahmedabad_warehouse)s' and b.item_code = i.name order by b.creation desc limit 1), '0') as ahmedabad,
        IFNULL((select ir.warehouse_reorder_level from `tabItem Reorder` ir where ir.parent = i.name and ir.warehouse = '%(bangalore_warehouse)s'), '0') as blr_reorder,
        IFNULL((select ir.warehouse_reorder_level from `tabItem Reorder` ir where ir.parent = i.name and ir.warehouse = '%(ahmedabad_warehouse)s'), '0') as amd_reorder,
        IFNULL((select po.schedule_date from `tabPurchase Order Item` poi left join `tabPurchase Order` po on poi.parent = po.name where (po.status = 'To Receive' or po.status = 'To Receive and Bill') and poi.item_code = i.name order by po.creation desc limit 1), '-') as po_name,
        IFNULL((select poi.qty from `tabPurchase Order Item` poi left join `tabPurchase Order` po on poi.parent = po.name where (po.status = 'To Receive' or po.status = 'To Receive and Bill') and poi.item_code = i.name order by po.creation desc limit 1), '0') as po_qty,
        IFNULL((select si.posting_date from `tabSales Invoice Item` sii left join `tabSales Invoice` si on sii.parent = si.name where si.docstatus = 1 and sii.item_code = i.name order by si.creation desc limit 1), '-') as si_date
        from
        `tabItem` i
        where
        i.disabled = 0
        %(cond)s
        limit %(limit)s offset %(offset)s
        """ % {"dealer_pricelist":dealer_pricelist, "retail_pricelist":retail_pricelist, "price3_pricelist": pricelist_3, "bangalore_warehouse":bangalore_warehouse, "ahmedabad_warehouse":ahmedabad_warehouse, "cond":cond, "offset":offset, "limit": limit},as_dict = True)

@frappe.whitelist()
def get_price_lists():
    """Get price lists from Jintex Configuration"""
    dealer_pricelist = frappe.db.get_single_value('Jintex Configuration', 'dealer_pricelist')
    retail_pricelist = frappe.db.get_single_value('Jintex Configuration', 'retail_pricelist')
    pricelist_3 = frappe.db.get_single_value('Jintex Configuration', 'pricelist_3')
    
    user = frappe.session.user
    user_roles = frappe.get_roles(user)
    
    # Build price list array
    price_lists = []
    
    # Admin sees all
    if "System Manager" in user_roles or "Administrator" in user_roles:
        if dealer_pricelist:
            price_lists.append({"name": "dealer", "price_list_name": "Dealer", "field": "dealer"})
        if retail_pricelist:
            price_lists.append({"name": "retail", "price_list_name": "Retail", "field": "retail"})
        if pricelist_3:
            price_lists.append({"name": "price3", "price_list_name": "Price List 3", "field": "price3"})
    else:
        # Custom logic: Example - Ahmedabad users see only Dealer and Inclusive
        # Modify this based on your permission logic
        user_location = frappe.db.get_value("User", user, "location")
        
        if user_location == "Ahmedabad":
            if dealer_pricelist:
                price_lists.append({"name": "dealer", "price_list_name": "Dealer", "field": "dealer"})
            if retail_pricelist:
                price_lists.append({"name": "retail", "price_list_name": "Inclusive", "field": "retail"})
        else:
            # Default: show all available
            if dealer_pricelist:
                price_lists.append({"name": "dealer", "price_list_name": "Dealer", "field": "dealer"})
            if retail_pricelist:
                price_lists.append({"name": "retail", "price_list_name": "Retail", "field": "retail"})
            if pricelist_3:
                price_lists.append({"name": "price3", "price_list_name": "Price List 3", "field": "price3"})
    
    return price_lists

@frappe.whitelist()
def get_item_groups():
    """Get item groups for filtering"""
    return frappe.db.sql("""
        SELECT DISTINCT item_group as name, item_group as item_group_name
        FROM `tabItem`
        WHERE disabled = 0 AND item_group IS NOT NULL
        ORDER BY item_group
    """, as_dict=1)

@frappe.whitelist()
def get_categories():
    """Get categories for filtering"""
    return frappe.db.sql("""
        SELECT DISTINCT category as name, category as category_name
        FROM `tabItem`
        WHERE disabled = 0 AND category IS NOT NULL
        ORDER BY category
    """, as_dict=1)

@frappe.whitelist()
def create_sales_order(items, customer, remarks=""):
    """Create sales order from POS cart"""
    import json
    if isinstance(items, str):
        items = json.loads(items)
    
    # Validate customer
    if not customer:
        frappe.throw("Please select a customer")
    
    # Get actual price list name based on type
    price_list_map = {
        "dealer": frappe.db.get_single_value('Jintex Configuration', 'dealer_pricelist'),
        "retail": frappe.db.get_single_value('Jintex Configuration', 'retail_pricelist'),
        "price3": frappe.db.get_single_value('Jintex Configuration', 'pricelist_3')
    }
    
    doc = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": customer,
        "delivery_date": frappe.utils.add_days(frappe.utils.today(), 7),
        "items": [
            {
                "item_code": item.get("item_code"),
                "item_name": item.get("item_name"),
                "qty": item.get("qty", 1),
                "rate": item.get("amount", 0),
                "uom": item.get("uom", "Nos"),
                "description": item.get("remarks", "")
            }
            for item in items
        ]
    })
    
    doc.insert()
    doc.submit()
    
    return {
        "name": doc.name,
        "grand_total": doc.grand_total
    }

@frappe.whitelist()
def get_customers(search_term=""):
    """Search customers for POS"""
    conditions = "disabled = 0"
    
    if search_term:
        search_term = f"%{search_term}%"
        conditions += " AND (name LIKE %(search)s OR customer_name LIKE %(search)s)"
    
    return frappe.db.sql(f"""
        SELECT name, customer_name, customer_group, territory
        FROM `tabCustomer`
        WHERE {conditions}
        ORDER BY customer_name
        LIMIT 20
    """, {"search": search_term}, as_dict=1)

@frappe.whitelist()
def can_see_purchase_price():
    """Check if current user can see purchase prices"""
    user = frappe.session.user
    user_roles = frappe.get_roles(user)
    
    # Define roles that can see purchase prices
    allowed_roles = [
        "System Manager",
        "Administrator", 
        "Accounts Manager",
        "Purchase Manager",
        "Stock Manager"
    ]
    
    return any(role in user_roles for role in allowed_roles)