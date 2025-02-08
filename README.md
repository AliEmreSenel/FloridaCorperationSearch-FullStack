# Florida Corporation Search

This project is a basic full stack app that lets the user search for corporations in Florida by name and shows them the details of the corporation in a easy to understand display.

For more details about the tech stack, check out the README's in both [backend](/python-backend) and [frontend](/react-frontend).

## Running the project

### Using Docker Compose (Reccomended)

```bash
docker-compose up --build
```

The project will be running its postgres db on the default port 5432, the backend on port 8000 and the frontend on port 3000.

This method is easily replicatable and quick to set up

### Manually

#### Setting up the postgresql database

Create a new user and database for the app to use.

By default the app uses the username `backend` with password `backend` and connects to the postgresql server running locally on the default port.

This behavior can be changed using the `DATABASE_URL` environment variable

#### Running Python Backend

1. Install Dependencies

```bash
pip install -r python-backend/requirements.txt
```

2. Run

```bash
python python-backend/main.py
```

or

```bash
cd python-backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Running ReactJS Backend

1. Install dependencies

```bash
npm install
```

2. Run the app in dev mode

```bash
npm run dev
```

or 2) Build the app

```bash
npm run build
```

3. Copy the build artifacts in the `out` folder into a preffered static hosting like nginx or apache
