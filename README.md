# SISTEMA INTEGRAL DE CONTROL PRENATAL

Aplicación web para la gestión integral del control prenatal, desarrollada con Flask y Supabase.

## 📋 Características

- Gestión de pacientes embarazadas
- Programación y seguimiento de citas prenatales
- Registro de inasistencias
- Módulo de censos poblacionales
- Generación de reportes clínicos y estadísticos
- Autenticación y autorización de usuarios
- Panel de control intuitivo

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Base de datos**: Supabase (PostgreSQL)
- **Frontend**: HTML/CSS/JavaScript con Jinja2 templates
- **Autenticación**: Supabase Auth
- **ORM**: Pydantic para validación de datos
- **Variables de entorno**: python-dotenv

## 📦 Requisitos Previos

- Python 3.8+
- Cuenta en Supabase
- Git (opcional, para versionado)

## ⚙️ Instalación y Configuración

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/SISTEMA-INTEGRAL-DE-CONTROL-PRENATAL.git
   cd SISTEMA-INTEGRAL-DE-CONTROL-PRENATAL
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Unix/Linux/macOS:
   source .venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   - Copiar `.env.example` a `.env` (o crear uno nuevo)
   - Configurar las credenciales de Supabase:
     ```
     SUPABASE_URL=tu_url_de_supabase
     SUPABASE_KEY=tu_anon_key_de_supabase
     ```

5. **Configurar la base de datos**
   - Ejecutar el script SQL en tu proyecto Supabase:
     ```bash
     # Acceder al SQL editor en Supabase Dashboard
     # Copiar y ejecutar el contenido de script.sql
     ```

## 🚀 Ejecución

```bash
# Desde el directorio raíz
python web/run.py
```

La aplicación estará disponible en `http://localhost:5000`

## 🗂️ Estructura del Proyecto

```
SISTEMA-INTEGRAL-DE-CONTROL-PRENATAL/
├── web/                    # Aplicación Flask principal
│   ├── controllers/       # Manejadores de rutas (blueprints)
│   │   ├── auth.py        # Autenticación y autorización
│   │   ├── dashboard.py   # Panel de control
│   │   ├── pacientes.py   # Gestión de pacientes
│   │   ├── citas.py       # Gestión de citas
│   │   ├── inasistencias.py # Registro de inasistencias
│   │   ├── censo.py       # Módulo de censos
│   │   └── reportes.py    # Generación de reportes
│   ├── models/            # Modelos de datos
│   ├── services/          # Lógica de negocio
│   ├── templates/         # Plantillas HTML (Jinja2)
│   ├── static/            # Archivos estáticos (CSS, JS, imágenes)
│   ├── utils/             # Funciones de utilidad
│   ├── config.py          # Configuración de la aplicación
│   ├── init.py            # Inicialización de la app Flask
│   └── run.py             # Punto de entrada
├── script.sql             # Esquema de la base de datos
├── requirements.txt       # Dependencias de Python
├── .env                   # Variables de entorno (no versionado)
└── .gitignore             # Archivos ignorados por Git
```

## 🔐 Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto con:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key_aquí
```

## 🗄️ Base de Datos

El esquema de la base de datos se encuentra en `script.sql` y incluye tablas para:
- Usuarios y roles
- Pacientes embarazadas
- Citas prenatales
- Historial clínico
- Inasistencias
- Censos poblacionales
- Reportes y estadísticas

Para inicializar la base de datos:
1. Acceder al panel de Supabase
2. Abrir el SQL Editor
3. Ejecutar el contenido completo de `script.sql`

## 🧪 Pruebas

Actualmente, las pruebas se realizan manualmente mediante el navegador web:
1. Iniciar la aplicación con `python web/run.py`
2. Navegar a `http://localhost:5000`
3. Probar los diferentes módulos según los roles de usuario

## 🤝 Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Autores

- Equipo de desarrollo del proyecto integrador

## 🙏 Agradecimientos

- Supabase por proporcionar una excelente plataforma backend
- Comunidad Flask por el framework robusto y flexible
- Todos los contribuidores al proyecto