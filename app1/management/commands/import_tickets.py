import csv
from django.core.management.base import BaseCommand
from app1.models import Ticket
import os

class Command(BaseCommand):
    help = 'Import tickets from a CSV file into the Ticket model'

    def handle(self, *args, **kwargs):
        # Specify the CSV file path
        csv_file_path = os.path.join('C:/Users/user/Trial', 'tickets.csv')
        
        # Open the CSV file
        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            
            # Iterate over the rows in the CSV file
            for row in reader:
                # Create and save the Ticket object
                Ticket.objects.create(
                    ticket_no=row['ticket_no'],
                    user_name=row['user_name'],
                    email=row['email'],
                    dprt=row['dprt'],
                    post=row['post'],
                    env=row['env'],
                    pc_ip=row['pc_ip'],
                    hw_sn=row['hw_sn'],
                    spa_no=row['spa_no'],
                    report_type=row['report_type'],
                    hw_type=row['hw_type'],
                    hw_type_encode=row['hw_type_encode'],
                    hw_model=row['hw_model'],
                    apps_sw=row['apps_sw'],
                    report_desc=row['report_desc'],
                    act_taken=row['act_taken'],
                    act_stat=row['act_stat'],
                    date_created=row['date_created'],
                    time_created=row['time_created'],
                    date_action=row.get('date_action', None),
                    time_action=row.get('time_action', None),
                    taken_by=row['taken_by'],
                    ftr_act=row.get('ftr_act', None),
                    fu_act=row.get('fu_act', None)
                )

        self.stdout.write(self.style.SUCCESS('Data imported successfully!'))
