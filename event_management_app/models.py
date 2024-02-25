from django.contrib.auth.models import User
from django.db import models

class Committee(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name='committees', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_committees', null=True)
    college_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True) 
    profile_image = models.ImageField(upload_to='committee_profile_images/')  

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
    initiator = models.ForeignKey(User, on_delete=models.CASCADE)
    launch_date = models.DateField()
    venue = models.CharField(max_length=255,null=True)  
    selected_members = models.ManyToManyField(User, related_name='selected_members')
    launch_approved_members = models.ManyToManyField(User, related_name='launch_approved_members',null=True)
    status_choices = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('launched', 'Launched'),
    ]
    approval_status = models.CharField(max_length=10, choices=status_choices, default='pending')
    document = models.FileField(upload_to='event_documents/', null=True)

    def update_launch_approved_members(self, user):
        self.launch_approved_members.add(user)


class Video(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='event_videos/')

class Photo(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='photos')
    title = models.CharField(max_length=100)
    photo_file = models.ImageField(upload_to='event_photos/')


