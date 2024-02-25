from audioop import reverse
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView, CreateView, View
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Committee,Event
from django.db.models import Q
from django.shortcuts import redirect,render, get_object_or_404
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Committee, User
from django.utils import timezone
from django.views.generic import ListView
from .models import Committee, Event
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Committee
from django.contrib.auth.models import User
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Video, Photo, Committee
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['committees'] = Committee.objects.all() 
        context['events'] = Event.objects.all()  
        context['videos'] = Video.objects.all()  
        context['photos'] = Photo.objects.all()  
        return context

class CommiteDashboardView(TemplateView):
    template_name = 'committee_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['committees'] = Committee.objects.all() 
        return context
 
class CustomLoginView(LoginView):
    template_name = 'login.html'

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('dashboard')

class CommitteeDetailView(DetailView):
    model = Committee
    template_name = 'committee_detail.html'
    context_object_name = 'committee'

class CommitteeUpdateView(UpdateView):
    model = Committee
    template_name = 'committee_update.html' 
    fields = ['name', 'description', 'members', 'college_name']  
    success_url = reverse_lazy('committee_dashboard')  

class CommitteeDeleteView(DeleteView):
    model = Committee
    template_name = 'committee_confirm_delete.html'
    success_url = reverse_lazy('committee_dashboard')




def create_committee(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        college_name = request.POST.get('college_name')
        members_ids = request.POST.getlist('members[]')  
        profile_image = request.FILES.get('profile_image')  

        committee = Committee.objects.create(
            name=name,
            description=description,
            college_name=college_name,
            created_by=request.user,
            profile_image=profile_image, 
            created_at=timezone.now()  
        )

        # Add selected members to the committee
        members = User.objects.filter(pk__in=members_ids)
        committee.members.set(members)

        return redirect('committee_dashboard')  

    return render(request, 'committee_form.html')



def search_users(request):
    if request.method == 'GET':
        query = request.GET.get('q', '')
        users = User.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))  
        results = [{'id': user.id, 'text': f"{user.first_name} {user.last_name}"} for user in users]
        return JsonResponse(results, safe=False)
    else:
        return JsonResponse([], safe=False)





class MyCommitteeListView(LoginRequiredMixin, ListView):
    template_name = 'my_committee.html'
    context_object_name = 'committees'

    def get_queryset(self):
        return Committee.objects.filter(members=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_committees = self.get_queryset()
        committe_all_events = Event.objects.filter(
            committee__in=user_committees,
            initiator=self.request.user
        )

        waiting_for_approval_events = Event.objects.filter(
            approval_status='pending',
            committee__in=user_committees,
            selected_members=self.request.user,
        ).exclude(
            launch_approved_members__username=self.request.user.username
        )
        context['pending_events'] = committe_all_events
        context['approval_events'] = waiting_for_approval_events
        return context






@login_required
def create_event(request):
    if request.method == 'POST':

        event_name = request.POST.get('name')
        event_description = request.POST.get('description')
        launch_date = request.POST.get('launch_date')
        venue = request.POST.get('venue')
        document = request.FILES.get('document')
        video_file = request.FILES.get('video_file')
        photo_file = request.FILES.get('photo_file')
        selected_members = request.POST.getlist('members[]')  
        committee_id = request.POST.get('committee_id') 
        
        committee = get_object_or_404(Committee, pk=committee_id)
        if Event.objects.filter(venue=venue).exists() or Event.objects.filter(launch_date=launch_date).exists():
            return HttpResponseBadRequest('An event already exists at this venue or on the same date.')

        event = Event.objects.create(
            name=event_name,
            description=event_description,
            launch_date=launch_date,
            venue=venue,
            committee=committee, 
            initiator=request.user, 
            approval_status='pending',  
        )

      
        for member_id in selected_members:
            event.selected_members.add(member_id)

        if document:
            event.document = document
            event.save()


        if video_file:
            video = Video.objects.create(
                event=event,
                title='Video Title',  
                video_file=video_file
            )

       
        if photo_file:
            photo = Photo.objects.create(
                event=event,
                title='Photo Title',  
                photo_file=photo_file
            )

        return redirect('committee_dashboard')  
    else:
        return HttpResponseBadRequest('Invalid request method')
    

def event_details_view(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    user_in_launch_approved_members = event.launch_approved_members.filter(id=request.user.id).exists()

    return render(request, 'event_detail.html', {'event': event, 'user_in_launch_approved_members': user_in_launch_approved_members})



def approve_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.user in event.committee.members.all() and event.approval_status == 'pending':
        event.update_launch_approved_members(request.user)

        if event.selected_members.count() == event.launch_approved_members.count():
            event.approval_status = 'ongoing'
            event.save()
    
    return redirect('my_committee')


@login_required
def update_document(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST' and 'document' in request.FILES:
        new_document = request.FILES['document']
        event.document = new_document
        event.save()

        return redirect('event_details', event_id=event.id)

    return render(request, 'event_detail.html', {'event': event})


def event_list(request):

    events = Event.objects.filter(
        approval_status='ongoing', 
        selected_members__in=F('launch_approved_members'),  
    ).distinct()

    return render(request, 'event_list.html', {'events': events})
