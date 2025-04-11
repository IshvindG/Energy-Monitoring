from co2_extract_clean import main as extract_main
from co2_load import insert_carbon_intensities, connect_to_db, load_csv


def lambda_handler(event=None, context=None):
    extract_main()

    file_path = "/tmp/clean_live_co2.csv"
    df = load_csv(file_path)
    conn, cur = connect_to_db()
    insert_carbon_intensities(df, conn, cur)
    cur.close()
    conn.close()

    return {"status": "Success", "rows": len(df)}
