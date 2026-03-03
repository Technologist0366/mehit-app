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
    """
    Receive form data, generate policy, store it, and return the policy info.
    """
    serializer = PolicyGenerateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Get the active template (you can extend this to select based on sector)
    template = PolicyTemplate.objects.filter(is_active=True).first()
    if not template:
        return Response({'error': 'No active policy template'}, status=500)

    # Add computed fields
    data['current_year'] = datetime.now().year
    if not data.get('effective_date'):
        data['effective_date'] = timezone.now().date().strftime('%B %d, %Y')

    # Build any conditional sector sections (optional)
    # For now we'll just leave placeholders like {{ health_sector_section }} empty.
    # In a real implementation you would generate those blocks here.

    # Generate the final HTML
    html_content = PolicyGenerator.generate_content(
        template.content_structure['html'],
        data
    )

    # Create the Policy record
    policy = Policy.objects.create(
        user=request.user,
        template=template,
        title=f"Privacy Policy – {data.get('legal_name', 'Untitled')}",
        responses=data,
        generated_content=html_content,
        effective_date=data.get('effective_date', timezone.now().date()),
        status='published'   # or 'draft'
    )

    # Generate PDF and QR (can be moved to Celery for production)
    PolicyGenerator.generate_pdf(policy)
    PolicyGenerator.generate_qr(policy)
    policy.save()

    out_serializer = PolicySerializer(policy)
    return Response(out_serializer.data, status=status.HTTP_201_CREATED)


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
