
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile, Lawyer, Appointment

class ClientRegisterForm(UserCreationForm):

    email = forms.EmailField()

    phone = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone',
            'password1',
            'password2'
        ]

    def save(self, commit=True):

        user = super().save(commit=commit)

        if commit:
            Profile.objects.create(
                user=user,
                role='CLIENT',
                phone=self.cleaned_data['phone']
            )

        return user

class LawyerForm(forms.ModelForm):

    class Meta:
        model = Lawyer

        exclude = ['user']

        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4
            }),

            'consultation_fee': forms.NumberInput(attrs={
                'min': '0',
                'step': '0.01'
            })
        }

class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment

        fields = [
            'lawyer',
            'appointment_date',
            'case_details'
        ]

        widgets = {
            'appointment_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local'
                }
            ),

            'case_details': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'Describe your legal issue...'
                }
            )
        }
class LawyerRegisterForm(UserCreationForm):

    email = forms.EmailField()

    phone = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone',
            'password1',
            'password2'
        ]

    def save(self, commit=True):

        user = super().save(commit=commit)

        if commit:
            Profile.objects.create(
                user=user,
                role='LAWYER',
                phone=self.cleaned_data['phone']
            )

        return user
class LawyerDetailsForm(forms.ModelForm):

    class Meta:
        model = Lawyer

        fields = [
            'specialization',
            'experience',
            'qualification',
            'consultation_fee',
            'bio',
            'profile_image'
        ]

        widgets = {
            'specialization': forms.TextInput(attrs={
                'placeholder': 'Example: Criminal Law'
            }),

            'experience': forms.NumberInput(attrs={
                'min': '0',
                'placeholder': 'Years of experience'
            }),

            'qualification': forms.TextInput(attrs={
                'placeholder': 'Example: LLB, LLM'
            }),

            'consultation_fee': forms.NumberInput(attrs={
                'min': '0',
                'step': '0.01',
                'placeholder': 'Consultation fee'
            }),

            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell clients about your legal experience...'
            })
        }

