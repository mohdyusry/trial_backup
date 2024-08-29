
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
    logger.info(f"User {user.username} has role: {user.userprofile.role}")

    if user.is_superuser or user.userprofile.role in ['admin', 'tech_support']:
        # Admin or Tech Support sees all tickets
        tickets = Ticket.objects.all()
    else:
        # Normal user sees only their tickets
        tickets = Ticket.objects.filter(user_name=user.username)

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
import logging
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import ChatForm
from .models import Ticket
from .chatbot import recommend_action

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
        logger.info(f"UserProfile created for {user.username} with role 'user'.")

    if request.method == 'POST':
        form = ChatForm(request.POST, role=profile.role)
        if form.is_valid():
            # Extract form data
            hw_type = form.cleaned_data['hw_type']
            apps_sw = form.cleaned_data['apps_sw']
            report_type = form.cleaned_data['report_type']
            report_desc = form.cleaned_data['report_desc']
            logger.info(f"Form data received: {hw_type}, {apps_sw}, {report_type}, {report_desc}")

            # Call the chatbot model
            recommended_action = recommend_action(hw_type, apps_sw, report_type, report_desc)
            logger.info(f"Recommended Action: {recommended_action}")
            
            # Save the ticket
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
        logger.info(f"Form initialized for user {user.username}")

    context = {
        'form': form,
        'is_admin_or_tech': is_admin_or_tech,
        'chat_history': [],
    }
    return render(request, 'chatbot.html', context)



from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib import messages

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            
            # Check if the user already exists
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                messages.error(request, "Pengguna telah didaftarkan sila login")
                return render(request, 'signup.html', {'form': form, 'user_exists': True})
            
            user = form.save()

            # Log the user in
            backend = 'django.contrib.auth.backends.ModelBackend'  # Use the default backend
            login(request, user, backend=backend)

            return redirect('login')  # Redirect to the login after signup
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

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Ticket

def respond_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        act_taken = request.POST.get('act_taken')
        act_stat = request.POST.get('act_stat')
        taken_by = request.user.username

        # Ensure act_taken is not empty
        if not act_taken:
            return render(request, 'respond_ticket.html', {
                'ticket': ticket,
                'error_message': 'Action taken is required.'
            })

        # Update the ticket fields
        ticket.act_taken = act_taken
        ticket.act_stat = act_stat
        ticket.taken_by = taken_by
        ticket.date_action = timezone.now().date()
        ticket.time_action = timezone.now().time()

        try:
            ticket.save()
            return redirect('dashboard')
        except Exception as e:
            return render(request, 'respond_ticket.html', {
                'ticket': ticket,
                'error_message': str(e)
            })

    return render(request, 'respond_ticket.html', {'ticket': ticket})


