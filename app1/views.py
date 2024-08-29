
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import EmailAuthenticationForm
from .forms import ChatForm, SignUpForm
from .models import Ticket
from .chatbot import respond
from django.utils import timezone
import logging
from .forms import ChatForm

# Set up logging
logger = logging.getLogger(__name__)

def landing_page(request):
    return render(request, 'landing_page.html')

@login_required
# def dashboard(request):
#     # Filter tickets based on the logged-in user's username
    # tickets = Ticket.objects.filter(user_name=request.user.username)
#     return render(request, 'dashboard.html', {'tickets': tickets})

def dashboard(request):
    user = request.user
    # Check user role

    
    if request.user.is_superuser or request.user.userprofile.role in ['admin', 'tech_support']:
        # Admin or Tech Support sees all tickets
        tickets = Ticket.objects.all()
    else:
        # Normal user sees only their tickets
        tickets = Ticket.objects.filter(user_name=request.user.username)

    context = {
        'tickets': tickets,
    }

    return render(request, 'dashboard.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ChatForm
from .models import Ticket, UserProfile
from .chatbot import recommend_action
from django.utils import timezone
import logging

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def chatbot_view(request):
    user = request.user
    profile = None
    is_admin_or_tech = False

    try:
        profile = user.userprofile
        is_admin_or_tech = profile.role in ['admin', 'tech_support']
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, role='user')
        is_admin_or_tech = False

    if request.method == 'POST':
        form = ChatForm(request.POST, role=profile.role)
        if form.is_valid():
            hw_type = form.cleaned_data['hw_type']
            apps_sw = form.cleaned_data['apps_sw']
            report_desc = form.cleaned_data['report_desc']
            
            # Call the chatbot model
            recommended_action = recommend_action(hw_type, apps_sw, report_desc)
            logger.info(f"Recommended Action: {recommended_action}")
            
            ticket = Ticket(
                email=form.cleaned_data['email'],
                user_name=form.cleaned_data['user_name'],
                dprt=form.cleaned_data['dprt'],
                post=form.cleaned_data['post'],
                env=form.cleaned_data['env'],
                pc_name=form.cleaned_data['pc_name'],
                report_type=form.cleaned_data['report_type'],
                hw_type=form.cleaned_data['hw_type'],
                apps_sw=form.cleaned_data['apps_sw'],
                pc_ip=form.cleaned_data['pc_ip'],
                hw_model=form.cleaned_data['hw_model'],
                report_desc=form.cleaned_data['report_desc'],
                hw_sn=form.cleaned_data['hw_sn'],
                hw_type_encode=form.cleaned_data['hw_type_encode'],
                spa_no=form.cleaned_data['spa_no'],
                act_taken=recommended_action,
                act_stat=form.cleaned_data['act_stat'],
                taken_by=form.cleaned_data['taken_by'],
                date_created=timezone.now().date(),
                time_created=timezone.now().time(),
            )
            
            if profile.role == 'tech_support':
                ticket.date_action = timezone.now().date()
                ticket.time_action = timezone.now().time()

            try:
                ticket.save()
                logger.info(f"Ticket {ticket.ticket_no} saved successfully.")
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"Error saving ticket: {e}")
        else:
            # Log form errors
            logger.error(f"Form is invalid: {form.errors}")

    else:
        form = ChatForm(
            hw_type_choices=[(x, x) for x in Ticket.objects.values_list('hw_type', flat=True).distinct()],
            report_type_choices=[(x, x) for x in Ticket.objects.values_list('report_type', flat=True).distinct()],
            apps_sw_choices=[(x, x) for x in Ticket.objects.values_list('apps_sw', flat=True).distinct()],
            dprt_choices=[(x, x) for x in Ticket.objects.values_list('dprt', flat=True).distinct()],
            post_choices=[(x, x) for x in Ticket.objects.values_list('post', flat=True).distinct()],
            env_choices=[(x, x) for x in Ticket.objects.values_list('env', flat=True).distinct()],
            email=user.email,
            user_name=user.username,
            pc_name=f"{profile.dprt}-{profile.post}-{profile.env}" if profile else '',
            role=profile.role if profile else 'user'
        )

    context = {
        'form': form,
        'is_admin_or_tech': is_admin_or_tech,
        'chat_history': [],
    }
    return render(request, 'chatbot.html', context)




from django.contrib.auth import get_backends
from .forms import SignUpForm  # Make sure you import your SignUpForm

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create a new user object, but don't save it to the database yet
            user.email = form.cleaned_data['email']  # Explicitly save the email
            if not form.cleaned_data['password1']:  # Check if password is empty
                user.set_password('1234')  # Set the default password
            else:
                user.set_password(form.cleaned_data.get('password1'))  # Set the password from the form
            user.save()  # Save the user to the database
            form.save_m2m()  # Save the roles

            # Manually specify the backend for login
            backend = get_backends()[0]  # Get the first available backend (usually the default)
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'

            login(request, user)  # Automatically log the user in after signup
            return redirect('login')  # Redirect to the login page
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})



def custom_login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('chatbot_view')  # Redirect to the chatbot page after successful login
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})


from django.shortcuts import render, get_object_or_404
from .models import Ticket

def respond_ticket(request, ticket_id):
    # Fetch the ticket based on the ticket_id
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        # Handle the response action here, e.g., updating the ticket status
        # Example: ticket.act_stat = 'Responded'
        # ticket.save()
        pass  # Replace with your logic

    # Render a template for responding to the ticket
    return render(request, 'respond_ticket.html', {'ticket': ticket})
