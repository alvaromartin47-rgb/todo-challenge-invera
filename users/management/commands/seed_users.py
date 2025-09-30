from django.core.management.base import BaseCommand
from users.factories import UserFactory

class Command(BaseCommand):
    help = 'Seed users data'
    
    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=10, help='Number of users to create')
        parser.add_argument('--clean', action='store_true', help='Delete existing users first')
        
    def handle(self, *args, **options):
        if options['clean']:
            from users.models import User
            # Solo borrar los datos generados por el seed
            deleted = User.objects.filter(is_seed_data=True).delete()
            self.stdout.write(f'Deleted {deleted[0]} seed users (preserving real data)')
            return
        
        users = UserFactory.create_batch_data(options['number'])
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(users)} users')
        )