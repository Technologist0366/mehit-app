import json
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import PolicyTemplate, Policy
from .serializers import PolicyGenerateSerializer, PolicySerializer
from .services import PolicyGenerator
import sys
import traceback

# ────────────────────────────── HTML PAGE VIEWS ──────────────────────────────
@login_required
def questionnaire(request):
    """Render the 6‑step HTML form."""
    return render(request, 'policies/questionnaire.html')

@login_required
def policy_detail(request, slug):
    """Display the generated policy HTML."""
    policy = get_object_or_404(Policy, slug=slug, user=request.user)
    return HttpResponse(policy.generated_content)

# ────────────────────────────── API ENDPOINTS ──────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_policy(request):
    print(">>> generate_policy view called")
    """
    Receive form data, generate policy, store it, and return the policy info.
    """
    try:
        serializer = PolicyGenerateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # ---- Handle effective_date ----
        # Get the date object (for the model) and also store a formatted string in data
        effective_date_obj = None
        if data.get('effective_date'):
            # The serializer gives us a date object (since it's a DateField)
            effective_date_obj = data['effective_date']
            # Store a string version for the responses JSON
            data['effective_date_str'] = effective_date_obj.strftime('%B %d, %Y')
        else:
            # If not provided, use today's date
            effective_date_obj = timezone.now().date()
            data['effective_date_str'] = effective_date_obj.strftime('%B %d, %Y')

        # Remove the original date object from data so it doesn't cause JSON errors
        if 'effective_date' in data:
            del data['effective_date']

        # Add computed fields
        data['current_year'] = datetime.now().year

        # Get the active template
        template = PolicyTemplate.objects.filter(is_active=True).first()
        if not template:
            return Response({'error': 'No active policy template'}, status=500)

        # Generate the final HTML
        html_content = PolicyGenerator.generate_content(
            template.content_structure['html'],
            data
        )

        # Create the Policy record (using effective_date_obj for the DateField)
        policy = Policy.objects.create(
            user=request.user,
            template=template,
            title=f"Privacy Policy – {data.get('legal_name', 'Untitled')}",
            responses=data,                     # data now contains the string version
            generated_content=html_content,
            effective_date=effective_date_obj,  # this is a date object
            status='published'
        )

        # Generate PDF and QR
        PolicyGenerator.generate_pdf(policy)
        PolicyGenerator.generate_qr(policy)
        policy.save()

        out_serializer = PolicySerializer(policy)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        import sys
        import traceback
        print(">>> EXCEPTION CAUGHT:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        with open('/tmp/policy_error.log', 'a') as f:
            f.write(f"--- {timezone.now()} ---\n")
            f.write(traceback.format_exc())
            f.write("\n\n")
        return Response({'error': 'Internal server error', 'detail': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_policies(request):
    policies = Policy.objects.filter(user=request.user).order_by('-created_at')
    serializer = PolicySerializer(policies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def public_policy(request, slug):
    """Public view for a published policy."""
    policy = get_object_or_404(Policy, slug=slug, status='published')
    return HttpResponse(policy.generated_content)
