from dagster import (
    op,
    job,
    ScheduleDefinition,
)

import subprocess



# =====================================================
# OP 1: Telegram Scraping
# =====================================================

@op
def scrape_telegram_data():

    print("Starting Telegram scraping...")

    try:

        subprocess.run(
            [
                "python",
                "src/scraper.py"
            ],
            check=True
        )

        print(
            "Telegram scraping completed successfully"
        )

        return "scraping_complete"


    except subprocess.CalledProcessError as e:

        raise Exception(
            f"Telegram scraping failed: {e}"
        )



# =====================================================
# OP 2: Load Raw Data To PostgreSQL
# =====================================================

@op
def load_raw_to_postgres(scraping_status):

    print(
        f"Previous step status: {scraping_status}"
    )

    print(
        "Loading raw data into PostgreSQL..."
    )


    try:

        subprocess.run(
            [
                "python",
                "src/load_to_postgres.py"
            ],
            check=True
        )


        print(
            "PostgreSQL loading completed successfully"
        )


        return "postgres_load_complete"


    except subprocess.CalledProcessError as e:

        raise Exception(
            f"PostgreSQL loading failed: {e}"
        )



# =====================================================
# OP 3: Run dbt Transformations
# =====================================================

@op
def run_dbt_transformations(load_status):

    print(
        f"Previous step status: {load_status}"
    )

    print(
        "Running dbt transformations..."
    )


    try:

        subprocess.run(
            [
                "dbt",
                "run",
                "--project-dir",
                "medical_warehouse"
            ],
            check=True
        )


        print(
            "dbt transformations completed successfully"
        )


        return "dbt_complete"


    except subprocess.CalledProcessError as e:

        raise Exception(
            f"dbt transformation failed: {e}"
        )



# =====================================================
# OP 4: YOLO Image Enrichment
# =====================================================

@op
def run_yolo_enrichment(dbt_status):

    print(
        f"Previous step status: {dbt_status}"
    )

    print(
        "Running YOLO image detection..."
    )


    try:

        subprocess.run(
            [
                "python",
                "src/yolo_detect.py"
            ],
            check=True
        )


        print(
            "YOLO enrichment completed successfully"
        )


        return "yolo_complete"


    except subprocess.CalledProcessError as e:

        raise Exception(
            f"YOLO enrichment failed: {e}"
        )



# =====================================================
# DAGSTER JOB GRAPH
# =====================================================

@job
def medical_pipeline():

    scrape_result = scrape_telegram_data()


    postgres_result = load_raw_to_postgres(
        scrape_result
    )


    dbt_result = run_dbt_transformations(
        postgres_result
    )


    run_yolo_enrichment(
        dbt_result
    )



# =====================================================
# DAILY SCHEDULE
# =====================================================

daily_schedule = ScheduleDefinition(

    job=medical_pipeline,

    cron_schedule="0 0 * * *",

    name="daily_medical_pipeline"

)