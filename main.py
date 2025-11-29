"""Streamlit entrypoint for the No Pressure prototype app."""

import datetime as dt

import streamlit as st

from agent.bp_agent import BPAgent
from database import PostgresDB

st.set_page_config(
    page_title="No Pressure (Blood Pressure AI Assistant)",
    page_icon="🩺",
    layout="wide",
)
db = PostgresDB()
bp_agent = BPAgent()


def fetch_recent_data(
    database: PostgresDB, limit: int = 10
) -> tuple[list[dict], Exception | None]:
    """Return recent readings and a potential error."""
    try:
        return database.get_recent_readings(limit=limit), None
    except Exception as exc:  # pragma: no cover - surface to UI
        return [], exc


def split_latest_previous(
    readings: list[dict],
) -> tuple[dict | None, dict | None]:
    """Return the latest and previous readings from a list."""
    latest = readings[0] if readings else None
    previous = readings[1] if len(readings) > 1 else None
    return latest, previous


def format_value(reading: dict | None, key: str) -> str:
    """Format the metric value for display."""
    if not reading:
        return "--"
    return str(reading[key])


def format_delta(latest: dict | None, previous: dict | None, key: str) -> str:
    """Format the delta string between two readings."""
    if not latest or not previous:
        return "N/A"
    delta = latest[key] - previous[key]
    prefix = "+" if delta > 0 else ""
    return f"{prefix}{delta} vs last"


def render_metrics(placeholder, latest: dict | None, previous: dict | None) -> None:
    """Render the trio of metrics with current readings."""
    with placeholder.container():
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Systolic (mmHg)",
            format_value(latest, "sys"),
            format_delta(latest, previous, "sys"),
            delta_color="inverse",
        )
        col2.metric(
            "Diastolic (mmHg)",
            format_value(latest, "dia"),
            format_delta(latest, previous, "dia"),
            delta_color="inverse",
        )
        col3.metric(
            "Heart Rate (bpm)",
            format_value(latest, "hr"),
            format_delta(latest, previous, "hr"),
            delta_color="inverse",
        )


def main() -> None:
    """Render the Streamlit experience."""
    st.title("No Pressure (Blood Pressure AI Assistant)")
    st.caption(
        "A lightweight starting point for building an AI copilot that tracks blood "
        "pressure readings, surfaces trends, and drafts personalized guidance."
    )

    metrics_placeholder = st.empty()
    recent_readings, load_error = fetch_recent_data(db)
    latest_reading, previous_reading = split_latest_previous(recent_readings)
    render_metrics(metrics_placeholder, latest_reading, previous_reading)

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
            guidance = bp_agent.generate_guidance(
                systolic, diastolic, heart_rate, symptoms
            )

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
            recent_readings, load_error = fetch_recent_data(db)
            latest_reading, previous_reading = split_latest_previous(recent_readings)
            render_metrics(metrics_placeholder, latest_reading, previous_reading)
        except Exception as exc:  # pragma: no cover - surface to UI
            st.error(f"Failed to save reading: {exc}")
        else:
            st.info(guidance, icon="💡")

    st.subheader("Recent Readings")
    if load_error:
        st.error(f"Unable to load readings: {load_error}")
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
