# Videoflix Backend API

Eine Django-basierte REST API für eine Video-Streaming-Plattform mit Benutzerauthentifizierung, Video-Management und Background Job Processing.

## 📋 Inhaltsverzeichnis

- [Projektübersicht](#projektübersicht)
- [Anforderungen](#anforderungen)
- [Installation mit Docker](#installation-mit-docker)
- [Konfiguration](#konfiguration)
- [Docker Container Befehle](#-docker-container-befehle)
- [Datenbankmigrationen](#datenbankmigrationen)
- [API Endpoints](#api-endpoints)
- [Background Jobs & Task Queue](#background-jobs--task-queue)
- [Entwicklung](#entwicklung)
- [Troubleshooting](#troubleshooting)

---

## 📺 Projektübersicht

Videoflix ist eine moderne Video-Streaming-Anwendung mit den folgenden Features:

- **Benutzerauthentifizierung**: JWT-basierte Authentifizierung mit Email-Aktivierung
- **Video-Management**: CRUD-Operationen für Videos mit Metadaten
- **Task Queue**: Asynchrone Job-Verarbeitung via Redis Queue (RQ)
- **Caching**: Redis-basiertes Caching für Performance-Optimierung
- **CORS-Support**: Cross-Origin-Requests für Frontend-Integration
- **Statische Dateien**: Optimiertes Serving mit WhiteNoise (Produktion)

### 🏗️ Tech Stack

| Komponente        | Technologie                         |
| ----------------- | ----------------------------------- |
| Framework         | Django 6.0.2                        |
| API               | Django REST Framework 3.16.1        |
| Authentifizierung | JWT (djangorestframework-simplejwt) |
| Datenbank         | PostgreSQL                          |
| Cache/Queue       | Redis                               |
| Task Queue        | RQ (Redis Queue)                    |
| Server            | Gunicorn (Produktion)               |
| Containerization  | Docker & Docker Compose             |

---

## ⚙️ Anforderungen

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git** (optional, zum Klonen des Repositories)
- ~2GB freier Speicher

---

## 🚀 Installation mit Docker

#### Schritt 1: Repository klonen

```bash
git clone <repository-url>
cd backend
```

#### Schritt 2: Umgebungsvariablen konfigurieren

Erstelle eine `.env`-Datei im Projekt-Root (Details siehe [Konfiguration](#konfiguration)).

#### Schritt 3: Docker Images bauen und Container starten

```bash
docker-compose up -d
```

Dies startet folgende Container:

- `videoflix_backend` - Django API (Gunicorn Server)
- `videoflix_database` - PostgreSQL Datenbank
- `videoflix_redis` - Redis Cache & Job Queue

#### Schritt 4: Datenbankmigrationen ausführen

```bash
docker-compose exec web python manage.py migrate
```

#### Schritt 5: Superuser erstellen (für Admin)

```bash
docker-compose exec web python manage.py createsuperuser
```

Folge den Anweisungen zur Eingabe von Benutzername, Email und Passwort.

#### ✅ Überprüfung

Die API ist nun verfügbar unter:

- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/

---

## 🔧 Konfiguration

### `.env` Datei erstellen

Erstelle eine `.env`-Datei im Projekt-Root mit den Variablen aus der .env.template:

### 📧 Ethereal Email für Testzwecke

Diese Anwendung nutzt **Ethereal Email** für die Email-Aktivierung bei Usern (zu Testzwecken). Ethereal ist ein kostenloser, webbasierter Fake-SMTP-Service, perfect für Entwicklung und Testing.

#### Ethereal Account erstellen:

1. Besuche https://ethereal.email/
2. Klicke auf **"Create Ethereal Account"**
3. Kopiere die generierten SMTP-Authdaten:
   - **Host**: `smtp.ethereal.email`
   - **Port**: `587`
   - **Security**: `TLS`
   - **Username**: (deine Ethereal Email)
   - **Password**: (dein generiertes Passwort)

4. Füge diese Werte in deine `.env` ein:
   ```env
   EMAIL_HOST_USER=xxxxxxxxxxxx@ethereal.email
   EMAIL_HOST_PASSWORD=zzzzzzzzzzzzzzzzz
   ```

#### Versendete Emails anschauen:

Alle über Ethereal versendeten Emails sind sofort auf der Ethereal Website unter **"Messages"** einsehbar. Dort kannst du:

- Aktivierungs-Links kopieren
- Email-Inhalte überprüfen
- Fehler debuggen

#### ⚡ Wichtig für Produktion:

Für den produktiven Einsatz sollte man auf einen echten SMTP-Service wie **Gmail**, **SendGrid** oder **AWS SES** umsteigen und die entsprechenden Credentials konfigurieren.

---

## 🐳 Docker Container Befehle

```bash
# Container starten (im Background)
docker-compose up -d

# Logs anschauen (alle Container)
docker-compose logs -f

# Logs anschauen (nur Django)
docker-compose logs -f web

# Container stoppen
docker-compose down

# Container neu starten
docker-compose restart web

# Django Shell im Container
docker-compose exec web python manage.py shell

# Beliebigen Command im Container ausführen
docker-compose exec web [command]
```

---

## 🗄️ Datenbankmigrationen

Migrationen verwalten die Datenbankstruktur. Sie müssen bei jeder Änderung am Datenmodell ausgeführt werden.

```bash
# Neue Migrationen erstellen
docker-compose exec web python manage.py makemigrations

# Migrationen auf Datenbank anwenden
docker-compose exec web python manage.py migrate
```

### Häufige Migration-Befehle

```bash
# Status der Migrationen anzeigen
docker-compose exec web python manage.py showmigrations

# Spezifische Migration rückgängig machen
docker-compose exec web python manage.py migrate auth_app 0001

# Alle Migrationen einer App zurücksetzen (Vorsicht!)
docker-compose exec web python manage.py migrate auth_app zero
```

---

## 📡 API Endpoints

### Authentifizierung

```
POST   /api/auth/login/         - Login und JWT Token erhalten
POST   /api/auth/register/      - Neuen Account registrieren
POST   /api/auth/refresh/       - Token refreshen
POST   /api/auth/logout/        - Logout
GET    /api/auth/activate/<uid>/<token>/ - Email bestätigen
```

### Videos

```
GET    /api/videos/             - Alle Videos abrufen
POST   /api/videos/             - Neues Video erstellen (Admin)
GET    /api/videos/<id>/        - Video-Details
PUT    /api/videos/<id>/        - Video aktualisieren (Admin)
DELETE /api/videos/<id>/        - Video löschen (Admin)
```

### Admin Panel

```
GET    /admin/                  - Django Admin Interface
```

---

## 🔄 Background Jobs & Task Queue

Die Anwendung nutzt Redis Queue (RQ) für asynchrone Tasks wie Email-Versand.

### RQ Worker als zusätzlicher Container

Bearbeite `docker-compose.yml` und füge hinzu:

```yaml
worker:
  build:
    context: .
    dockerfile: backend.Dockerfile
  container_name: videoflix_worker
  command: python manage.py rqworker default
  volumes:
    - .:/app
  environment:
    - PYTHONUNBUFFERED=1
  depends_on:
    - db
    - redis
  env_file: .env
```

Dann starten mit:

```bash
docker-compose up -d
```

---

## 👨‍💻 Entwicklung

### Code-Struktur

```
backend/
├── auth_app/           # Benutzerauthentifizierung
│   ├── models.py       # User Model & SignUp
│   ├── api/
│   │   ├── views.py    # Auth Endpoints
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── tasks.py        # Background Jobs (Email)
│   └── emails.py       # Email Templates
│
├── video_app/          # Video-Management
│   ├── models.py       # Video & Genre Models
│   ├── api/
│   │   ├── views.py    # Video Endpoints
│   │   ├── serializers.py
│   │   └── urls.py
│   └── signals.py
│
├── core/               # Django Config
│   ├── settings.py     # Settings & Config
│   ├── urls.py         # URL Routing
│   ├── asgi.py
│   └── wsgi.py
│
├── docker-compose.yml  # Docker Konfiguration
├── backend.Dockerfile  # Docker Image Definition
├── requirements.txt    # Python Dependencies
└── manage.py           # Django CLI
```

### Neue Features entwickeln

Die gesamte Entwicklung erfolgt innerhalb des Docker Containers. So wird sichergestellt, dass die Entwicklungsumgebung identisch mit der Produktionsumgebung ist.

#### 1. Modell erstellen

```bash
# Bearbeite video_app/models.py (in deinem Editor)
# Die Datei wird automatisch im Container aktualisiert (Volume Mapping)
```

#### 2. Migration erstellen

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

#### 3. Serializer & ViewSet erstellen

Bearbeite die Dateien lokal in deinem Editor:

- `video_app/api/serializers.py`
- `video_app/api/views.py`
- `video_app/api/urls.py`

Änderungen werden automatisch im Container aktualisiert (wegen `volumes: .:/app` in docker-compose.yml).

#### 4. Testen im Container

```bash
docker-compose exec web python manage.py test video_app
```

#### 5. Django Shell nutzen

```bash
docker-compose exec web python manage.py shell
>>> from auth_app.models import SignUp
>>> SignUp.objects.all()
```

---

## 🐛 Troubleshooting

### Docker-Probleme

#### ❌ Container starten nicht

```bash
# Logs prüfen
docker-compose logs web

# Container recyceln
docker-compose down
docker-compose up -d --build  # Neubauen
```

#### ❌ "Permission denied" beim Exec

```bash
# Mit sudo versuchen
sudo docker-compose exec web python manage.py migrate
```

#### ❌ "Port 8000 already in use"

```bash
# Find Prozess auf Port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Mac/Linux

# Alternative Port nutzen
docker-compose up -d -p "8001:8000"
```

### Datenbankprobleme

#### ❌ "relation does not exist" Error

```bash
# Migrationen zurücksetzen und neu ausführen
docker-compose exec web python manage.py migrate video_app zero
docker-compose exec web python manage.py migrate
```

#### ❌ PostgreSQL Connection refused

```bash
# PostgreSQL-Container Status prüfen
docker-compose logs db

# Container neu starten
docker-compose restart db
```

#### ❌ Superuser Login funktioniert nicht

```bash
# Neuen Superuser erstellen
docker-compose exec web python manage.py createsuperuser
```

### Redis/Queue Probleme

#### ❌ "ConnectionError: Cannot connect to Redis"

```bash
# Redis-Container prüfen
docker-compose logs redis

# Redis Status prüfen
docker-compose exec redis redis-cli ping  # Sollte "PONG" ausgeben

# Container neu starten
docker-compose restart redis
```

#### ❌ Background Jobs werden nicht ausgeführt

```bash
# RQ Worker Container läuft nicht?
# Stelle sicher, dass du einen Worker-Service in docker-compose.yml hast (siehe Background Jobs Sektion)

# Worker-Service starten (falls als Service definiert)
docker-compose up -d worker

# Logs anschauen
docker-compose logs worker

# Jobs in Queue anschauen
docker-compose exec redis redis-cli -n 0 KEYS "*"
```

---

#### ❌ Emails werden nicht versendet

```bash
# 1. SMTP-Einstellungen in .env prüfen (siehe Ethereal-Sektion)
# 2. RQ Worker Container läuft? (siehe Background Jobs Sektion)
docker-compose up -d worker

# 3. Ethereal Account Credentials korrekt?
#    - Besuche https://ethereal.email/messages
#    - Prüfe ob Test-Emails dort ankommen
#    - Username & Password korrekt in .env kopieren (keine Zeilenumbrüche!)

# 4. Redis läuft?
docker-compose exec redis redis-cli ping  # Sollte "PONG" ausgeben

# 5. Logs prüfen
docker-compose logs web
docker-compose logs worker
```

#### ✅ Ethereal: Aktivierungs-Email testen

1. **Registriere einen neuen User via API**

   ```bash
   curl -X POST http://localhost:8000/api/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpass123"}'
   ```

2. **Aktivierungs-Email auf Ethereal prüfen**
   - Gehe zu https://ethereal.email/messages
   - Du solltest eine Email mit dem Betreff "Activate your account" sehen
   - Kopiere den Aktivierungs-Link und öffne ihn im Browser

3. **Email-Inhalte debuggen**
   - Klicke auf die Email um den HTML/Text anzuschauen
   - Prüfe ob der Aktivierungs-Link korrekt ist
   - Prüfe ob die Frontend-URL korrekt ist

#### ⚠️ Häufige Ethereal-Fehler

| Fehler                 | Ursache               | Lösung                                                         |
| ---------------------- | --------------------- | -------------------------------------------------------------- |
| "Invalid login"        | Falsche Credentials   | Ethereal Credentials neu kopieren (https://ethereal.email)     |
| "Connection refused"   | Port/Host falsch      | `EMAIL_HOST=smtp.ethereal.email`, `EMAIL_PORT=587`             |
| "TLS required"         | TLS nicht aktiviert   | `EMAIL_USE_TLS=True` in .env setzen                            |
| Emails kommen nicht an | RQ Worker nicht aktiv | `docker-compose up -d worker` um den Worker-Service zu starten |

---

## 📚 Nützliche Ressourcen

- [Django Dokumentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Doku](https://www.postgresql.org/docs/)
- [Redis Dokumentation](https://redis.io/documentation)
- [Docker Docs](https://docs.docker.com/)
- [JWT Authentication](https://jwt.io/)

---

**Zuletzt aktualisiert**: März 2026
