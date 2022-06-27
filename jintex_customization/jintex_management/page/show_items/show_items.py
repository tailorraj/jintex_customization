import frappe
import json
from frappe.utils import today

@frappe.whitelist()
def get_items(product_id=None, item_group=None, category=None):
    dealer_pricelist = frappe.db.get_single_value('Jintex Configuration', 'dealer_pricelist')
    retail_pricelist = frappe.db.get_single_value('Jintex Configuration', 'retail_pricelist')
    bangalore_warehouse = frappe.db.get_single_value('Jintex Configuration', 'bangalore_warehouse')
    ahmedabad_warehouse = frappe.db.get_single_value('Jintex Configuration', 'ahmedabad_warehouse')

    cond = ""
    if product_id:
        product_id = '%' + product_id + '%'
        cond += "where (i.item_name like '" + product_id + "' or i.description like '" + product_id + "' or i.bangalore_bin like '" + product_id + "' or i.ahmedabad_bin like '" + product_id + "' or i.aliases like '" + product_id + "')"
    
    if item_group:
        if cond == "":
            cond = "where"
        else:
            cond += " and" 
        cond += " i.item_group = '" + item_group + "'"
    
    if category:
        if cond == "":
            cond = "where"
        else:
            cond += " and" 
        cond += " i.category = '" + category + "'"


    return frappe.db.sql("""
        select
        i.name,
        i.item_name,
        i.item_group,
        i.category,
        i.aliases,
        i.bangalore_bin,
        i.ahmedabad_bin,
        i.image,
        (select ip.price_list_rate from `tabItem Price` ip where ip.price_list = '%(dealer_pricelist)s' and ip.item_code = i.name order by ip.creation desc limit 1) as dealer,
        (select ip.price_list_rate from `tabItem Price` ip where ip.price_list = '%(retail_pricelist)s' and ip.item_code = i.name  order by ip.creation desc limit 1) as retail,
        (select b.actual_qty from `tabBin` b where b.warehouse = '%(bangalore_warehouse)s' and b.item_code = i.name  order by b.creation desc limit 1) as banglore,
        (select b.actual_qty from `tabBin` b where b.warehouse = '%(ahmedabad_warehouse)s' and b.item_code = i.name order by b.creation desc limit 1) as ahmedabad,
        (select ir.warehouse_reorder_level from `tabItem Reorder` ir where ir.parent = i.name and ir.warehouse = '%(bangalore_warehouse)s') as blr_reorder,
        (select ir.warehouse_reorder_level from `tabItem Reorder` ir where ir.parent = i.name and ir.warehouse = '%(ahmedabad_warehouse)s') as amd_reorder,
        (select po.transaction_date from `tabPurchase Order Item` poi left join `tabPurchase Order` po on poi.parent = po.name where (po.status = 'To Receive' or po.status = 'To Receive and Bill') and poi.item_code = i.name order by po.creation desc limit 1) as po_name,
        (select poi.qty from `tabPurchase Order Item` poi left join `tabPurchase Order` po on poi.parent = po.name where (po.status = 'To Receive' or po.status = 'To Receive and Bill') and poi.item_code = i.name order by po.creation desc limit 1) as po_qty,
        (select si.posting_date from `tabSales Invoice Item` sii left join `tabSales Invoice` si on sii.parent = si.name where si.docstatus = 1 and sii.item_code = i.name order by si.creation desc limit 1) as si_date
        from
        `tabItem` i
        %(cond)s limit 12
        """ % {"dealer_pricelist":dealer_pricelist, "retail_pricelist":retail_pricelist, "bangalore_warehouse":bangalore_warehouse, "ahmedabad_warehouse":ahmedabad_warehouse, "cond":cond},as_dict = True)

@frappe.whitelist()
def send_material_request(product_id, qty):
    doc = frappe.new_doc('Material Request')
    doc.material_request_type = "Purchase"
    row = doc.append('items', {})
    row.item_code = product_id
    row.schedule_date = today()
    row.qty = qty

    doc.insert()
    return "Success"