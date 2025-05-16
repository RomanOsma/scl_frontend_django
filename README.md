# SCL Inventory - Frontend (Django)

Frontend para el sistema de gestión de inventario SCL. Consume la API del backend.

## Ejecución Local

### Prerrequisitos
*   Python 3.10+
*   pip
*   Git
*   El **Backend FastAPI (`scl_backend_fastapi`) debe estar configurado y ejecutándose** en `http://127.0.0.1:8000` (o según se configure en `.env`).

### Pasos

1.  **Clonar el Repositorio (si aún no lo has hecho):**
    ```bash
    git clone https://github.com/RomanOsma/scl_frontend_django.git
    cd scl_frontend_django
    ```

2.  **Crear y Activar Entorno Virtual:**
    ```bash
    python -m venv venv
    # Windows CMD:
    venv\Scripts\activate.bat
    # Windows PowerShell:
    # venv\Scripts\Activate.ps1
    # macOS/Linux:
    # source venv/bin/activate
    ```

3.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar Variables de Entorno:**
    *   Crea un archivo `.env` en la raíz del proyecto (`scl_frontend_django/.env`).
    *   Añade las siguientes variables:
        ```env
        FASTAPI_BASE_URL=http://127.0.0.1:8000/api/v1
        DJANGO_SECRET_KEY_LOCAL=una_clave_secreta_simple_para_frontend_local
        DJANGO_DEBUG_LOCAL=True
        DJANGO_ALLOWED_HOSTS_LOCAL=127.0.0.1,localhost
        ```
    *   **Importante:** `FASTAPI_BASE_URL` debe apuntar a tu backend local.

5.  **(Opcional) Aplicar Migraciones de Django:**
    ```bash
    python manage.py migrate
    ```

6.  **Ejecutar Servidor Django:**
    ```bash
    python manage.py runserver 8001
    ```

7.  **Acceder a la Aplicación:**
    *   Abre tu navegador y ve a `http://127.0.0.1:8001/`.
    *   Deberías ser redirigido a la página de login: `http://127.0.0.1:8001/portal/login/`.