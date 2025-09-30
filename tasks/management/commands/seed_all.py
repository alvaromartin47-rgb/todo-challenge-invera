from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Seed all data for the application'
    
    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=10, help='Number of items to create per model')
        parser.add_argument('--clean', action='store_true', help='Delete existing seed data first')
    
    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('Cleaning all seed data...')
            call_command('seed_tasks', '--clean')
            call_command('seed_users', '--clean')
            self.stdout.write(self.style.SUCCESS('All seed data cleaned'))
            return
        
        self.stdout.write('Seeding all data...')
        
        # Seed tasks
        call_command('seed_tasks', '--number', str(options['number']))
        call_command('seed_users', '--number', str(options['number']))
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded all data with {options["number"]} items each')
        )
