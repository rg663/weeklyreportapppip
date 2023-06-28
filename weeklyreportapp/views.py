from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.http import HttpResponse, Http404
from django.db.models import Q

from .models import *

from django.template import loader

def index(request):
    context = {}
    template_name = 'index.html'
    if request.user.is_authenticated:
        project_list = Project.objects.filter(
            (Q(pi=request.user) & Q(status__name__in=['New', 'Active', ])) |
            (Q(status__name__in=['New', 'Active', ]) &
             Q(projectuser__user=request.user) &
             Q(projectuser__status__name__in=['Active', ]))
        ).distinct().order_by('-created')

        allocation_list = Allocation.objects.filter(
            Q(status__name__in=['Active', 'New', 'Renewal Requested', ]) &
            Q(project__status__name__in=['Active', 'New']) &
            Q(project__projectuser__user=request.user) &
            Q(project__projectuser__status__name__in=['Active', ]) &
            Q(allocationuser__user=request.user) &
            Q(allocationuser__status__name__in=['Active', ])
        ).distinct().order_by('-created')

        resource_list = Resource.objects.distinct()
        user_list = User.objects.distinct()
        context['project_list'] = project_list
        context['allocation_list'] = allocation_list
        context['new_allocations'] = [allocation for allocation in allocation_list if allocation.start_date != None and datetime.today().date() - allocation.start_date <= timedelta(days=7)]
        context['allocations_expiring_soon'] = [allocation for allocation in allocation_list if allocation.end_date != None and allocation.expires_in <= 30]
        context['resource_list'] = resource_list
        context['resource_types_initial'] = [res.resource_type for res in resource_list]
        context['resource_types_in_between'] = {}
        for res_type in context['resource_types_initial']:
            context['resource_types_in_between'][res_type] = 0
        for res in context['resource_types_initial']:
            context['resource_types_in_between'][res] += 1
        context['resource_types'] = []
        for res_type, count in context['resource_types_in_between'].items():
            new_list = [res_type.name, count]
            context['resource_types'].append(new_list)
        context['user_list'] = user_list
        context['users_from_this_week'] = [user for user in user_list if user.last_login != None and datetime.today().date() - user.last_login.date() <= timedelta(days=7)]
        context['all_other_users'] = [user for user in user_list if user not in context['users_from_this_week']]
       
    return render(request, template_name, context)