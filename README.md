# Library Srvice API
The online management system for book borrowings.

## Content
1. [How to run](#how-to-run)
2. [Endpoints](#endpoints)
3. [Environmental variables](#environmental-variables)


## How to run

 - `docker-compose up --build`
 - Use test admin user created during migrations:
   - Email `test@admin.com`
   - Password `testpass123`
 - Create schedule for running sync in DB


## Endpoints

1. Book API endpoints
   - book/
   - book/{id}
2. User API endpoints
   - me/
   - token/
   - token/refresh
   - ./ 
3. Borrowing API endpoints
   - borrowings/
   - borrowings/{id}
   - borrowings/return
4. Swagger 
   - schema/swagger/

Also added notification via telegram.

## Environmental variables

The following environment variables should be set in the `.env` file:

- DJANGO_SECRET_KEY=YOUR_SECRET_KEY
- TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID=TELEGRAM_CHAT_ID
- CELERY_BROKER_URL=CELERY_BROKER_URL
- CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND
- POSTGRES_DB=POSTGRES_DB
- POSTGRES_USER=POSTGRES_USER
- POSTGRES_PASSWORD=POSTGRES_PASSWORD
- POSTGRES_HOST=POSTGRES_HOST
- POSTGRES_PORT=POSTGRES_PORT

**Note:** Before starting the project, make a copy of the `.env_sample` file and rename it to `.env`. Replace the sample values with your actual environment variable values.