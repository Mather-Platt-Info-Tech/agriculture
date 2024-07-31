import frappe
import os
from frappe import _
from frappe.model.document import Document
from agriculture.agriculture.generate_contract_pdf import generate_farmer_contract

class Farmer(Document):
    def after_insert(self):
        self.generate_contract()

    def generate_contract(self):
        result = generate_farmer_contract(self)
        self.db_set('registration_document', result['file_url'], update_modified=False)

    def on_trash(self):
        self.delete_registration_files()
    
    def delete_registration_files(self):
        if self.registration_document:
            # Delete the file referenced in registration_document
            try:
                file_doc = frappe.get_doc("File", {"file_url": self.registration_document})
                file_doc.delete()
            except Exception as e:
                frappe.log_error(f"Error deleting registration document: {str(e)}")
        
        # Delete any other matching files
        file_name_pattern = f"{self.first_name}_{self.last_name}_registration"
        files = frappe.get_all("File", filters={
            "file_name": ["like", f"%{file_name_pattern}%"],
            "attached_to_doctype": "Farmer",
            "attached_to_name": self.name
        }, fields=["name", "file_url"])
        
        for file in files:
            try:
                frappe.delete_doc("File", file.name)
                # Also delete the physical file
                if file.file_url:
                    file_path = frappe.get_site_path() + file.file_url
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except Exception as e:
                frappe.log_error(f"Error deleting file {file.name}: {str(e)}")

@frappe.whitelist()
def after_insert(doc, method):
    doc.generate_contract()

@frappe.whitelist()
def generate_missing_pdfs():
    farmers = frappe.get_all('Farmer', filters={'registration_document': ['is', 'not set']}, fields=['name'])
    
    total_farmers = len(farmers)
    processed_farmers = 0

    for farmer in farmers:
        farmer_doc = frappe.get_doc('Farmer', farmer.name)
        result = generate_farmer_contract(farmer_doc)
        farmer_doc.db_set('registration_document', result['file_url'], update_modified=False)
        processed_farmers += 1
        
        # Commit every 10 records to avoid long-running transactions
        if processed_farmers % 10 == 0:
            frappe.db.commit()
    
    frappe.db.commit()
    return {'total': total_farmers, 'processed': processed_farmers}

@frappe.whitelist()
def check_missing_pdfs():
    count = frappe.db.count('Farmer', filters={'registration_document': ['is', 'not set']})
    return count > 0
