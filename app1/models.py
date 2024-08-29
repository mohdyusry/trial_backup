from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('tech_support', 'Tech Support'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    dprt = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    env = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Ticket(models.Model):
    ticket_no = models.CharField(max_length=100, unique=True, editable=False)
    user_name = models.CharField(max_length=100)
    email = models.EmailField()
    dprt = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    env = models.CharField(max_length=100)
    pc_name = models.CharField(max_length=100, editable=False)
    pc_ip = models.GenericIPAddressField()
    hw_sn = models.CharField(max_length=100)
    spa_no = models.CharField(max_length=100)
    report_type = models.CharField(max_length=100, default='Default Value')
    hw_type = models.CharField(max_length=100)
    hw_type_encode = models.CharField(max_length=100)
    hw_model = models.CharField(max_length=100)
    apps_sw = models.CharField(max_length=255, blank=True, null=True)
    report_desc = models.TextField()
    act_taken = models.TextField()
    act_stat = models.CharField(max_length=100)
    date_created = models.DateField(editable=False)
    time_created = models.TimeField(editable=False)
    date_action = models.DateField(null=True, blank=True)
    time_action = models.TimeField(null=True, blank=True)
    taken_by = models.CharField(max_length=100)
    ftr_act = models.TextField(null=True, blank=True)
    fu_act = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.pc_name = f"{self.dprt}-{self.post}-{self.env}"
        if not self.id:
            self.date_created = timezone.now().date()
            self.time_created = timezone.now().time()
        if not self.ticket_no:
            prefix = "AHBKPP"
            current_date = timezone.now()
            year = current_date.strftime('%y')
            month = current_date.strftime('%m')
            last_ticket = Ticket.objects.filter(ticket_no__startswith=prefix + year + month).order_by('ticket_no').last()
            if last_ticket:
                last_number = int(last_ticket.ticket_no[-3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.ticket_no = f"{prefix}{year}{month}{new_number:03d}"
        super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return self.ticket_no
