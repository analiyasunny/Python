import io
import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Pandemic Residence Data Analyzer")
st.title("Pandemic Residence Data Analyzer")
st.caption(f"Current Date and Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.write("Upload an Excel file (.xlsx) with three columns for Affected, Isolated, and Fine.")

uploaded = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])

def process_dataframe(df: pd.DataFrame):
    # Ensure at least 3 columns
    if df.shape[1] < 3:
        st.error("Your Excel needs at least three columns (Affected, Isolated, Fine).")
        return None

    # Extract the first three columns (adjust if you want to match by column name)
    affected = df.iloc[:, 0].dropna().astype(str).tolist()
    isolated = df.iloc[:, 1].dropna().astype(str).tolist()
    fine = df.iloc[:, 2].dropna().astype(str).tolist()

    summary = {
        "Number of residents affected": len(affected),
        "Number of residents isolated": len(isolated),
        "Number of residents who are fine": len(fine)
    }

    # Create text report
    report_lines = []
    report_lines.append("Residents who are Affected")
    report_lines.extend(affected)
    report_lines.append("\nResidents who are Isolated")
    report_lines.extend(isolated)
    report_lines.append("\nResidents who are Fine")
    report_lines.extend(fine)
    report_bytes = "\n".join(report_lines).encode("utf-8")

    tidy = pd.concat([
        pd.DataFrame({"name": affected, "status": "affected"}),
        pd.DataFrame({"name": isolated, "status": "isolated"}),
        pd.DataFrame({"name": fine, "status": "fine"}),
    ], ignore_index=True)

    return summary, report_bytes, tidy

if uploaded:
    try:
        df = pd.read_excel(uploaded)
        result = process_dataframe(df)
        if result:
            summary, report_bytes, tidy = result

            st.subheader("Summary")
            for k, v in summary.items():
                st.write(f"- **{k}**: {v}")

            # Download text report
            st.download_button(
                label="Download text report",
                data=report_bytes,
                file_name="report.txt",
                mime="text/plain"
            )

            # Download processed Excel
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Original")
                tidy.to_excel(writer, index=False, sheet_name="Processed_Tidy")
            st.download_button(
                label="Download processed Excel",
                data=out.getvalue(),
                file_name="processed.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"Failed to read/process Excel: {e}")
