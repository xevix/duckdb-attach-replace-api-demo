from fastapi import FastAPI

import duckdb

TPCH_BASE_FILENAME = "tpch_fastapi"
DB_ALIAS = "t"

app = FastAPI()
conn = duckdb.connect()


def attach_tpch(version):
    # Use the same DB alias when replacing the DB, allowing to keep DB queries the same
    conn.execute(
        f"ATTACH OR REPLACE '{TPCH_BASE_FILENAME}_{version}.duckdb' AS {DB_ALIAS}"
    )


def attach_and_generate_tpch(version):
    attach_tpch(version)
    if not conn.sql(
        f"FROM information_schema.tables WHERE table_catalog = '{DB_ALIAS}'"
    ).fetchone():
        sf = int(version[1]) - 1
        conn.execute(f"CALL dbgen(sf = {sf}, catalog = '{DB_ALIAS}')")


def create_tpch():
    attach_and_generate_tpch("v1")
    attach_and_generate_tpch("v2")


@app.get("/")
def read_root():
    return {}


@app.get("/tpch/create")
def create_tpch_endpoint():
    create_tpch()


@app.get("/tpch/attach/{version}")
def attach_new_version(version: str):
    attach_tpch(version)


@app.get("/tpch/attached")
def get_attached():
    attached_dbs = conn.sql(
        "SELECT DISTINCT catalog_name FROM information_schema.schemata ORDER BY ALL"
    ).fetchall()
    return {"dbs": [db[0] for db in attached_dbs]}


@app.get("/items/count")
def count_items():
    cnt = conn.sql("SELECT COUNT(*) FROM t.lineitem").fetchone()[0]
    return {"cnt": cnt}


@app.get("/suppliers/top")
def top_suppliers():
    supps = conn.sql(f"""
             SELECT s.s_name, COUNT(*) AS cnt 
             FROM {DB_ALIAS}.lineitem l, {DB_ALIAS}.supplier s 
             WHERE l.l_suppkey = s.s_suppkey 
             GROUP BY ALL
             ORDER BY cnt DESC LIMIT 3
             """).fetchall()

    return {"suppliers": supps}


@app.get("/supplier/{supp_name}/items/price/total")
def read_item(supp_name: str):
    item = conn.sql(
        f"""
        SELECT s.s_name, SUM(l_extendedprice) 
        FROM {DB_ALIAS}.lineitem l, {DB_ALIAS}.supplier s 
        WHERE l.l_suppkey = s.s_suppkey AND s.s_name = ?
        GROUP BY ALL""",
        params=[f"Supplier#00000000{supp_name}"],
    ).fetchone()
    if not item:
        return {}
    return {"name": item[0], "totalprice": item[1]}
