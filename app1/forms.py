from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth.models import User, Group
from .models import Ticket, UserProfile
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True, label='Select Role')
    username = forms.CharField(
        max_length=150,  # Adjust if necessary
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
        help_text='You can use spaces and special characters in your username.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError("This field is required.")
        # Additional custom validation can be added here if needed
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            role = self.cleaned_data['role']
            UserProfile.objects.create(user=user, role=role)
        return user
from django import forms

class ChatForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'readonly': 'readonly'}))
    user_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    dprt = forms.ChoiceField(choices=[])
    post = forms.ChoiceField(choices=[])
    env = forms.ChoiceField(choices=[])
    pc_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    report_type = forms.ChoiceField(choices=[])
    hw_type = forms.ChoiceField(choices=[], required=False)
    apps_sw = forms.ChoiceField(choices=[], required=False)
    pc_ip = forms.GenericIPAddressField()
    hw_model = forms.CharField(max_length=100)
    report_desc = forms.CharField(widget=forms.Textarea, required=True)
    
    # Fields visible to admin and tech support
    hw_sn = forms.CharField(max_length=100, required=False)
    hw_type_encode = forms.CharField(max_length=100, required=False)
    spa_no = forms.CharField(max_length=100, required=False)
    act_taken = forms.CharField(widget=forms.Textarea, required=False)
    act_stat = forms.CharField(max_length=100, required=False)
    taken_by = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        hw_type_choices = kwargs.pop('hw_type_choices', [])
        report_type_choices = kwargs.pop('report_type_choices', [])
        apps_sw_choices = kwargs.pop('apps_sw_choices', [])
        dprt_choices = kwargs.pop('dprt_choices', [])
        post_choices = kwargs.pop('post_choices', [])
        env_choices = kwargs.pop('env_choices', [])
        email = kwargs.pop('email', None)
        user_name = kwargs.pop('user_name', None)
        pc_name = kwargs.pop('pc_name', None)
        role = kwargs.pop('role', None)
        super().__init__(*args, **kwargs)
        
        # Populate choice fields
        self.fields['hw_type'].choices = hw_type_choices
        self.fields['report_type'].choices = report_type_choices
        self.fields['apps_sw'].choices = apps_sw_choices
        self.fields['dprt'].choices = dprt_choices
        self.fields['post'].choices = post_choices
        self.fields['env'].choices = env_choices
        
        # Set initial values for readonly fields
        if email:
            self.fields['email'].initial = email
        if user_name:
            self.fields['user_name'].initial = user_name
        if pc_name:
            self.fields['pc_name'].initial = pc_name
        
        # Role-based field handling
        if role == 'user':
            self.set_readonly_fields(['hw_sn', 'hw_type_encode', 'spa_no', 'act_taken', 'act_stat', 'taken_by'])
        elif role == 'tech_support':
            self.fields['act_taken'].widget.attrs['readonly'] = False
            self.fields['act_taken'].required = True
            self.fields['act_stat'].widget.attrs['readonly'] = False
            self.fields['act_stat'].required = True
            self.fields['taken_by'].initial = user_name
        elif role == 'admin':
            self.set_readonly_fields(self.fields.keys())
        else:
            self.set_readonly_fields(['email', 'user_name', 'pc_name'])

    def set_readonly_fields(self, fields):
        for field in fields:
            if field in self.fields:
                self.fields[field].widget.attrs['readonly'] = 'readonly'
                self.fields[field].required = False



class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254, widget=forms.EmailInput(attrs={'autofocus': True}))

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password.")
        return self.cleaned_data
