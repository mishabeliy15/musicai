from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from store.models import Customer, Composer


class CreateCustomerForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(CreateCustomerForm, self).save()

        return Customer.objects.create(
            user=user,
            name=self.cleaned_data["username"],
            email=self.cleaned_data["email"]
        )


class CreateComposerForm(UserCreationForm):
    first_name = forms.CharField(label="First name")
    last_name = forms.CharField(label="Last name")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super(CreateComposerForm, self).save()

        return Composer.objects.create(
            user=user,
            rating=0.0,
            name=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"]
        )