Repo for (CM12005 group project coursework)[https://moodle.bath.ac.uk/mod/assign/view.php?id=1552525].

Currently using (poetry)[https://python-poetry.org/] for dependency management.
****
install deps:
```bash
poetry install
```

run:
```bash
fastapi dev --host localhost
```

If you are using a different version of python then:
```bash
poetry run fastapi dev --host localhost
```
> Remember --host