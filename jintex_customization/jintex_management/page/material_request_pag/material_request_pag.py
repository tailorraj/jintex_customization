import frappe
import json
from frappe.utils import today

@frappe.whitelist()
def get_items(product_id=None, item_group=None, category=None, supplier=None, offset=0):
    bangalore_warehouse = frappe.db.get_single_value('Jintex Configuration', 'bangalore_warehouse')

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

    if supplier:
        cond += " and" 
        cond += " id.default_supplier = '" + supplier + "'"


    return frappe.db.sql("""
        select
        i.name,
        i.item_name,
        IFNULL(i.item_group, '-') as item_group,
        IFNULL(i.category, '-') as category,
        i.image,
        IFNULL(id.default_supplier, '-') as default_supplier,
        IFNULL((select b.actual_qty from `tabBin` b where b.warehouse = '%(bangalore_warehouse)s' and b.item_code = i.name  order by b.creation desc limit 1), '0') as banglore,
        (select ir.warehouse_reorder_level from `tabItem Reorder` ir where ir.parent = i.name and ir.warehouse = '%(bangalore_warehouse)s') as blr_reorder,
        IFNULL((select po.schedule_date from `tabPurchase Order Item` poi left join `tabPurchase Order` po on poi.parent = po.name where (po.status = 'To Receive' or po.status = 'To Receive and Bill') and poi.item_code = i.name order by po.creation desc limit 1), '-') as po_name,
        IFNULL((select poi.qty from `tabPurchase Order Item` poi left join `tabPurchase Order` po on poi.parent = po.name where (po.status = 'To Receive' or po.status = 'To Receive and Bill') and poi.item_code = i.name order by po.creation desc limit 1), '0') as po_qty,
        IFNULL((select poi.rate from `tabPurchase Invoice Item` poi left join `tabPurchase Invoice` po on poi.parent = po.name where (po.docstatus=1) and poi.item_code = i.name order by po.creation desc limit 1), '0') as cny_rate,
        IFNULL((select poi.base_rate from `tabPurchase Invoice Item` poi left join `tabPurchase Invoice` po on poi.parent = po.name where (po.docstatus=1) and poi.item_code = i.name order by po.creation desc limit 1), '0') as last_purchase_rate,
        IFNULL((select pi.supplier from `tabPurchase Invoice Item` pii left join `tabPurchase Invoice` pi on pii.parent = pi.name where pi.docstatus = 1 and pii.item_code = i.name order by pi.creation desc limit 1), '-') as pi_supplier,
        IFNULL((select pii.qty from `tabPurchase Invoice Item` pii left join `tabPurchase Invoice` pi on pii.parent = pi.name where pi.docstatus = 1 and pii.item_code = i.name order by pi.creation desc limit 1), '0') as pi_qty
        from
        `tabItem` i
        left join `tabItem Default` id on id.parent = i.name
        where
        i.disabled = 0
        %(cond)s
        limit 12 offset %(offset)s
        """ % {"bangalore_warehouse":bangalore_warehouse, "cond":cond, "offset":offset},as_dict = True)

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
    data = frappe.db.sql("select (sum(mri.qty) - sum(mri.received_qty)) as qty from `tabMaterial Request Item` mri inner join `tabMaterial Request` mr on mr.name = mri.parent where mri.item_code = %s and mr.docstatus!=2 and mr.status != 'Stopped' group by mri.item_code", (product_id), as_dict = True)

    if data:
        return data[0].qty
    else:
        data_po = frappe.db.sql("select (sum(poi.qty) - sum(received_qty)) as qty from `tabPurchase Order Item` poi left join `tabPurchase Order` po on po.name = poi.parent where (po.status = 'To Receive and Bill' or po.status = 'To Receive' or po.status = 'Draft') and po.docstatus!=2 and poi.item_code = %s group by poi.item_code", (product_id), as_dict = True)
        if data_po:
            return data_po[0].qty
        else:
            return 0