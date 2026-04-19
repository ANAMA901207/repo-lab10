# Skill: supabase-cli-helper

## Descripcion
Comandos CLI para que Cursor maneje la base de datos de Delphi sin MCP.
Mas barato, mas rapido y sin dependencias de red.

---

## Requisitos

Docker Desktop corriendo y Supabase CLI instalado:
```bash
npm install -g supabase
```

---

## Comandos de uso frecuente

### Levantar la base de datos local
```bash
cd repo-lab10
supabase start
```

Supabase levanta en:
- URL: `http://localhost:54321`
- DB: `postgresql://postgres:postgres@localhost:54322/postgres`
- Studio: `http://localhost:54323`

### Detener la base de datos
```bash
supabase stop
```

### Aplicar el schema de Delphi
```bash
supabase db reset
```

Esto ejecuta `delphi/schema.sql` y deja la base de datos limpia.

---

## Inspeccionar la base de datos

### Ver todas las tablas
```bash
supabase db dump --schema public
```

### Contar registros en una tabla
```bash
psql postgresql://postgres:postgres@localhost:54322/postgres \
  -c "SELECT COUNT(*) FROM sesiones;"
```

### Ver estructura de una tabla
```bash
psql postgresql://postgres:postgres@localhost:54322/postgres \
  -c "\d sesiones"
```

### Ver ultimas sesiones creadas
```bash
psql postgresql://postgres:postgres@localhost:54322/postgres \
  -c "SELECT id, usuario_id, estado, created_at FROM sesiones ORDER BY created_at DESC LIMIT 5;"
```

---

## Crear una migracion nueva

Cuando se necesita cambiar el schema:

```bash
supabase migration new [nombre_migracion]
```

Esto crea un archivo nuevo en `supabase/migrations/`.
Escribir el SQL del cambio en ese archivo y luego aplicarlo:

```bash
supabase db push
```

---

## Verificar que la conexion funciona

```bash
psql postgresql://postgres:postgres@localhost:54322/postgres \
  -c "SELECT NOW();"
```

Si devuelve la fecha y hora actual — la conexion esta bien.

---

## Cuando usar este skill

Usar CLI para:
- Desarrollo local — rapido y sin costo de tokens
- Inspeccionar tablas durante debugging
- Crear y aplicar migraciones

No usar para:
- Produccion — ahi usar el cliente de Supabase en Python (`db.py`)
- Operaciones con datos sensibles de usuarios reales