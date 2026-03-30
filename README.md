Repo for CM12005 group project coursework.
Currently using [poetry](https://python-poetry.org/) for dependency management.

# Running backend
(In /backend)
****
install deps:
```bash
poetry install
```

## Without activating environment:
```bash
poetry run fastapi dev --host localhost
```

## With Environment
### Windows
```bash
(poetry env info --path)\Scripts\activate 
fastapi dev
```

### Mac
```bash
source $(poetry env info --path)/bin/activate
fastapi dev --host localhost
```

# Running Frontend
(In /frontend)
```bash
npm run dev
```