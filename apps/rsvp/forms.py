from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rsvp.models import ATTENDING_CHOICES,PRINTED_CHOICES, Guest, Event, DAY_CHOICES


VISIBLE_ATTENDING_CHOICES = [choice for choice in ATTENDING_CHOICES if choice[0] != 'no_rsvp']
VISIBLE_EVENING_CHOICES = [choice for choice in DAY_CHOICES if choice[0] != 'neither']


class RSVPForm(forms.Form):
   
    name = forms.CharField(max_length=128)
    email = forms.EmailField()
    attending = forms.ChoiceField(choices=VISIBLE_ATTENDING_CHOICES, initial='yes', widget=forms.RadioSelect)
    day_or_evening = forms.ChoiceField(choices=VISIBLE_EVENING_CHOICES, initial='day', widget=forms.RadioSelect)
    

    number_of_guests = forms.IntegerField(initial=0,label='Number of adults')
    number_of_children = forms.IntegerField(initial=0)
   
    number_of_adult_vegetarian_meals = forms.IntegerField(initial=0)
    number_of_adult_meals = forms.IntegerField(initial=0,label="Number of non-vegetarian adult meals")
    number_of_childrens_meals = forms.IntegerField(initial=0)
    number_of_high_chairs = forms.IntegerField(initial=0)

    request_printed_details = forms.ChoiceField(choices=PRINTED_CHOICES, initial='no', widget=forms.RadioSelect)

    comment = forms.CharField(max_length=255, required=False, widget=forms.Textarea,label='Other special requests (please let us know if you have any allergies or have babies that do not need a meal)')
  
    def __init__(self, *args, **kwargs):
        if 'guest_class' in kwargs:
            self.guest_class = kwargs['guest_class']
            del(kwargs['guest_class'])
        else:
            self.guest_class = Guest
        super(RSVPForm, self).__init__(*args, **kwargs)
    
    def clean_email(self):
        try:
            OurWedding = Event.objects.get(id=1)
            guest = self.guest_class._default_manager.get_or_create(event=OurWedding,email=self.cleaned_data['email'])
        except ObjectDoesNotExist:
            raise forms.ValidationError, 'That e-mail is not on the guest list.'
        
        if hasattr(guest, 'attending_status') and guest.attending_status != 'no_rsvp':
            raise forms.ValidationError, 'You have already provided RSVP information.'
        
        return self.cleaned_data['email']
    
    def clean_number_of_guests(self):
        if self.cleaned_data['number_of_guests'] < 0:
            raise forms.ValidationError, "The number of guests you're bringing can not be negative."
        return self.cleaned_data['number_of_guests']
        
    def save(self):
        guest = self.guest_class._default_manager.get(email=self.cleaned_data['email'])
        
        if self.cleaned_data['name']:
            guest.name = self.cleaned_data['name']
        
        guest.attending_status = self.cleaned_data['attending']
        guest.number_of_guests = self.cleaned_data['number_of_guests']
        guest.comment = self.cleaned_data['comment']

        guest.day_or_evening = self.cleaned_data['day_or_evening']
        guest.number_of_children = self.cleaned_data['number_of_children']
        guest.number_of_adult_vegetarian_meals = self.cleaned_data['number_of_adult_vegetarian_meals']
        guest.number_of_adult_meals = self.cleaned_data['number_of_adult_meals']
        guest.number_of_childrens_meals = self.cleaned_data['number_of_childrens_meals']
        guest.number_of_high_chairs = self.cleaned_data['number_of_high_chairs']
        guest.request_printed_details = self.cleaned_data['request_printed_details']

        guest.save()
        return guest
