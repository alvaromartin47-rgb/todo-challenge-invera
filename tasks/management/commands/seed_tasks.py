from django.core.management.base import BaseCommand
from tasks.factories import TaskFactory

class Command(BaseCommand):
    help = 'Seed tasks data'
    
    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=10, help='Number of tasks to create')
        parser.add_argument('--clean', action='store_true', help='Delete existing tasks first')
    
    def handle(self, *args, **options):
        if options['clean']:
            from tasks.models import Task
            # Solo borrar los datos generados por el seed
            deleted = Task.objects.filter(is_seed_data=True).delete()
            self.stdout.write(f'Deleted {deleted[0]} seed tasks (preserving real data)')
            return
        
        tasks = TaskFactory.create_batch_data(options['number'])
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(tasks)} tasks')
        )