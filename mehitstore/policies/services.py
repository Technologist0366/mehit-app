import re
from datetime import datetime
from io import BytesIO
from django.core.files.base import ContentFile
import qrcode
from weasyprint import HTML

class PolicyGenerator:
    @staticmethod
    def generate_content(template_html, responses):
        """
        Replace placeholders {{ variable }} in the template with actual values.
        Also generates HTML lists for multi‑value fields.
        """
        html = template_html

        # Simple replacements (single fields)
        simple_fields = [
            'legal_name', 'business_reg', 'physical_address', 'postal_address',
            'website_url', 'app_name', 'effective_date',
            'legitimate_interest_desc', 'dpa_status',
            'destination_countries', 'safeguard', 'cookie_banner',
            'response_time', 'breach_process',
            'retention_policy', 'retention_customer', 'retention_employee', 'retention_web',
            'children_policy', 'contact_email', 'contact_phone', 'dpo_email',
            'current_year'
        ]
        for field in simple_fields:
            value = responses.get(field, '')
            html = html.replace(f'{{{{ {field} }}}}', str(value))

        # List replacements (generate <ul>)
        list_fields = {
            'provided_info_list': 'data_categories',
            'third_party_sources_list': 'data_sources',
            'sensitive_data_list': 'sensitive_data',   # you'll need to identify which categories are sensitive
            'purposes_list': 'purposes',
            'legal_basis_list': 'legal_basis',
            'third_parties_list': 'third_parties',
            'cookies_uses_list': 'cookies',
            'cookies_types_list': 'cookies',
            'rights_methods_list': 'rights_methods',
            'tech_measures_list': 'tech_measures',
            'org_measures_list': 'org_measures',
        }
        for placeholder, source_field in list_fields.items():
            items = responses.get(source_field, [])
            if items:
                list_html = '<ul>' + ''.join(f'<li>{item}</li>' for item in items) + '</ul>'
            else:
                list_html = ''
            html = html.replace(f'{{{{ {placeholder} }}}}', list_html)

        # Conditional sections (sector‑specific) – you can build these separately in the view
        # and then replace placeholders like {{ health_sector_section }}
        # For simplicity, we'll assume the view handles that.

        return html

    @staticmethod
    def generate_pdf(policy):
        """Generate a PDF from policy.generated_content and save it."""
        html_string = policy.generated_content
        pdf_file = HTML(string=html_string).write_pdf()
        policy.pdf_file.save(f"{policy.slug}.pdf", ContentFile(pdf_file))

    @staticmethod
    def generate_qr(policy):
        """Generate a QR code linking to the public policy view."""
        # Update with your actual domain
        url = f"https://mehit.app/policy/{policy.slug}/"
        qr = qrcode.make(url)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        policy.qr_code.save(f"{policy.slug}.png", ContentFile(buffer.getvalue()))
