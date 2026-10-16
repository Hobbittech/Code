# NEURAL-HAND 3D WORKSTATION

A local Windows/VS Code futuristic 3D hand-tracking workstation using React, React Three Fiber, MediaPipe Tasks Vision, FastAPI, MongoDB/Motor, OpenAI, Tailwind CSS, Framer Motion, and Lucide React.

## Requirements

- Windows 10/11
- Python 3.10+ (3.11 recommended)
- Node.js 18+ and Yarn
- A Chromium-based browser with webcam support
- MongoDB Community Server (optional; the app still runs without it)
- An OpenAI API key for NEURAL AI

## 1. MongoDB

Install MongoDB Community Server for Windows if needed. The default local connection is:

`mongodb://localhost:27017`

The app uses database `neural_hand_db`. MongoDB persistence is optional: if MongoDB is unavailable, the API remains usable and scene/telemetry persistence is skipped.

Start MongoDB using the Windows service if you installed it as a service, or start `mongod` using your MongoDB installation.

## 2. Backend

Open PowerShell in this folder:

```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Open `backend/.env` and replace:

`OPENAI_API_KEY=YOUR_OPENAI_API_KEY`

with your own key. Never put this key in the frontend.

Start the API:

```powershell
uvicorn server:app --reload --port 8001
```

Backend: http://localhost:8001

API health: http://localhost:8001/api/

If PowerShell blocks activation, you can either allow scripts for your user with the normal Windows PowerShell execution-policy procedure, or run the venv Python directly:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn server:app --reload --port 8001
```

## 3. Frontend

Open a second PowerShell window:

```powershell
cd frontend
copy .env.example .env
yarn install
yarn start
```

Then open:

http://localhost:3000

The frontend reads `REACT_APP_BACKEND_URL` from `frontend/.env`. Do not put the OpenAI key there.

## Webcam / MediaPipe

Allow camera access when the browser asks. The MediaPipe WASM runtime and hand-landmarker model are loaded from public CDNs. An internet connection is therefore needed the first time the tracker loads.

If camera permission is denied, the rest of the workstation remains usable.

## Gesture mapping

- open_palm -> reset
- fist -> select/hold state
- pinch -> interact
- point -> rotate
- thumbs_up -> confirm
- peace -> mode
- three_finger -> scale up

The gesture classifier is intentionally simple and is located at `frontend/src/lib/gestures.js` so it can be extended.

## AI scene commands

NEURAL AI supports:

- set_color
- set_shape
- set_scale
- rotate
- reset
- spawn_particles

Supported shapes:

- cube
- sphere
- torus
- cone
- pyramid

Example prompts:

- Make the object cyan.
- Change it to a sphere.
- Make it twice as large.
- Rotate it.
- Reset the scene.
- Spawn particles.

The backend validates action directives before returning them to the browser.

## Browser panel

The browser panel uses an iframe. Many real websites send security headers that prevent iframe embedding. This is normal browser behavior. Use "Open externally" when a site refuses to embed.

## Troubleshooting

### Backend says OpenAI is not configured
Make sure `backend/.env` exists and contains a valid `OPENAI_API_KEY`, then restart uvicorn.

### MongoDB is unavailable
That is allowed. Start MongoDB if you want persistence. The server logs a warning and continues.

### Camera fails
Check Windows camera privacy settings and browser permissions. Make sure no other application is exclusively using the camera.

### MediaPipe fails to load
The tracker downloads its WASM/model assets from CDNs. Check internet access and browser console errors.

### Frontend cannot reach backend
Confirm uvicorn is running on port 8001 and `frontend/.env` says:

`REACT_APP_BACKEND_URL=http://localhost:8001`

Restart `yarn start` after changing `.env`.

## Security

No API key is included in this project. `.env` files are ignored by Git. Keep your OpenAI key only in `backend/.env`.

This project intentionally contains no Emergent packages, no Anthropic SDK, and no `ANTHROPIC_API_KEY`.
