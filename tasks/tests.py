from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Task
from datetime import datetime, timedelta

# Create your tests here.

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


# =============================================================================
# TESTS CRUD DE TAREAS
# =============================================================================

class TaskCRUDTests(TaskAPITestCase):
    """Tests para operaciones CRUD de tareas"""
    
    def test_create_task_success(self):
        """Test: Crear una nueva tarea"""
        url = reverse('task-list')
        data = {
            'title': 'Nueva Tarea de Test',
            'description': 'Descripción de la nueva tarea',
            'done': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Nueva Tarea de Test')
        self.assertEqual(response.data['description'], 'Descripción de la nueva tarea')
        self.assertFalse(response.data['done'])
        
        # Verificar que se guardó en BD
        task = Task.objects.get(id=response.data['id'])
        self.assertEqual(task.title, 'Nueva Tarea de Test')
    
    def test_list_all_tasks(self):
        """Test: Ver lista de todas las tareas existentes"""
        url = reverse('task-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 5 seed tasks + 1 manual task = 6 total
        self.assertEqual(len(response.data), 6)
    
    def test_retrieve_single_task(self):
        """Test: Obtener una tarea específica"""
        url = reverse('task-detail', args=[self.manual_task.id])
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Manual Test Task')
        self.assertEqual(response.data['id'], str(self.manual_task.id))
    
    def test_update_task_success(self):
        """Test: Actualizar una tarea existente"""
        url = reverse('task-detail', args=[self.manual_task.id])
        data = {
            'title': 'Tarea Actualizada',
            'description': 'Descripción actualizada',
            'done': True
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Tarea Actualizada')
        self.assertTrue(response.data['done'])
        
        # Verificar en BD
        task = Task.objects.get(id=self.manual_task.id)
        self.assertEqual(task.title, 'Tarea Actualizada')
        self.assertTrue(task.done)
    
    def test_mark_task_as_completed(self):
        """Test: Marcar tarea como completada"""
        url = reverse('task-detail', args=[self.manual_task.id])
        data = {
            'title': self.manual_task.title,
            'description': self.manual_task.description,
            'done': True  # Marcar como completada
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['done'])
        
        # Verificar en BD
        task = Task.objects.get(id=self.manual_task.id)
        self.assertTrue(task.done)
    
    def test_partial_update_task(self):
        """Test: Actualización parcial de tarea (PATCH)"""
        url = reverse('task-detail', args=[self.manual_task.id])
        data = {'done': True}  # Solo actualizar el campo 'done'
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['done'])
        # El título debe permanecer igual
        self.assertEqual(response.data['title'], 'Manual Test Task')
    
    def test_delete_task_success(self):
        """Test: Eliminar una tarea"""
        task_id = self.manual_task.id
        url = reverse('task-detail', args=[task_id])
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que se eliminó de BD
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=task_id)
    
    def test_delete_nonexistent_task(self):
        """Test: Fallo al eliminar tarea que no existe"""
        url = reverse('task-detail', args=['00000000-0000-0000-0000-000000000000'])
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# =============================================================================
# TESTS DE FILTRADO Y BÚSQUEDA
# =============================================================================

class TaskFilteringTests(TaskAPITestCase):
    """Tests para filtrado y búsqueda de tareas"""
    
    def setUp(self):
        super().setUp()
        
        # Crear tareas específicas para filtrado
        self.completed_task = Task.objects.create(
            title='Tarea Completada',
            description='Esta tarea está completada',
            done=True
        )
        
        self.pending_task = Task.objects.create(
            title='Tarea Pendiente',
            description='Esta tarea está pendiente',
            done=False
        )
        
        # Crear tarea con fecha específica (ayer)
        yesterday = timezone.now() - timedelta(days=1)
        self.old_task = Task.objects.create(
            title='Tarea de Ayer',
            description='Tarea creada ayer'
        )
        self.old_task.created_at = yesterday
        self.old_task.save()
    
    def test_filter_tasks_by_completion_status(self):
        """Test: Filtrar tareas por estado de completado"""
        # Filtrar tareas completadas
        url = reverse('task-list')
        response = self.client.get(url, {'done': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        completed_tasks = [task for task in response.data if task['done']]
        self.assertTrue(len(completed_tasks) >= 1)
        
        # Filtrar tareas pendientes
        response = self.client.get(url, {'done': 'false'})
        pending_tasks = [task for task in response.data if not task['done']]
        self.assertTrue(len(pending_tasks) >= 1)
    
    def test_search_tasks_by_title(self):
        """Test: Buscar tareas por título"""
        url = reverse('task-list')
        response = self.client.get(url, {'search': 'autenticación'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        
        # Verificar que contiene la palabra buscada
        found_task = next((task for task in response.data if 'autenticación' in task['title']), None)
        self.assertIsNotNone(found_task)
    
    def test_search_tasks_by_description(self):
        """Test: Buscar tareas por contenido/descripción"""
        url = reverse('task-list')
        response = self.client.get(url, {'search': 'servidor'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que encontró tareas con esa palabra en descripción
        found_task = next((task for task in response.data 
                          if 'servidor' in task['description'].lower()), None)
        self.assertIsNotNone(found_task)
    
    def test_filter_tasks_by_creation_date(self):
        """Test: Filtrar tareas por fecha de creación"""
        url = reverse('task-list')
        today = timezone.now().date()
        
        # Filtrar tareas de hoy usando el formato correcto que espera la API
        response = self.client.get(url, {'created_at': today.isoformat()})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que las tareas devueltas son de hoy
        for task in response.data:
            task_date = timezone.datetime.fromisoformat(task['created_at'].replace('Z', '+00:00')).date()
            self.assertEqual(task_date, today)
    
    
    def test_combined_filters(self):
        """Test: Combinación de filtros (búsqueda + estado)"""
        url = reverse('task-list')
        response = self.client.get(url, {
            'search': 'Implementar',
            'done': 'false'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que todas las tareas devueltas están pendientes y contienen "Implementar"
        for task in response.data:
            self.assertFalse(task['done'])
            self.assertTrue('Implementar' in task['title'] or 'Implementar' in task['description'])


# =============================================================================
# TESTS DE CASOS EDGE
# =============================================================================

class TaskEdgeCasesTests(TaskAPITestCase):
    """Tests para casos edge y validaciones"""
    
    def test_create_task_missing_required_fields(self):
        """Test: Crear tarea sin campos requeridos"""
        url = reverse('task-list')
        data = {}  # Sin datos requeridos
        
        response = self.client.post(url, data, format='json')
        
        # Debería fallar por campos faltantes
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_task_with_very_long_title(self):
        """Test: Crear tarea con título muy largo"""
        url = reverse('task-list')
        data = {
            'title': 'A' * 300,  # Título muy largo
            'description': 'Test description'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debería fallar si el modelo tiene límite de caracteres
        if response.status_code != status.HTTP_201_CREATED:
            self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST])
    
    def test_get_task_with_invalid_uuid(self):
        """Test: Obtener tarea con UUID inválido"""
        url = reverse('task-detail', args=['invalid-uuid'])
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_nonexistent_task(self):
        """Test: Actualizar tarea que no existe"""
        url = reverse('task-detail', args=['00000000-0000-0000-0000-000000000000'])
        data = {
            'title': 'Tarea Inexistente',
            'description': 'Esta tarea no existe'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)