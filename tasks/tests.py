from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Task
from datetime import datetime, timedelta
from users.models import User

class TaskAPITestCase(APITestCase):
    """
    Batería de tests para la API de tareas.
    Incluye seeders automáticos y tests para todas las funcionalidades CRUD.
    """
    
    @classmethod
    def setUpTestData(cls):
        """
        Carga datos reales de prueba predecibles.
        """
        cls.seed_tasks = [
            Task.objects.create(
                title='Implementar autenticación de usuarios',
                description='Desarrollar sistema de login y registro para la aplicación web',
                done=False,
                is_seed_data=True
            ),
            Task.objects.create(
                title='Diseñar base de datos',
                description='Crear esquema de base de datos con todas las tablas necesarias',
                done=True,
                is_seed_data=True
            ),
            Task.objects.create(
                title='Configurar servidor de producción',
                description='Instalar y configurar servidor web con SSL y dominio',
                done=False,
                is_seed_data=True
            ),
            Task.objects.create(
                title='Escribir documentación API',
                description='Documentar todos los endpoints REST con ejemplos de uso',
                done=True,
                is_seed_data=True
            ),
            Task.objects.create(
                title='Implementar tests unitarios',
                description='Crear suite completa de tests para todas las funcionalidades',
                done=False,
                is_seed_data=True
            )
        ]
    
    def setUp(self):
        """
        Se ejecuta antes de cada test individual.
        Aquí configuramos datos específicos para cada test.
        """
        self.manual_task = Task.objects.create(
            title='Manual Test Task', 
            description='Creado manualmente para el test'
        )

class IntegrationTaskTestsBase(TaskAPITestCase):
    """Clase base para tests de integración con autenticación"""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="alvaro", password="1234")

    def _login_fail_user(self):
        login_response = self.client.post("/api/v1/auth/login/", {
            "username": "alvaro",
            "password": "12345"
        }, format="json")

        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def _logout_user(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=""
        )

    def _login_user(self):
        login_response = self.client.post("/api/v1/auth/login/", {
            "username": "alvaro",
            "password": "1234"
        }, format="json")

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _create_task(self, data):
        response = self.client.post("/api/v1/tasks/", data, format='json')
        return response

    def _update_task(self, id, data):
        response = self.client.put(f"/api/v1/tasks/{id}/", data, format='json')
        return response

    def _get_task(self, id):
        response = self.client.get(f"/api/v1/tasks/{id}/", format='json')
        return response

    def _delete_task(self, id):
        response = self.client.delete(f"/api/v1/tasks/{id}/", format='json')
        return response

    def _update_task_field(self, id, field, value):
        response = self.client.patch(f"/api/v1/tasks/{id}/", {field: value}, format='json')
        return response

    def _search_task(self, query):
        response = self.client.get(f"/api/v1/tasks/?search={query}", format='json')
        return response

    def _filter_task(self, field, value):
        response = self.client.get(f"/api/v1/tasks/?{field}={value}", format='json')
        return response

class IntegrationPostTests(IntegrationTaskTestsBase):
    """Tests de integración para método POST (CREATE)"""

    def test_create_task_with_authentication(self):
        self._login_user()

        data = {
            'title': 'Tarea de Test',
            'description': 'Descripción de la tarea de test'
        }

        response = self._create_task(data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Tarea de Test')
        self.assertEqual(response.data['description'], 'Descripción de la tarea de test')

    def test_create_task_with_authentication_fails(self):
        self._login_fail_user()

        data = {
            'title': 'Tarea de Test',
            'description': 'Descripción de la tarea de test'
        }

        response = self._create_task(data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_with_authentication_and_missing_fields_fails(self):
        self._login_user()

        data = {
            'title': 'Tarea de Test',
        }

        response = self._create_task(data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class IntegrationGetTests(IntegrationTaskTestsBase):
    """Tests de integración para método GET (READ)"""

    def test_get_task_with_authentication(self):
        self._login_user()

        data = {
            'title': 'Tarea de Test a obtener',
            'description': 'Descripción de la tarea de test a obtener'
        }

        response = self._create_task(data)
        response = self._get_task(response.data['id'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Tarea de Test a obtener')
        self.assertEqual(response.data['description'], 'Descripción de la tarea de test a obtener')

    def test_get_task_with_authentication_fails(self):
        self._login_fail_user()

        response = self._get_task(self.manual_task.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_task_with_invalid_uuid_fails(self):
        self._login_user()

        response = self._get_task('invalid-uuid')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_task_with_nonexistent_task_fails(self):
        self._login_user()

        response = self._get_task('00000000-0000-0000-0000-000000000000')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class IntegrationPutPatchTests(IntegrationTaskTestsBase):
    """Tests de integración para métodos PUT/PATCH (UPDATE)"""

    def test_update_task_with_authentication(self):
        self._login_user()

        data = {
            'title': 'Tarea de Test a actualizar',
            'description': 'Descripción de la tarea de test a actualizar',
            'done': False
        }

        response = self._create_task(data)

        data = {
            'title': 'Tarea de Test Actualizada',
            'description': 'Descripción de la tarea de test actualizada',
            'done': True
        }

        response = self._update_task(response.data['id'], data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Tarea de Test Actualizada')
        self.assertEqual(response.data['description'], 'Descripción de la tarea de test actualizada')

    def test_update_task_incomplete_data_with_authentication_fails(self):
        self._login_user()

        data = {
            'title': 'Tarea de Test a actualizar',
            'description': 'Descripción de la tarea de test a actualizar',
            'done': False
        }

        response = self._create_task(data)

        data = {
            'title': 'Tarea de Test Actualizada',
        }

        response = self._update_task(response.data['id'], data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_task_field_with_authentication(self):
        self._login_user()

        data = {
            'title': 'Tarea de Test a actualizar campo',
            'description': 'Descripción de la tarea de test a actualizar campo',
            'done': False
        }

        response = self._create_task(data)
        response = self._update_task_field(response.data['id'], 'done', True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['done'])

    def test_update_task_field_with_authentication_fails(self):
        self._login_fail_user()

        response = self._update_task_field(self.manual_task.id, 'done', True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class IntegrationDeleteTests(IntegrationTaskTestsBase):
    """Tests de integración para método DELETE"""

    def test_delete_task_with_authentication(self):
        self._login_user()

        data = {
            'title': 'Tarea de Test a eliminar',
            'description': 'Descripción de la tarea de test a eliminar'
        }

        response = self._create_task(data)
        response = self._delete_task(response.data['id'])

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_task_with_authentication_fails(self):
        self._login_fail_user()

        response = self._delete_task(self.manual_task.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class IntegrationFilteringTests(IntegrationTaskTestsBase):
    """Tests de integración para filtrado y búsqueda de tareas con autenticación"""
    
    def setUp(self):
        super().setUp()
        
        self._login_user()
        
        self.completed_task_data = {
            'title': 'Tarea Completada',
            'description': 'Esta tarea está completada',
            'done': True
        }
        completed_response = self._create_task(self.completed_task_data)
        self.completed_task_id = completed_response.data['id']
        
        self.pending_task_data = {
            'title': 'Tarea Pendiente',
            'description': 'Esta tarea está pendiente',
            'done': False
        }
        pending_response = self._create_task(self.pending_task_data)
        self.pending_task_id = pending_response.data['id']
        
        self.search_task_data = {
            'title': 'Implementar autenticación de usuarios',
            'description': 'Desarrollar sistema de login con servidor seguro',
            'done': False
        }
        search_response = self._create_task(self.search_task_data)
        self.search_task_id = search_response.data['id']

        self._logout_user()
    
    def test_filter_tasks_by_completion_status(self):
        """Test: Filtrar tareas por estado de completado"""
        self._login_user()
        
        response = self._filter_task('done', 'true')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        completed_tasks = [task for task in response.data if task['done']]
        self.assertTrue(len(completed_tasks) >= 1)
        
        completed_task_ids = [task['id'] for task in completed_tasks]
        self.assertIn(self.completed_task_id, completed_task_ids)
        
        response = self._filter_task('done', 'false')
        
        pending_tasks = [task for task in response.data if not task['done']]
        self.assertTrue(len(pending_tasks) >= 1)
        
        pending_task_ids = [task['id'] for task in pending_tasks]
        self.assertIn(self.pending_task_id, pending_task_ids)
    
    def test_search_tasks_by_title(self):
        self._login_user()

        response = self._search_task('autenticación')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        
        found_task = next((task for task in response.data if 'autenticación' in task['title']), None)
        self.assertIsNotNone(found_task)
        
        search_task_ids = [task['id'] for task in response.data]
        self.assertIn(self.search_task_id, search_task_ids)
    
    def test_search_tasks_by_description(self):
        self._login_user()

        response = self._search_task('servidor')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        found_task = next((task for task in response.data if 'servidor' in task['description'].lower()), None)
        self.assertIsNotNone(found_task)
        
        search_task_ids = [task['id'] for task in response.data]
        self.assertIn(self.search_task_id, search_task_ids)
    
    def test_filter_tasks_by_creation_date(self):
        self._login_user()
        
        today = timezone.now().date()
        
        response = self._filter_task('created_at', today.isoformat())

        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for task in response.data:
            task_date = timezone.datetime.fromisoformat(task['created_at'].replace('Z', '+00:00')).date()
            self.assertEqual(task_date, today)
        
        today_task_ids = [task['id'] for task in response.data]
        self.assertIn(self.completed_task_id, today_task_ids)
        self.assertIn(self.pending_task_id, today_task_ids)
        self.assertIn(self.search_task_id, today_task_ids)
    
    
    def test_combined_filters(self):
        self._login_user()
        
        response = self._filter_task('search', 'Implementar')
        response = self._filter_task('done', 'false')
        response = self._filter_task('search', 'Implementar')
        response = self._filter_task('done', 'false')
        
        response = self.client.get("/api/v1/tasks/", {
            'search': 'Implementar',
            'done': 'false'
        }, format='json')
        
        response = self.client.get("/api/v1/tasks/", {
            'search': 'Implementar',
            'done': 'false'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for task in response.data:
            self.assertFalse(task['done'])
            self.assertTrue('Implementar' in task['title'] or 'Implementar' in task['description'])
        
        combined_task_ids = [task['id'] for task in response.data]
        self.assertIn(self.search_task_id, combined_task_ids)

    def test_filter_tasks_without_authentication_fails(self):
        self._login_fail_user()
        
        response = self._filter_task('done', 'true')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_tasks_without_authentication_fails(self):
        self._login_fail_user()
        
        response = self._search_task('test')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        