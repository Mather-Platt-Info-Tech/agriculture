# Copyright (c) 2024, MPlatt InfoTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry

class FarmerSuppliesEntry(Document):
    pass

def create_stock_entry(doc, method):
    frappe.logger().info(f"create_stock_entry called with doc: {doc} and method: {method}")
    item_code = doc.item
    qty = doc.accepted_quantity
    s_warehouse = None  # Set the source warehouse if applicable
    t_warehouse = doc.collection_center
    posting_date = doc.supply_date
    posting_time = frappe.utils.nowtime()
    company = frappe.defaults.get_user_default("Company")
    
    # Create a new stock entry document
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Receipt"
    stock_entry.to_warehouse = t_warehouse
    stock_entry.posting_date = posting_date
    stock_entry.posting_time = posting_time
    stock_entry.company = company
    stock_entry.append("items", {
        "item_code": item_code,
        "qty": qty,
        "t_warehouse": t_warehouse
    })
    # Insert and submit the stock entry
    stock_entry.insert()
    stock_entry.submit()

    frappe.logger().info(f"Stock Entry created successfully: {stock_entry.name}")

    return stock_entry.name

@frappe.whitelist()
def fetch_supplies(farmer):
    farmer_supplies = frappe.get_all(
        'Farmer Supplies Entry',
        filters={'farmer': farmer},
        fields=['name', 'supply_date', 'item', 'accepted_quantity', 'collection_center']
    )
    return farmer_supplies

