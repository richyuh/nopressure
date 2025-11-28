"""Streamlit entrypoint for the No Pressure prototype app."""

import datetime as dt

import streamlit as st

from ai import generate_guidance
from database import PostgresDB

st.set_page_config(
    page_title="No Pressure (Blood Pressure AI Assistant)",
    page_icon="🩺",
    layout="wide",
)
db = PostgresDB()


def main() -> None:
    """Render the Streamlit experience."""
    st.title("No Pressure (Blood Pressure AI Assistant)")
    st.caption(
        "A lightweight starting point for building an AI copilot that tracks blood "
        "pressure readings, surfaces trends, and drafts personalized guidance."
    )

    with st.sidebar:
        st.header("Session Controls")
        st.write(
            "Use the form below to log a new reading. "
            "When you're ready, press *Generate Guidance* to plug in your AI logic."
        )
        st.divider()
        st.subheader("Next Steps")
        st.markdown(
            "- Connect to your LLM or rules engine\n"
            "- Swap placeholder data with your own sources\n"
            "- Deploy to Streamlit Community Cloud or your infra"
        )

    col1, col2, col3 = st.columns(3)
    col1.metric("Systolic (mmHg)", "118", "-4 vs. last")
    col2.metric("Diastolic (mmHg)", "76", "-1 vs. last")
    col3.metric("Heart Rate (bpm)", "68", "+3 vs. last")

    st.subheader("Log a Reading")
    current_time = dt.datetime.now()
    with st.form("bp_entry"):
        systolic = st.number_input("Systolic", min_value=80, max_value=200, value=118)
        diastolic = st.number_input("Diastolic", min_value=40, max_value=140, value=76)
        heart_rate = st.number_input(
            "Heart Rate", min_value=40, max_value=200, value=68
        )
        symptoms = st.text_area("Symptoms / Notes", height=80, placeholder="Optional")
        timestamp = st.date_input("Reading Date", value=dt.date.today())
        reading_time = st.time_input("Reading Time", value=current_time.time())
        submitted = st.form_submit_button("Generate Guidance", use_container_width=True)

    if submitted:
        with st.spinner("Generating guidance..."):
            guidance = generate_guidance(systolic, diastolic, heart_rate, symptoms)

        try:
            timestamp_value = dt.datetime.combine(timestamp, reading_time)
            db.insert_reading(
                sys=systolic,
                dia=diastolic,
                hr=heart_rate,
                timestamp=timestamp_value,
            )
            st.success(
                f"Logged {systolic}/{diastolic} with heart rate {heart_rate} on "
                f"{timestamp:%b %d, %Y}.",
                icon="✅",
            )
        except Exception as exc:  # pragma: no cover - surface to UI
            st.error(f"Failed to save reading: {exc}")
        else:
            st.info(guidance, icon="💡")

    st.subheader("Recent Readings")
    try:
        recent_readings = db.get_recent_readings(limit=10)
    except Exception as exc:  # pragma: no cover - surface to UI
        st.error(f"Unable to load readings: {exc}")
        return

    formatted_readings = [
        {
            "Date": (
                row["timestamp"].strftime("%Y-%m-%d %H:%M")
                if hasattr(row["timestamp"], "strftime")
                else str(row["timestamp"])
            ),
            "Sys": row["sys"],
            "Dia": row["dia"],
            "HR": row["hr"],
        }
        for row in recent_readings
    ]

    if formatted_readings:
        st.dataframe(formatted_readings, use_container_width=True, hide_index=True)
    else:
        st.info("No readings recorded yet.")


if __name__ == "__main__":
    main()
