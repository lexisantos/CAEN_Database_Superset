import time
import os
import glob
from sqlalchemy import create_engine, text

import pandas as pd

from process_bin_root import (
    bin_to_df,
    hist_bin,
    filter_hist,
    apply_calibration_en,
    get_info,
    duration_to_seconds
)

from comparison_cps import get_counts, see_relation


DAQ_PATH = "/home/lexi/Documentos/Datos CNEA/CAC_Protonterapia/20260608_test/DAQ/"
PATH_CALIB = "/home/lexi/Documentos/Datos CNEA/CAC_Protonterapia/20260608_test/coef_calib_energia.csv"
window_E = [13.5, 14.5]

engine = create_engine(
    "postgresql://superset:superset@localhost:5432/beam_monitor"
)

with engine.begin() as conn:

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS runs (
            run_name TEXT PRIMARY KEY,
            start_time TEXT,
            end_time TEXT,
            duration_s REAL,
            n_events INTEGER
        )
    """))


def already_processed(run_name):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT 1
                FROM runs
                WHERE run_name = :run_name
            """),
            {"run_name": run_name}
        )

        return result.fetchone() is not None


def save_run_metadata(run_name, start_time, end_time, duration_s, n_events):

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO runs
                (
                    run_name,
                    start_time,
                    end_time,
                    duration_s,
                    n_events
                )
                VALUES
                (
                    :run_name,
                    :start_time,
                    :end_time,
                    :duration_s,
                    :n_events
                )
            """),
            {
                "run_name": run_name,
                "start_time": start_time,
                "end_time": end_time,
                "duration_s": duration_s,
                "n_events": n_events
            }
        )

def process_run(run_folder):

    try:

        run_name = os.path.basename(run_folder)

        print(f"\nProcesando RUN: {run_name}")

        if already_processed(run_name):
            print("RUN ya procesado.")
            return None

        bins = glob.glob(
            os.path.join(run_folder, "RAW", "*.BIN")
        )

        if len(bins) == 0:
            print("No se encontró BIN.")
            return None

        bin_path = bins[0]

        print(f"BIN encontrado: {bin_path}")

        info = get_info(
            DAQ_PATH,
            run_name
        )

        print("INFO:", info)

        dfBIN = bin_to_df(bin_path)

        if dfBIN.empty:

            print("BIN vacío.")
            return None

        n_events = len(dfBIN)

        print(f"Eventos: {n_events}")

        df_hist = hist_bin(dfBIN)

        df_hist_filt = filter_hist(
            df_hist,
            counts_min=1
        )

        df_coef = pd.read_csv(PATH_CALIB)

        dfBIN = apply_calibration_en(
            dfBIN,
            df_coef
        )

        df_hist_filt = apply_calibration_en(
            df_hist_filt,
            df_coef
        )

        df_hist_filt["run_name"] = run_name

        df_hist_filt.to_sql(
            "histograms",
            engine,
            if_exists="append",
            index=False
        )

        print("Histogramas subidos.")

        cps_dict = get_counts(
            dfBIN,
            det_ch=[0, 1],
            window_s=1,
            window_E=window_E
        )

        for det, df_cps in cps_dict.items():
            df_cps["detector"] = det
            df_cps["run_name"] = run_name
            df_cps.to_sql(
                "cps",
                engine,
                if_exists="append",
                index=False
            )

        df_ratio = see_relation(cps_dict)

        df_ratio["run_name"] = run_name

        df_ratio.to_sql(
            "cps_ratio",
            engine,
            if_exists="append",
            index=False
        )

        print("Tabla de CPS y cocientes subidas.")

        save_run_metadata(
            run_name=run_name,
            start_time=info["time.start"],
            end_time=info["time.stop"],
            duration_s=duration_to_seconds(
                info["time.real"]
            ),
            n_events=n_events
        )

        print("Metadata del run guardada.")

        print("RUN completado.")

    except Exception as e:

        print(f"Error procesando {run_folder}")
        print(e)


print("Escaneando runs nuevos...")


while True:

    try:

        run_folders = [
            os.path.join(DAQ_PATH, d)
            for d in os.listdir(DAQ_PATH)
            if os.path.isdir(
                os.path.join(DAQ_PATH, d)
            )
        ]

        for run_folder in run_folders:

            process_run(run_folder)

        time.sleep(10)

    except KeyboardInterrupt:

        print("\nDetenido por usuario.")
        break

    except Exception as e:

        print("Error en loop principal:")
        print(e)

        time.sleep(10)