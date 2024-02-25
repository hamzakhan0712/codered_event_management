from django.urls import path
from .views import (
    DashboardView,
    CommiteDashboardView,
    CustomLoginView,
    SignUpView,
    CustomLogoutView,
    MyCommitteeListView,
    CommitteeDetailView,
    CommitteeUpdateView,
    CommitteeDeleteView,
    create_committee,
    create_event,
    event_details_view,
    approve_event,
    search_users,
    update_document,
    event_list,
)



urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('committee_dashboard/', CommiteDashboardView.as_view(), name='committee_dashboard'),
    path('my_committee/', MyCommitteeListView.as_view(), name='my_committee'),
    path('committee_dashboard/create_committee/', create_committee, name='create_committee'),
    path('search-users/', search_users, name='search_users'),

    path('committee_dashboard/committees/<int:pk>/', CommitteeDetailView.as_view(), name='committee_detail'),
    path('committee_dashboard/committees/<int:pk>/update/', CommitteeUpdateView.as_view(), name='committee_update'),
    path('committee_dashboard/committees/<int:pk>/delete/', CommitteeDeleteView.as_view(), name='committee_delete'),

    path('create_event/', create_event, name='create_event'),
    path('events/<int:event_id>/', event_details_view, name='event_details'),
    path('approve_event/<int:event_id>/', approve_event, name='approve_event'),
    path('update_document/<int:event_id>/', update_document, name='update_document'),

    path('events/', event_list, name='event_list'),

]
