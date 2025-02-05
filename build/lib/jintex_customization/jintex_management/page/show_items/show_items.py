import frappe
import json
from frappe.utils import today

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
        cond += "and (i.item_name like '" + product_id + "' or i.description like '" + product_id + "' or i.bangalore_bin like '" + product_id + "' or i.ahmedabad_bin like '" + product_id + "' or i.aliases like '" + product_id + "')"
    
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
def send_material_request(product_id, qty):
    if frappe.db.exists('Material Request', {'material_request_type': 'Purchase', 'docstatus': 0}):
        req = frappe.db.get_value('Material Request', {'material_request_type': 'Purchase', 'docstatus': 0}, 'name')
        
        doc = frappe.get_doc('Material Request', req)

        flag = False
        for item in doc.items:
            if item.item_code == product_id:
                item.qty = item.qty + float(qty)
                flag = True
                break
        
        if flag == False:
            row = doc.append('items', {})
            row.item_code = product_id
            row.schedule_date = doc.schedule_date
            row.qty = qty
        
        doc.save()
        return "Success"
    else:
        doc = frappe.new_doc('Material Request')
        doc.material_request_type = "Purchase"
        row = doc.append('items', {})
        row.item_code = product_id
        row.schedule_date = today()
        row.qty = qty

        doc.insert()
        return "Success"


@frappe.whitelist()
def check_purchase_material(product_id):
    # data = frappe.db.sql("select sum(poi.qty) as qty from `tabPurchase Order Item` poi left join `tabPurchase Order` po on po.name = poi.parent where (po.status = 'To Receive and Bill' or po.status = 'To Receive') and poi.item_code = %s group by poi.item_code", (product_id), as_dict = True)
    data = frappe.db.sql("select (sum(mri.qty) - sum(mri.received_qty)) as qty from `tabMaterial Request Item` mri where mri.item_code = %s group by mri.item_code", (product_id), as_dict = True)


    if data:
        return data[0].qty
    else:
        return 0