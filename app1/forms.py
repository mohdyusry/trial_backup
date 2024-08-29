from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth.models import User, Group # If using Django's Group model
from .models import Ticket
from django.contrib.auth import authenticate
# from .models import Role  # If using custom Role model

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    roles = forms.MultipleChoiceField(
        choices=[('admin', 'Pentadbir/Admin'), ('tech_support', 'Teknikal/Tech Support'), ('user', 'Pengguna/User')],
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'roles')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # Explicitly save the email field
        if commit:
            user.save()
            # Save roles to the user
            for role_name in self.cleaned_data['roles']:
                group = Group.objects.get(name=role_name)  # If using Group model
                # role = Role.objects.get(name=role_name)  # If using custom Role model
                group.user_set.add(user)
        return user

from django import forms
from .models import Ticket

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
        role = kwargs.pop('role', None)  # User role
        super().__init__(*args, **kwargs)
        
        self.fields['hw_type'].choices = hw_type_choices
        self.fields['report_type'].choices = report_type_choices
        self.fields['apps_sw'].choices = apps_sw_choices
        self.fields['dprt'].choices = dprt_choices
        self.fields['post'].choices = post_choices
        self.fields['env'].choices = env_choices
        if email:
            self.fields['email'].initial = email
        if user_name:
            self.fields['user_name'].initial = user_name
        if pc_name:
            self.fields['pc_name'].initial = pc_name
        
        # Role-based visibility
        if role == 'user':
            for field in ['hw_sn', 'hw_type_encode', 'spa_no', 'act_taken', 'act_stat', 'taken_by']:
                self.fields[field].widget.attrs['readonly'] = 'readonly'
                self.fields[field].required = False
        elif role == 'tech_support':
            for field in ['act_taken', 'act_stat']:
                self.fields[field].widget.attrs['readonly'] = False
                self.fields[field].required = True
            self.fields['taken_by'].initial = user_name
        elif role == 'admin':
            for field in self.fields:
                self.fields[field].widget.attrs['readonly'] = 'readonly'



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



