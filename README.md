DuckDB ATTACH OR REPLACE in API
===============================

**NOTE:** unreleased feature, possibly will release with 1.3. Requires nightly builds for now. Uses TPCH, ensure you have ~256MB of disk space.

This demo shows how to make use of ATTACH OR REPLACE functionality in DuckDB to seamlessly switch to a newer upstream DB file. It uses a simple FastAPI-based service to wrap some basic DuckDB queries that generate and query TPCH data. First a v1 DuckDB file is queried, then a v2, but both use the same alias `t` which allows all queries to stay the same without needing to keep track of filenames or versions.

Example usage:

```sql
ATTACH OR REPLACE 'v1.duckdb' AS t
FROM t.lineitem;
-- Replace the alias
ATTACH OR REPLACE 'v2.duckdb' AS t
-- Alias is kept between attaches, so query can stay the same
FROM t.lineitem;
```

See: [main.py](main.py).

# Install

```
uv sync
uv run fastapi dev
```

# Test

```
# Once API is up, generate files and run queries. Notice the values change after attaching v2.
sh ./test.sh
```