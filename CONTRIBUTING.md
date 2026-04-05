# Contributing Guidelines

## Quick start for contributors

1. **Clone the repository.**

   ```bash
   git clone https://github.com/mbdeaton/semitone-api.git
   cd semitone-api
   ```

2. **Install dependencies.**
   We use Poetry for dependency management.

   ```bash
   poetry install
   ```

3. **Activate the development environment.**

   ```bash
   eval $(poetry env activate)             # Linux
   poetry env activate | Invoke-Expression # Windows
   ```

4. **Run the linters and type checker.**

   ```bash
   ./check-style.sh     # Linux
   poetry run black ... # Windows: run check-style.sh black, pylint, mypy calls
   ```

5. **Run the server locally.**

   ```bash
   poetry run uvicorn semitone_api.main:app --reload                   # run from local env
   docker run --rm -p 8000:8000 -v "$(pwd):/home/appuser" semitone-api # run from deploy env
   ```

6. **Make your changes and commit.**

   ```bash
   git checkout -b my-feature
   git commit -am "Describe your change"
   git push origin my-feature
   ```

7. **Submit a pull request.**


## Style

We conform to PEP-8 and where that is silent we follow the
[Google style guide](https://google.github.io/styleguide/pyguide.html).
We also use type hints.

Style is enforced with `black`, type-hinting with `mypy`, linting with `pylint`
which is configured to the Google pylintrc (with a few minor adjustments).

To check conformance locally, from within a poetry shell, invoke

```bash
./check-style.sh
```


## Testing

We use the unittest framework. To run tests invoke

```bash
poetry run python -m unittest -v
```


## Continuous Integration

We use GitHub Actions to automatically run style checks and linting on every
push and pull request to `main`.


## Docker

To build and run the app in a Docker container:

1. **Build the image.**

   ```bash
   docker build -t semitone-api .
   ```

2. **Run the container.**

   ```bash
   docker run --rm -p 8000:8000 -v "$(pwd):/home/appuser" semitone-api
   ```

3. **Verify.** Visit `http://localhost:8000/docs` to confirm the Swagger UI
   loads, or hit the health endpoint:

   ```bash
   curl http://localhost:8000/health
   ```

The image runs as a non-root user on port 8000. Only production dependencies
are installed (no dev tools).


## Fly.io
Deploy is automatic with a GitHub action, however some common fly.io gestures:

```bash
fly deploy # push up app to fly.io and deploy
fly status # check status of machines
fly logs   # view logged interactions with the app
fly machine list --app semitone-api # view deployed machines
```


## Dependency Management

We use Poetry. Common gestures:

```bash
poetry install      # create the virtual environment and install dependencies
poetry env activate # print the command to activate the virtual environment
poetry run COMMAND  # run a command within this environment
poetry add X             # add runtime dependency X
poetry add --group dev X # add development dependency X

poetry lock         # regenerate lock file without upgrading versions
poetry add X@^X.Y.Z # update specific dependency version
poetry update X     # rebuild poetry.lock from only updated versio to X
```
