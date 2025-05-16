# PowerShell script to create Sweatz app project structure
Write-Host "Creating Sweatz App basic folder structure..." -ForegroundColor Green

# Create main project directory (we're already in it, so no need to create or cd)

# Create app package and subpackages
New-Item -ItemType Directory -Path "app" -Force
New-Item -ItemType Directory -Path "app\api", "app\models", "app\services", "app\utils" -Force
New-Item -ItemType Directory -Path "app\static", "app\static\css", "app\static\css\components", "app\static\js", "app\static\js\components", "app\static\img" -Force
New-Item -ItemType Directory -Path "app\templates", "app\templates\auth", "app\templates\nutrition", "app\templates\body", "app\templates\workouts" -Force

# Create mobile directories
New-Item -ItemType Directory -Path "mobile", "mobile\android", "mobile\ios" -Force

# Create tests directory
New-Item -ItemType Directory -Path "tests" -Force

# Create migrations directory
New-Item -ItemType Directory -Path "migrations" -Force

# Create empty __init__.py files
New-Item -ItemType File -Path "app\__init__.py" -Force
New-Item -ItemType File -Path "app\api\__init__.py" -Force
New-Item -ItemType File -Path "app\models\__init__.py" -Force
New-Item -ItemType File -Path "app\services\__init__.py" -Force
New-Item -ItemType File -Path "app\utils\__init__.py" -Force
New-Item -ItemType File -Path "tests\__init__.py" -Force

# Create empty config file
New-Item -ItemType File -Path "app\config.py" -Force

# Create empty API modules
New-Item -ItemType File -Path "app\api\auth.py", "app\api\nutrition.py", "app\api\body.py", "app\api\workouts.py", "app\api\reminders.py" -Force

# Create empty models
New-Item -ItemType File -Path "app\models\user.py", "app\models\nutrition.py", "app\models\body.py", "app\models\workouts.py", "app\models\reminders.py" -Force

# Create empty services
New-Item -ItemType File -Path "app\services\auth_service.py", "app\services\nutrition_service.py", "app\services\workout_service.py", "app\services\ai_service.py" -Force

# Create empty utility files
New-Item -ItemType File -Path "app\utils\validators.py", "app\utils\security.py", "app\utils\formatters.py" -Force

# Create empty template files
New-Item -ItemType File -Path "app\templates\base.html", "app\templates\index.html" -Force
New-Item -ItemType File -Path "app\templates\auth\login.html", "app\templates\auth\register.html" -Force

# Create empty static files
New-Item -ItemType File -Path "app\static\css\styles.css" -Force
New-Item -ItemType File -Path "app\static\js\app.js" -Force
New-Item -ItemType File -Path "app\static\manifest.json" -Force

# Create empty root files
New-Item -ItemType File -Path "run.py", "wsgi.py", "requirements.txt", ".env", ".gitignore", "README.md" -Force

Write-Host "Sweatz App basic folder structure created successfully!" -ForegroundColor Green
Write-Host "Now we can implement each file one by one." -ForegroundColor Yellow