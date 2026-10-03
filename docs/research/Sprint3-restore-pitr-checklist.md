# Sprint 3: Postgres gestionado + PITR + restore ensayado

## Checklist

- [ ] Elegir proveedor (Neon/Supabase/Render) - confirmar PITR
- [ ] Crear instancia staging
- [ ] Aplicar Alembic (incluye 001_tsvector)
- [ ] Importar catálogo 4.259 productos
- [ ] Backup automático verificado
- [ ] **Restore ensayado**: restaurar a snapshot, crear dato de prueba, restaurar a antes, verificar integridad
- [ ] Configurar REDIS_URL si réplicas
- [ ] Variables: DATABASE_URL, REDIS_URL
- [ ] Pooling: pool_pre_ping=true, pool_recycle=3600
- [ ] Documentar procedimiento restore
- [ ] Pasar gate: restore exitoso documentado

## Comandos sugeridos (Neon)

```bash
# aplicar migraciones
alembic upgrade head

# verificar tsvector
psql $DATABASE_URL -c "SELECT count(*) FROM products WHERE name IS NOT NULL;"
```

## Criterio "Definido hecho"
Restaurar backup y recuperar un lote escrito después del último dump.
