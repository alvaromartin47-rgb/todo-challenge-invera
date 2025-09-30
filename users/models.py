import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.
    Se integra completamente con el sistema de autenticación de Django.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_seed_data = models.BooleanField(default=False, help_text="Indica si el usuario fue creado como datos de prueba")
    
    # AbstractUser incluye: username, password (hasheado), email, first_name, last_name,
    # is_active, is_staff, is_superuser, date_joined, last_login, groups, user_permissions
    # Y todos los métodos necesarios: check_password(), set_password(), etc.
    
    USERNAME_FIELD = 'username'  # Campo para autenticación
    REQUIRED_FIELDS = ['email']   # Campos adicionales requeridos al crear superuser
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
  
    def __str__(self):
        return self.username