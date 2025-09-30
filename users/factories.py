import factory
from factory.django import DjangoModelFactory
from users.models import User

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    username = factory.SelfAttribute('email')
    is_seed_data = True
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            obj.set_password(extracted)
        else:
            obj.set_password('password123') 
        obj.save()

    @classmethod
    def create_batch_data(cls, count=10):
        return cls.create_batch(count)