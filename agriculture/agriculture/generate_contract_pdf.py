import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file

def generate_farmer_contract(doc):
    # Fetch the farmer document
    farmer = doc
    
    # Read the HTML template
    template_path = frappe.get_site_path("private", "files", "contract_template.html")
    with open(template_path, "r") as template_file:
        html_template = template_file.read()
    
    # Replace placeholders with actual data
    html_content = html_template.replace('{{ first_name }}', farmer.first_name or '')
    html_content = html_content.replace('{{ last_name }}', farmer.last_name or '')
    html_content = html_content.replace('{{ date_of_joining }}', str(farmer.date_of_joining) or '')
    html_content = html_content.replace('{{ address }}', farmer.address or '')
    html_content = html_content.replace('{{ county }}', farmer.county or '')
    html_content = html_content.replace('{{ government_id }}', farmer.government_id or '')
    
    # Replace the fruit details
    fruits = ', '.join([d.fruit for d in farmer.fruit_acreage])
    acres = ', '.join([str(d.fruit_acres) for d in farmer.fruit_acreage])
    valuation_rates = ', '.join([str(frappe.get_doc('Item', d.fruit).valuation_rate) for d in farmer.fruit_acreage])
    html_content = html_content.replace('{{ fruit }}', fruits)
    html_content = html_content.replace('{{ fruit_acres }}', acres)
    html_content = html_content.replace('{{ valuation_rate }}', valuation_rates)
    
    # Generate the PDF
    pdf_content = get_pdf(html_content)
    
    # Save the PDF file
    pdf_name = f"{farmer.first_name}_{farmer.last_name}_registration.pdf"
    
    # Check if the file already exists
    existing_file = frappe.get_all("File", 
                                   filters={
                                       "file_name": pdf_name,
                                       "attached_to_doctype": "Farmer", 
                                       "attached_to_name": farmer.name
                                   }, 
                                   fields=["name", "file_url"])
    
    if existing_file:
        file_doc = frappe.get_doc("File", existing_file[0].name)
        file_doc.file_data = pdf_content
        file_doc.save()
    else:
        # Save the PDF file
        file_doc = save_file(pdf_name, pdf_content, "Farmer", farmer.name, is_private=1)
    
    return {"file_doc": file_doc, "file_url": file_doc.file_url}