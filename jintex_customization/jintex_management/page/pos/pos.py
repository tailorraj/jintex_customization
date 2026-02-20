import frappe

def get_context(context):
    context.no_cache = 1

@frappe.whitelist()
def get_items(product_id=None, item_group=None, category=None, offset=0, limit=15):
    dealer_pricelist = frappe.db.get_single_value('Jintex Configuration', 'dealer_pricelist')
    retail_pricelist = frappe.db.get_single_value('Jintex Configuration', 'retail_pricelist')
    pricelist_3 = frappe.db.get_single_value('Jintex Configuration', 'pricelist_3')
    prime_pricelist = frappe.db.get_single_value('Jintex Configuration', 'prime')
    purchase_pricelist = frappe.db.get_single_value('Jintex Configuration', 'purchase_pricelist')
    

    bangalore_warehouse = frappe.db.get_single_value('Jintex Configuration', 'bangalore_warehouse')
    ahmedabad_warehouse = frappe.db.get_single_value('Jintex Configuration', 'ahmedabad_warehouse')
    conditions = ["i.disabled = 0"]
    values = {
        "purchase_pricelist": purchase_pricelist,
        "prime_pricelist": prime_pricelist,
        "dealer_pricelist": dealer_pricelist,
        "retail_pricelist": retail_pricelist,
        "price3_pricelist": pricelist_3,
        "bangalore_warehouse": bangalore_warehouse,
        "ahmedabad_warehouse": ahmedabad_warehouse,
        "limit": int(limit),
        "offset": int(offset),
    }

    if product_id:
        # Use % as wildcards within the value, not the SQL string
        safe_product_id = product_id.replace("\\", "\\\\")
        search_val = f"%{safe_product_id}%"
        
        values["search_val"] = search_val
        
        # Build the OR conditions
        product_cond = """
            (i.item_name LIKE %(search_val)s 
            OR i.description LIKE %(search_val)s 
            OR i.bangalore_bin LIKE %(search_val)s 
            OR i.ahmedabad_bin LIKE %(search_val)s 
            OR i.aliases LIKE %(search_val)s 
            OR REPLACE(i.aliases, '-', '') LIKE %(search_val)s 
            OR REPLACE(i.aliases, '-', ' ') LIKE %(search_val)s 
            OR i.jintex_item_codes LIKE %(search_val)s 
            OR REPLACE(i.jintex_item_codes, '-', '') LIKE %(search_val)s 
            OR REPLACE(i.jintex_item_codes, '-', ' ') LIKE %(search_val)s)
        """
        conditions.append(product_cond)

    if item_group:
        conditions.append("i.item_group = %(item_group)s")
        values["item_group"] = item_group

    if category:
        conditions.append("i.category = %(category)s")
        values["category"] = category

    # Join conditions with AND
    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            i.name,
            i.item_name,
            i.jintex_item_codes,
            IFNULL(i.item_group, '-') AS item_group,
            IFNULL(i.category, '-') AS category,
            IFNULL(i.aliases, '-') AS aliases,
            IFNULL(i.bangalore_bin, '-') AS bangalore_bin,
            IFNULL(i.ahmedabad_bin, '-') AS ahmedabad_bin,
            i.image,
            IFNULL((SELECT ip.price_list_rate FROM `tabItem Price` ip WHERE ip.price_list = %(purchase_pricelist)s AND ip.item_code = i.name ORDER BY ip.creation DESC LIMIT 1), 0) AS purchase,
            IFNULL((SELECT ip.price_list_rate FROM `tabItem Price` ip WHERE ip.price_list = %(dealer_pricelist)s AND ip.item_code = i.name ORDER BY ip.creation DESC LIMIT 1), 0) AS dealer,
            IFNULL((SELECT ip.price_list_rate FROM `tabItem Price` ip WHERE ip.price_list = %(prime_pricelist)s AND ip.item_code = i.name ORDER BY ip.creation DESC LIMIT 1), 0) AS prime,
            IFNULL((SELECT ip.price_list_rate FROM `tabItem Price` ip WHERE ip.price_list = %(retail_pricelist)s AND ip.item_code = i.name ORDER BY ip.creation DESC LIMIT 1), 0) AS retail,
            IFNULL((SELECT ip.price_list_rate FROM `tabItem Price` ip WHERE ip.price_list = %(price3_pricelist)s AND ip.item_code = i.name ORDER BY ip.creation DESC LIMIT 1), 0) AS inclusive,
            IFNULL((SELECT b.actual_qty FROM `tabBin` b WHERE b.warehouse = %(bangalore_warehouse)s AND b.item_code = i.name ORDER BY b.creation DESC LIMIT 1), 0) AS banglore,
            IFNULL((SELECT b.actual_qty FROM `tabBin` b WHERE b.warehouse = %(ahmedabad_warehouse)s AND b.item_code = i.name ORDER BY b.creation DESC LIMIT 1), 0) AS ahmedabad,
            IFNULL((SELECT ir.warehouse_reorder_level FROM `tabItem Reorder` ir WHERE ir.parent = i.name AND ir.warehouse = %(bangalore_warehouse)s), 0) AS blr_reorder,
            IFNULL((SELECT ir.warehouse_reorder_level FROM `tabItem Reorder` ir WHERE ir.parent = i.name AND ir.warehouse = %(ahmedabad_warehouse)s), 0) AS amd_reorder,
            IFNULL((SELECT po.schedule_date FROM `tabPurchase Order Item` poi LEFT JOIN `tabPurchase Order` po ON poi.parent = po.name WHERE (po.status IN ('To Receive', 'To Receive and Bill')) AND poi.item_code = i.name ORDER BY po.creation DESC LIMIT 1), '-') AS po_name,
            IFNULL((SELECT poi.qty FROM `tabPurchase Order Item` poi LEFT JOIN `tabPurchase Order` po ON poi.parent = po.name WHERE (po.status IN ('To Receive', 'To Receive and Bill')) AND poi.item_code = i.name ORDER BY po.creation DESC LIMIT 1), 0) AS po_qty,
            IFNULL((SELECT si.posting_date FROM `tabSales Invoice Item` sii LEFT JOIN `tabSales Invoice` si ON sii.parent = si.name WHERE si.docstatus = 1 AND sii.item_code = i.name ORDER BY si.creation DESC LIMIT 1), '-') AS si_date
        FROM
            `tabItem` i
        WHERE
            {where_clause}
        LIMIT %(limit)s OFFSET %(offset)s
    """

    return frappe.db.sql(query, values, as_dict=True)

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
    """Search customers for POS by Name, ID, or Mobile Number (SQLi Protected)"""
    # Initialize base conditions
    conditions = ["disabled = 0"]
    values = {}
    
    if search_term:
        # The database driver handles escaping for this value
        values["search"] = f"%{search_term}%"
        
        # Define the search logic across multiple fields
        search_logic = """(
            name LIKE %(search)s 
            OR customer_name LIKE %(search)s 
            OR mobile_no LIKE %(search)s
        )"""
        conditions.append(search_logic)
    
    # Safely join conditions with AND
    where_clause = " AND ".join(conditions)
    
    # Values dictionary ensures all inputs are escaped and quoted correctly by the driver
    return frappe.db.sql(f"""
        SELECT 
            name, 
            customer_name, 
            customer_group, 
            territory,
            mobile_no
        FROM `tabCustomer`
        WHERE {where_clause}
        ORDER BY customer_name
        LIMIT 20
    """, values, as_dict=1)

@frappe.whitelist()
def quick_create_customer(customer_name, mobile_no):
    """Creates a new customer and returns the document"""
    # Check if mobile already exists to avoid duplicates
    existing_customer = frappe.db.get_value("Customer", {"mobile_no": mobile_no}, "name")
    if existing_customer:
        return frappe.get_doc("Customer", existing_customer)
        
    doc = frappe.new_doc("Customer")
    doc.customer_name = customer_name
    doc.mobile_no = mobile_no
    doc.customer_type = "Individual"
    doc.customer_group = "All Customer Groups"
    doc.territory = "All Territories"
    doc.insert(ignore_mandatory=True)
    
    return doc

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