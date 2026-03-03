from rest_framework import serializers
from .models import Policy, PolicyTemplate

class PolicyGenerateSerializer(serializers.Serializer):
    # Step 1 – Entity
    legal_name = serializers.CharField(required=True)
    business_reg = serializers.CharField(required=False, allow_blank=True)
    physical_address = serializers.CharField(required=True)
    postal_address = serializers.CharField(required=False, allow_blank=True)
    entity_type = serializers.CharField(required=False, allow_blank=True)

    # Step 2 – Data subjects & sources
    website_url = serializers.CharField(required=False, allow_blank=True)
    app_name = serializers.CharField(required=False, allow_blank=True)
    app_store_links = serializers.CharField(required=False, allow_blank=True)

    data_subjects = serializers.ListField(child=serializers.CharField(), required=False)
    data_sources = serializers.ListField(child=serializers.CharField(), required=False)
    data_categories = serializers.ListField(child=serializers.CharField(), required=False)
    app_permissions = serializers.ListField(child=serializers.CharField(), required=False)

    # "Other" text fields
    data_sources_other = serializers.CharField(required=False, allow_blank=True)
    data_categories_other = serializers.CharField(required=False, allow_blank=True)
    app_permissions_other = serializers.CharField(required=False, allow_blank=True)
    other_subjects = serializers.CharField(required=False, allow_blank=True)

    # Step 3 – Legal basis & purpose
    legal_basis = serializers.ListField(child=serializers.CharField(), required=False)
    legitimate_interest_desc = serializers.CharField(required=False, allow_blank=True)
    purposes = serializers.ListField(child=serializers.CharField(), required=False)

    # Step 4 – Sector specific
    health_type = serializers.CharField(required=False, allow_blank=True)
    emr = serializers.CharField(required=False, allow_blank=True)
    health_research_approval = serializers.CharField(required=False, allow_blank=True)

    edu_type = serializers.CharField(required=False, allow_blank=True)
    minors_edu = serializers.CharField(required=False, allow_blank=True)
    parental_consent_methods = serializers.ListField(child=serializers.CharField(), required=False)

    telecom_data_types = serializers.ListField(child=serializers.CharField(), required=False)
    share_vas = serializers.CharField(required=False, allow_blank=True)

    finance_service_types = serializers.ListField(child=serializers.CharField(), required=False)
    crb_reporting = serializers.CharField(required=False, allow_blank=True)
    credit_check = serializers.CharField(required=False, allow_blank=True)

    # Step 5 – Sharing, cookies & rights
    share_third = serializers.CharField(required=False, allow_blank=True)
    third_parties = serializers.ListField(child=serializers.CharField(), required=False)
    dpa_status = serializers.CharField(required=False, allow_blank=True)

    cross_border = serializers.CharField(required=False, allow_blank=True)
    destination_countries = serializers.CharField(required=False, allow_blank=True)
    safeguard = serializers.CharField(required=False, allow_blank=True)

    cookies = serializers.ListField(child=serializers.CharField(), required=False)
    cookie_banner = serializers.CharField(required=False, allow_blank=True)

    rights_methods = serializers.ListField(child=serializers.CharField(), required=False)
    rights_portal_url = serializers.CharField(required=False, allow_blank=True)
    rights_email = serializers.CharField(required=False, allow_blank=True)
    rights_phone = serializers.CharField(required=False, allow_blank=True)
    rights_physical = serializers.CharField(required=False, allow_blank=True)
    rights_postal = serializers.CharField(required=False, allow_blank=True)
    rights_authorised = serializers.CharField(required=False, allow_blank=True)
    response_time = serializers.CharField(required=False, allow_blank=True)

    # Step 6 – Security & retention
    tech_measures = serializers.ListField(child=serializers.CharField(), required=False)
    org_measures = serializers.ListField(child=serializers.CharField(), required=False)
    breach_plan = serializers.CharField(required=False, allow_blank=True)
    breach_process = serializers.CharField(required=False, allow_blank=True)

    retention_policy = serializers.CharField(required=False, allow_blank=True)
    retention_customer = serializers.CharField(required=False, allow_blank=True)
    retention_employee = serializers.CharField(required=False, allow_blank=True)
    retention_web = serializers.CharField(required=False, allow_blank=True)

    children_policy = serializers.CharField(required=False, allow_blank=True)

    # Contact details (can be prefilled from user profile)
    contact_email = serializers.EmailField(required=False)
    contact_phone = serializers.CharField(required=False)
    dpo_email = serializers.EmailField(required=False)

    # Policy metadata
    effective_date = serializers.DateField(required=False)

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ['id', 'slug', 'title', 'status', 'effective_date',
                  'pdf_file', 'qr_code', 'created_at', 'published_at']
        read_only_fields = ['id', 'slug', 'pdf_file', 'qr_code',
                            'created_at', 'published_at']
