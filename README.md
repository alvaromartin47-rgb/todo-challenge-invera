# Invera API Tasks

Una API REST desarrollada con Django y Django REST Framework para la gestión de tareas, con base de datos PostgreSQL y configuración Docker.

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Configuración Inicial](#configuración-inicial)
- [Desarrollo Local](#desarrollo-local)
- [Despliegue con Docker](#despliegue-con-docker)
- [Testing](#testing)

## 🔧 Requisitos Previos

### Para Desarrollo Local:
- Python 3.12+
- Conda o virtualenv
- Docker y Docker Compose (para la base de datos)
- PostgreSQL client (opcional, para conexión directa a BD)

### Para Despliegue:
- Docker
- Docker Compose

## ⚙️ Configuración Inicial

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd invera
```

### 2. Configurar variables de entorno
Crear un archivo `.env` basado en `env.example`:
```bash
cp env.example .env
```

Editar el archivo `.env` con tus configuraciones:
```env
# App Configuration
API_PORT=4000
ACCESS_TOKEN_LIFETIME= # in minutes
REFRESH_TOKEN_LIFETIME= # in days
SECRET_KEY=

# Database Configuration
DB_NAME=invera
DB_USER=user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
POSTGRES_VOLUME=invera_data
```

## 🚀 Desarrollo Local

### 1. Crear entorno virtual con Conda
```bash
conda create -n invera python=3.12
conda activate invera
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Levantar base de datos con Docker
```bash
docker compose up db -d
```

### 4. Crear y ejecutar migraciones
```bash
# Crear migraciones basadas en cambios en los modelos
python manage.py makemigrations

# Opcionalmente, usa --name para dar un nombre descriptivo a la migración
python manage.py makemigrations --name nombre_descriptivo

# Aplicar las migraciones a la base de datos
python manage.py migrate
```

### 5. Crear un superusuario (opcional)
```bash
python manage.py createsuperuser
```
> Este comando te solicitará nombre de usuario, email y contraseña para acceder al panel de administración de Django en `/admin`.

### 6. Cargar datos de prueba (opcional)

#### Cargar todos los seeders
```bash
python manage.py seed_all
```

#### Cargar seeders específicos
```bash
# Cargar solo tareas
python manage.py seed_tasks

# Cargar solo usuarios
python manage.py seed_users
```

#### Opciones adicionales
```bash
# Especificar cantidad de registros a generar
python manage.py seed_all --number 20
python manage.py seed_tasks --number 15

# Limpiar datos existentes antes de generar nuevos
python manage.py seed_all --clean
python manage.py seed_tasks --clean
```

> Los seeders generarán datos aleatorios para facilitar el desarrollo. Por defecto se crean 10 registros por modelo.

### 7. Iniciar servidor de desarrollo
```bash
python manage.py runserver
```

La API estará disponible en: `http://localhost:4000` (o el puerto configurado en `API_PORT`)

## 🐳 Despliegue con Docker

### Para entornos QA/Producción:

### 1. Construir y levantar todos los servicios
```bash
docker compose up --build -d
```

### 2. Crear y ejecutar migraciones en el contenedor
```bash
# Crear migraciones basadas en cambios en los modelos
docker exec invera-api python manage.py makemigrations

# Opcionalmente, usa --name para dar un nombre descriptivo a la migración
docker exec invera-api python manage.py makemigrations --name nombre_descriptivo

# Aplicar las migraciones a la base de datos
docker exec invera-api python manage.py migrate
```

### 3. Crear un superusuario (opcional)
```bash
docker exec -it invera-api python manage.py createsuperuser
```
> Este comando te solicitará nombre de usuario, email y contraseña para acceder al panel de administración de Django en `/admin`.

### 4. Cargar datos de prueba (opcional)

#### Cargar todos los seeders
```bash
docker exec invera-api python manage.py seed_all
```

#### Cargar seeders específicos
```bash
# Cargar solo tareas
docker exec invera-api python manage.py seed_tasks

# Cargar solo usuarios
docker exec invera-api python manage.py seed_users
```

#### Opciones adicionales
```bash
# Especificar cantidad de registros a generar
docker exec invera-api python manage.py seed_all --number 20
docker exec invera-api python manage.py seed_tasks --number 15

# Limpiar datos existentes antes de generar nuevos
docker exec invera-api python manage.py seed_all --clean
docker exec invera-api python manage.py seed_tasks --clean
```

La API estará disponible en: `http://localhost:4000` (o el puerto configurado en `API_PORT`)

## 🧪 Testing

Para ejecutar los tests localmente, necesitas tener la base de datos levantada y luego usar el comando estándar de Django para testing.

### Preparación para tests

1. **Levantar la base de datos con Docker Compose:**
```bash
docker compose up db -d
```

2. **Asegurar que tienes el entorno virtual activado:**
```bash
conda activate invera
```

### Ejecutar todos los tests

```bash
python manage.py test
```

### Ejecutar tests específicos

Puedes especificar el módulo o test específico que quieres ejecutar:

```bash
# Ejecutar todos los tests de una aplicación
python manage.py test tasks.tests

# Ejecutar una clase de tests específica
python manage.py test tasks.tests.TaskCRUDTests

# Ejecutar un test específico
python manage.py test tasks.tests.TaskCRUDTests.test_create_task_success
```

