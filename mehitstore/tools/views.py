from django.shortcuts import render
from .models import Tool

def tool_list(request):
    tools = Tool.objects.filter(is_active=True).order_by('order', 'name')
    return render(request, 'tools.html', {'tools': tools})
