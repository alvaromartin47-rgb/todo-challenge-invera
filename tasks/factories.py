import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from .models import Task

class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task
    
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=200)
    done = factory.Faker('boolean', chance_of_getting_true=25)
    is_seed_data = True  # Marcar como datos del seed
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
    
    @classmethod
    def create_batch_data(cls, count=10):
        """Método para crear datos en lote"""
        return cls.create_batch(count)