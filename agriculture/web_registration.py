import frappe
from frappe.website.doctype.web_form.web_form import accept
from agriculture.agriculture.generate_contract_pdf import generate_farmer_contract

@frappe.whitelist(allow_guest=True)
def get_filled_contract_template(form_data):
    # Convert form_data to a dictionary
    data = {item['name']: item['value'] for item in frappe.parse_json(form_data)}
    
    # Read the HTML template
    template_path = frappe.get_site_path("private", "files", "contract_template.html")
    with open(template_path, "r") as template_file:
        html_template = template_file.read()
    
    # Replace placeholders with form data
    html_content = html_template.replace('{{ first_name }}', data.get('first_name', ''))
    html_content = html_content.replace('{{ last_name }}', data.get('last_name', ''))
    html_content = html_content.replace('{{ date_of_joining }}', data.get('date_of_joining', ''))
    html_content = html_content.replace('{{ address }}', data.get('address', ''))
    html_content = html_content.replace('{{ county }}', data.get('county', ''))
    html_content = html_content.replace('{{ government_id }}', data.get('government_id', ''))
    
    # Handle fruit details (adjust as needed based on your form structure)
    fruits = data.get('fruit', '')
    acres = data.get('fruit_acres', '')
    html_content = html_content.replace('{{ fruit }}', fruits)
    html_content = html_content.replace('{{ fruit_acres }}', acres)
    html_content = html_content.replace('{{ valuation_rate }}', '')  # You may need to calculate this
    
    return html_content

@frappe.whitelist(allow_guest=True)
def farmer_web_form_submit(web_form, data):
    # First, let the standard web form submission happen
    response = accept(web_form, data)
    
    # Now, generate the PDF
    farmer_name = response.get('name')
    if farmer_name:
        farmer_doc = frappe.get_doc('Farmer', farmer_name)
        result = generate_farmer_contract(farmer_doc)
        farmer_doc.db_set('registration_document', result['file_url'], update_modified=False)
    
    return response
