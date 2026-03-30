Repo for [CM12005 group project coursework](https://moodle.bath.ac.uk/mod/assign/view.php?id=1552525).

Currently using [poetry](https://python-poetry.org/) for dependency management.
****
install deps:
```bash
poetry install
```

Without activating environment:
```bash
poetry run fastapi dev
```

# With Environment
## Windows
```bash
(poetry env info --path)\Scripts\activate 
fastapi dev
```

## Mac
```bash
source $(poetry env info --path)/bin/activate
fastapi dev
```

But we should probably just all agree on a version to use.
(currently on latest version (3.14.3)
Repo for [CM12005 group project coursework](https://moodle.bath.ac.uk/mod/assign/view.php?id=1552525).
