import datetime
from django.db import models
from django.db.models import permalink
from django.core.mail import send_mass_mail
from django.template import loader, Context
from django.conf import settings
from django.contrib.sites.models import Site


ATTENDING_CHOICES = (
    ('yes', 'Yes'),
    ('no', 'No'),
    ('no_rsvp', 'Hasn\'t RSVPed yet')
)

DAY_CHOICES = (
    ('day', 'Ceremony & Evening'),
    ('evening', 'Evening (Dinner and Dancing)'),
    ('neither', 'Neither')
)

PRINTED_CHOICES = (
    
    ('no', 'No'),
    ('yes', 'Yes')
    )


class Event(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    date_of_event = models.DateTimeField()
    verification_code = models.CharField(max_length=32, blank=True, default='', help_text='Present for future extension/guest verification.')
    email_subject = models.CharField(max_length=255, help_text='The subject line for the e-mail sent out to guests.')
    email_message = models.TextField(help_text='The body of the e-mail sent out to guests.')
    hosted_by = models.CharField(max_length=255, help_text='The name of the person/organization hosting the event.', blank=True, default='')
    street_address = models.CharField(max_length=255, help_text='The street address where the event is being held.', blank=True, default='')
    city = models.CharField(max_length=64, help_text='The city where the event is being held.', blank=True, default='')
    state = models.CharField(max_length=64, help_text='The state where the event is being held.', blank=True, default='')
    zip_code = models.CharField(max_length=10, help_text='The zip code where the event is being held.', blank=True, default='')
    telephone = models.CharField(max_length=20, blank=True, default='')
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(blank=True, null=True)
    
    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        super(Event, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return ('rsvp_event_view', [self.slug])
    get_absolute_url = permalink(get_absolute_url)
    
    def guests_attending(self):
        return self.guests.filter(attending_status='yes')
    
    def guests_not_attending(self):
        return self.guests.filter(attending_status='no')
    
    def guests_may_attend(self):
        return self.guests.filter(attending_status='maybe')
    
    def guests_no_rsvp(self):
        return self.guests.filter(attending_status='no_rsvp')
    
    def send_guest_emails(self):
        """
        Sends an invite e-mail to all guest who have not RSVPed.
        
        Requires settings RSVP_FROM_EMAIL in your settings file. Returns a 
        count of the number of guests e-mailed.
        """
        mass_mail_data = []
        from_email = getattr(settings, 'RSVP_FROM_EMAIL', '')
        
        for guest in self.guests_no_rsvp():
            t = loader.get_template('rsvp/event_email.txt')
            c = Context({
                'event': self,
                'site': Site.objects.get_current(),
            })
            message = t.render(c)
            mass_mail_data.append([self.email_subject, message, from_email, [guest.email]])
        
        send_mass_mail(mass_mail_data, fail_silently=True)
        return self.guests_no_rsvp().count()


class Guest(models.Model):
    event = models.ForeignKey(Event, related_name='guests')
    email = models.EmailField()
    name = models.CharField(max_length=128, blank=True, default='')
   
    day_or_evening = models.CharField(max_length=32, choices=DAY_CHOICES, default='day')
    attending_status = models.CharField(max_length=32, choices=ATTENDING_CHOICES, default='no_rsvp')
    number_of_guests = models.SmallIntegerField(default=0)
    number_of_children = models.SmallIntegerField(default=0)
    number_of_adult_meals = models.SmallIntegerField(default=0)
    number_of_adult_vegetarian_meals = models.SmallIntegerField(default=0)
    number_of_childrens_meals = models.SmallIntegerField(default=0)
    number_of_high_chairs = models.SmallIntegerField(default=0)
    request_printed_details = models.CharField(max_length=32, choices=PRINTED_CHOICES, default='no')
    comment = models.CharField(max_length=255, blank=True, default='')
    created = models.DateTimeField(default=datetime.datetime.now)
    updated = models.DateTimeField(blank=True, null=True)
    
    def __unicode__(self):
        return u"%s - %s - %s" % (self.event.title, self.email, self.attending_status)
    
    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        super(Guest, self).save(*args, **kwargs)
