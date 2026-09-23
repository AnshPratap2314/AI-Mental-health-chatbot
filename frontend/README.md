# MindCare AI Frontend

Static browser frontend for the MindCare AI FastAPI backend.

## Run locally

From the repository root:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
cd frontend
python3 -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500
```

## API configuration

`index.html` defines:

```javascript
window.MINDCARE_API_URL = "https://<your-backend-domain>";
```

Change this value when deploying the frontend against another backend. The script also falls back to `127.0.0.1:8000` during local development.

## Frontend behavior

- Creates and stores one session ID in `localStorage`.
- Deletes the old server-side session when **New conversation** is selected.
- Automatically creates a replacement session if the server reports that the previous session expired.
- Performs a backend health check and shows online/offline status.
- Disables duplicate submissions while a request is in progress.
- Does not print the session ID to the browser console.
- Sends plain text to the API and renders bot responses with `textContent`, avoiding HTML injection.

## Production CORS

The backend must list the deployed frontend origin in `FRONTEND_URLS`.

Example:

```env
FRONTEND_URLS=https://your-frontend.example.com
```
