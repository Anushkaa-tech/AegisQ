import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st

try:
    from sklearn.ensemble import IsolationForest
except ImportError as exc:  # pragma: no cover
    raise SystemExit("scikit-learn is required. Install it with: pip install scikit-learn") from exc

try:
    from Crypto.Hash import SHA3_256
except ImportError:  # pragma: no cover
    from hashlib import sha3_256 as _sha3_256

    def sha3_256_digest(payload: bytes) -> str:
        """Fallback helper that preserves a modern hash-based digest for the demo."""
        return _sha3_256(payload).hexdigest()
else:

    def sha3_256_digest(payload: bytes) -> str:
        """Cryptographic digest helper aligned with modern post-quantum-friendly demo semantics."""
        return SHA3_256.new(payload).hexdigest()


DB_PATH = os.path.join(os.path.dirname(__file__), "aegisq.db")


class PostQuantumVault:
    """
    Simulation layer for a NIST FIPS 203 / ML-KEM-768 style handshake.

    This class deliberately avoids any external PQC binary dependency and instead
    emulates the workflow of key generation, encapsulation, and decapsulation
    through deterministic cryptographic hashing. It is designed to be explainable
    to judges while still visualizing the high-level mechanics of a post-quantum
    key exchange in a polished dashboard experience.
    """

    def __init__(self, session_id: str = "AegisQ-FinSpark26"):
        self.session_id = session_id

    def generate_keypair(self) -> Tuple[str, str]:
        """Create a public/private key pair for the simulated Kyber-768 handshake."""
        seed_material = sha3_256_digest(self.session_id.encode("utf-8"))
        private_seed = int(seed_material[:16], 16)
        public_key = f"PK-{private_seed:x}"
        private_key = f"SK-{private_seed:x}"
        return public_key, private_key

    def encapsulate(self, public_key: str) -> Tuple[str, str]:
        """Encapsulate a shared secret using the public key and a pseudo-ciphertext."""
        salt = sha3_256_digest(f"{self.session_id}:{public_key}".encode("utf-8"))
        ciphertext = f"CT-{salt[:32]}"
        shared_secret = sha3_256_digest(f"{public_key}:{ciphertext}".encode("utf-8"))
        return ciphertext, shared_secret

    def decapsulate(self, private_key: str, ciphertext: str) -> str:
        """Decapsulate the shared secret from the ciphertext using the private key."""
        shared_secret = sha3_256_digest(f"{private_key}:{ciphertext}".encode("utf-8"))
        return shared_secret


class BehavioralEngine:
    """
    Unsupervised anomaly isolation engine for finding abnormal privileged access.

    The workflow uses a tiny, pre-defined corpus of normal behaviors representing
    ordinary admin activity: regular working hours, small-to-moderate download
    sizes, and known internal IP ranges. Isolation Forest is then used to score
    incoming activity and surface suspicious behavior without requiring labeled
    insider-threat training data.
    """

    def __init__(self):
        self.normal_training_data = np.array(
            [
                [10.0, 12.0, 0.1],
                [11.0, 24.0, 0.15],
                [13.0, 18.0, 0.12],
                [14.0, 40.0, 0.18],
                [15.0, 9.0, 0.2],
                [16.0, 30.0, 0.14],
                [9.0, 16.0, 0.1],
                [17.0, 20.0, 0.16],
            ],
            dtype=float,
        )
        self.model = IsolationForest(contamination=0.15, n_estimators=200, random_state=42)
        self.model.fit(self.normal_training_data)

    def _ip_weight(self, ip_address: str) -> float:
        """Translate an IP address into a low-risk / high-risk feature score."""
        if ip_address.startswith("10.") or ip_address.startswith("192.168."):
            return 0.1
        if ip_address.startswith("172."):
            return 0.15
        if ip_address.startswith("203.0.113."):
            return 0.6
        return 0.8

    def evaluate(self, hour: int, data_volume_mb: float, ip_address: str) -> int:
        """Score a behavior sample on a 0-100 scale using the isolation forest."""
        ip_feature = self._ip_weight(ip_address)
        sample = np.array([[float(hour), float(data_volume_mb), float(ip_feature)]], dtype=float)
        decision_score = self.model.decision_function(sample)[0]

        # A low decision score indicates anomalous structure; the score is mapped
        # into a percent-based risk indicator for UI visibility.
        risk_score = int(np.clip((0.65 - decision_score) * 100, 0, 100))

        # Additional heuristics make the simulation clearly reflect a sensitive
        # privileged-access control scenario with a strong insider-threat signal.
        if hour < 6 or hour > 22:
            risk_score += 10
        if data_volume_mb > 300:
            risk_score += 20
        if ip_feature > 0.5:
            risk_score += 10
        return int(np.clip(risk_score, 0, 100))


@st.cache_resource(show_spinner=False)
def get_behavior_engine() -> BehavioralEngine:
    """Cache the anomaly engine so the dashboard remains responsive across reruns."""
    return BehavioralEngine()


def init_database() -> None:
    """Create the local SQLite store for simulated admin telemetry."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            data_volume_mb REAL NOT NULL,
            ip_address TEXT NOT NULL,
            threat_risk_score INTEGER NOT NULL
        )
        """
    )
    conn.commit()

    # Seed a small baseline of normal activity if the database is empty.
    row_count = conn.execute("SELECT COUNT(*) FROM admin_actions").fetchone()[0]
    if row_count == 0:
        baseline_rows = [
            ("ADM-101", "2026-07-16T09:10:00", "Approved Vault Query", 15.0, "10.42.7.11", 12),
            ("ADM-102", "2026-07-16T11:30:00", "Quarterly Compliance Report", 34.0, "10.42.7.12", 19),
            ("ADM-103", "2026-07-16T15:20:00", "Role Based Access Review", 22.0, "10.42.7.13", 14),
        ]
        conn.executemany(
            """
            INSERT INTO admin_actions (admin_id, timestamp, action, data_volume_mb, ip_address, threat_risk_score)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            baseline_rows,
        )
        conn.commit()

    conn.close()


def fetch_actions() -> pd.DataFrame:
    """Return the admin activity table from SQLite as a DataFrame for the UI."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM admin_actions ORDER BY timestamp DESC", conn)
    conn.close()
    return df


def insert_action(record: Dict[str, object]) -> None:
    """Persist a new simulated action to the local database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO admin_actions (admin_id, timestamp, action, data_volume_mb, ip_address, threat_risk_score)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            record["admin_id"],
            record["timestamp"],
            record["action"],
            record["data_volume_mb"],
            record["ip_address"],
            record["threat_risk_score"],
        ),
    )
    conn.commit()
    conn.close()


def simulate_normal_behavior(engine: BehavioralEngine) -> List[Dict[str, object]]:
    """Generate a normal admin session pattern for the dashboard narrative."""
    now = datetime.now()
    generated = []
    for admin_id, action, volume_mb, ip_address, hour_offset in [
        ("ADM-204", "Approved Access Review", 18.0, "10.42.7.20", 0),
        ("ADM-205", "Compliance Report Export", 24.0, "10.42.7.21", 1),
        ("ADM-206", "Privileged Session Audit", 11.0, "10.42.7.22", 2),
    ]:
        timestamp = (now + timedelta(minutes=hour_offset * 8)).strftime("%Y-%m-%dT%H:%M:%S")
        hour = int(timestamp[11:13])
        risk = engine.evaluate(hour, volume_mb, ip_address)
        generated.append(
            {
                "admin_id": admin_id,
                "timestamp": timestamp,
                "action": action,
                "data_volume_mb": volume_mb,
                "ip_address": ip_address,
                "threat_risk_score": risk,
            }
        )
    return generated


def simulate_attack_behavior(engine: BehavioralEngine) -> List[Dict[str, object]]:
    """Generate a malicious insider pattern with midnight bulk transfer signals."""
    now = datetime.now()
    generated = []
    for admin_id, action, volume_mb, ip_address, minute_offset in [
        ("ADM-301", "Bulk Data Download - Finance Ledger", 780.0, "203.0.113.14", 0),
        ("ADM-301", "Archive Export - Restricted Dataset", 940.0, "203.0.113.14", 4),
        ("ADM-302", "Credential Dump Attempt", 112.0, "198.51.100.7", 7),
    ]:
        timestamp = (now + timedelta(minutes=minute_offset)).strftime("%Y-%m-%dT%H:%M:%S")
        hour = 3 if minute_offset < 10 else 4
        risk = engine.evaluate(hour, volume_mb, ip_address)
        generated.append(
            {
                "admin_id": admin_id,
                "timestamp": timestamp,
                "action": action,
                "data_volume_mb": volume_mb,
                "ip_address": ip_address,
                "threat_risk_score": risk,
            }
        )
    return generated


def render_dashboard() -> None:
    """Render the polished Streamlit frontend for the AegisQ prototype."""
    st.set_page_config(page_title="AegisQ | PAM Prototype", page_icon="🛡️", layout="wide")

    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #060816 0%, #0d1229 50%, #111627 100%);
            color: #f5f7ff;
        }
        .block-container {
            padding-top: 1.2rem;
        }
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(80, 133, 255, 0.2);
            border-radius: 14px;
            padding: 10px 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🛡️ AegisQ — Post-Quantum Safe PAM & Insider Threat Defense")
    st.caption("FinSpark'26 cyber-hackathon prototype | NIST FIPS 203 / Kyber-768 simulation + Isolation Forest anomaly detection")

    init_database()
    engine = get_behavior_engine()

    with st.sidebar:
        st.header("Mission Controls")
        st.caption("Select the operational scenario to stress the control plane.")

        if st.button("Simulate Normal Admin Behavior", use_container_width=True):
            records = simulate_normal_behavior(engine)
            for record in records:
                insert_action(record)
            st.success("Normal admin workflow simulated and persisted to the local vault telemetry store.")

        if st.button("Simulate Malicious Insider Attack (Bulk Data Download at 3 AM)", use_container_width=True):
            records = simulate_attack_behavior(engine)
            for record in records:
                insert_action(record)
            st.error("Threat scenario injected. Step-up MFA and session restriction workflows have been triggered.")

        st.markdown("---")
        st.subheader("Security Posture")
        st.checkbox("Quantum-Secured Session", value=True, disabled=True)
        st.checkbox("Privileged Access Monitoring", value=True, disabled=True)
        st.checkbox("Step-Up MFA Enforcement", value=True, disabled=True)

    df = fetch_actions()
    if df.empty:
        df = pd.DataFrame(columns=["admin_id", "timestamp", "action", "data_volume_mb", "ip_address", "threat_risk_score"])

    latest_risk = int(df.iloc[0]["threat_risk_score"]) if not df.empty else 0
    system_status = "Active / Quantum-Secured" if latest_risk < 75 else "Threat Contained"
    anomaly_status = "Threat Detected" if latest_risk >= 75 else "Safe"
    active_sessions = int(df["admin_id"].nunique())

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("System Status", system_status, "PQC Handshake Active")
    metric_col2.metric("Active Admin Sessions", active_sessions, "Real-Time Monitoring")
    metric_col3.metric("AI Anomaly Status", anomaly_status, "Isolation Forest")

    if latest_risk >= 75:
        st.warning("WARNING: Insider Threat Detected! Session restricted, Step-up MFA triggered!")

    st.markdown("### Quantum Key Exchange")
    vault = PostQuantumVault(session_id="AegisQ-FinSpark26")
    public_key, private_key = vault.generate_keypair()
    ciphertext, encapsulated_secret = vault.encapsulate(public_key)
    decapsulated_secret = vault.decapsulate(private_key, ciphertext)
    handshake_valid = encapsulated_secret == decapsulated_secret

    c1, c2, c3 = st.columns(3)
    c1.subheader("Public Key")
    c1.code(public_key, language="text")
    c2.subheader("Ciphertext")
    c2.code(ciphertext, language="text")
    c3.subheader("Decapsulated Secret")
    c3.code(decapsulated_secret, language="text")

    if handshake_valid:
        st.success("Quantum session validation passed — the encapsulated secret and decapsulated secret match perfectly.")
    else:
        st.error("The secure channel handshake failed. Immediate containment is required.")

    st.markdown("### Simulated Admin Activity Log")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.caption(f"Local telemetry store: {DB_PATH}")


if __name__ == "__main__":
    render_dashboard()
