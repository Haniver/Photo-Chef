# Validation — Fase 0: Andamiaje del proyecto

## Criterios de aceptación

La fase está completa y lista para merge cuando **todos** los siguientes puntos son verdaderos.

---

### 1. Entorno Python

```bash
# Desde la raíz del repositorio:
uv run python --version
# Debe imprimir: Python 3.13.x
```

- `pyproject.toml` existe en la raíz con `requires-python = ">=3.13"`
- `.venv/` existe y no está trackeado por git (`git status` no lo muestra)

---

### 2. Variables de entorno

```bash
# No debe salir en git status ni en git log
git status --short | grep ".env$"
# Debe retornar vacío
```

- `.env` existe localmente con `DASHSCOPE_API_KEY` y `TAVILY_API_KEY` con valores reales
- `.env.example` existe en git con las mismas variables pero sin valores reales
- `cat .env.example` muestra exactamente las dos variables que necesita Photo-Chef

---

### 3. Estructura de carpetas

```bash
ls backend/
# Debe mostrar: __init__.py

ls frontend/
# Debe existir (puede estar vacío o con .gitkeep)
```

---

### 4. .gitignore funcional

```bash
# Ninguno de estos debe aparecer en `git status`:
# - .env
# - .venv/
# - __pycache__/
# - frontend/node_modules/   (aunque no exista aún, la regla debe estar)
# - frontend/dist/           (idem)

git check-ignore -v .env
# Debe retornar una línea indicando que .env está ignorado
```

---

### 5. Commit limpio en la rama correcta

```bash
git branch --show-current
# Debe imprimir: feat/fase-0-andamiaje

git log --oneline -1
# Debe mostrar el commit del andamiaje

git diff main --name-only
# Debe listar únicamente los archivos nuevos de esta fase:
# pyproject.toml, backend/__init__.py, .env.example,
# specs/2026-05-29-fase-0-andamiaje/ (los tres archivos de spec),
# y opcionalmente frontend/.gitkeep
```

---

### Checklist manual antes de hacer push

- [ ] `uv run python --version` → Python 3.13.x
- [ ] `pyproject.toml` tiene `requires-python = ">=3.13"`
- [ ] `.env` no aparece en `git status`
- [ ] `.env.example` está en git con solo las dos variables de Photo-Chef
- [ ] `backend/__init__.py` existe
- [ ] `frontend/` existe
- [ ] `git branch --show-current` → `feat/fase-0-andamiaje`
- [ ] La rama ha sido pusheada al remote de GitHub
