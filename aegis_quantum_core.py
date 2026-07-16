import datetime
import json
import math
import random
import time
from typing import Dict, List, Tuple


# ==========================================
# 1. QUANTUM-SAFE CRYPTOGRAPHY SIMULATION
# ==========================================
class QuantumSafeVault:
    """
    Simulates NIST FIPS 203 ML-KEM (Kyber) Key Encapsulation
    to protect administrative credentials against future quantum decryption.
    """

    def __init__(self):
        self.vault: Dict[str, dict] = {}

    def wrap_credential(self, admin_user: str, credential: str) -> Tuple[str, str]:
        """Simulates PQC encapsulation generating a ciphertext and a shared key."""
        # Simulated Post-Quantum Kyber-1024 shared secret and ciphertext
        simulated_shared_secret = f"pqc_shared_secret_ml_kem_{random.randint(10000, 99999)}"
        simulated_ciphertext = (
            f"ct_ml_kem_1024_{hash(admin_user + credential + str(time.time()))}"
        )

        self.vault[admin_user] = {
            "ciphertext": simulated_ciphertext,
            "algorithm": "ML-KEM-1024 (NIST FIPS 203)",
            "wrapped_at": datetime.datetime.now().isoformat(),
        }
        return simulated_ciphertext, simulated_shared_secret

    def get_vault_status(self) -> Dict:
        return self.vault


# ==========================================
# 2. TELEMETRY & TRANSACTION DATA SIMULATORS
# ==========================================
class TelemetryStreamSimulator:
    """Generates real-time SIEM, EDR, and network telemetry logs."""

    def __init__(self):
        self.compromised_ips = ["198.51.100.42", "203.0.113.11"]

    def generate_siem_event(self) -> dict:
        event_type = random.choice(
            ["LOGIN_SUCCESS", "BRUTE_FORCE_ATTEMPT", "PRIVILEGE_ESCALATION", "DATA_ARCHIVE"]
        )
        user = random.choice(["sys_admin_01", "operator_john", "anushka_pachade", "vendor_temp"])
        source_ip = (
            random.choice(self.compromised_ips)
            if random.random() < 0.15
            else f"10.120.{random.randint(1, 254)}.{random.randint(1, 254)}"
        )

        event = {
            "timestamp": datetime.datetime.now().isoformat(),
            "source": "SIEM/EDR",
            "event_type": event_type,
            "user": user,
            "source_ip": source_ip,
            "severity": "LOW",
            "metadata": {},
        }

        if event_type == "PRIVILEGE_ESCALATION":
            event["severity"] = "HIGH"
            event["metadata"] = {"target_group": "Domain Admins"}
        elif event_type == "DATA_ARCHIVE":
            # Potential Harvest-Now-Decrypt-Later exfiltration trigger
            event["severity"] = "MEDIUM"
            event["metadata"] = {
                "file_name": "customer_ledger_encrypted.zip",
                "size_mb": random.choice([5, 12, 4500]),  # 4.5 GB is massive!
            }

        return event


class TransactionStreamSimulator:
    """Generates real-time banking transactional data (ISO 20022 format structure)."""

    def generate_transaction(self) -> dict:
        amount = round(random.uniform(10.0, 150000.0), 2)
        account_id = f"ACT-{random.randint(100000, 999999)}"
        destination_country = random.choice(["IN", "US", "UK", "SG", "CH", "RU"])

        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "source": "CoreBanking/ISO20022",
            "account_id": account_id,
            "amount": amount,
            "destination_country": destination_country,
            "risk_flag": "SUSPICIOUS" if (amount > 100000.0) else "NORMAL",
        }


# ==========================================
# 3. AI CO-RELATION ENGINE (The Brain)
# ==========================================
class AegisCorrelationEngine:
    """
    Correlates security telemetry events with core banking transactions in real-time,
    calculating a unified threat score and catching Harvest-Now-Decrypt-Later (HNDL) attacks.
    """

    def __init__(self):
        self.active_security_alerts: List[dict] = []
        self.quantum_risk_threshold_mb = 1000  # Alert on encrypted files > 1GB

    def ingest_security_event(self, event: dict):
        # Keep window of recent alerts
        self.active_security_alerts.append(event)
        if len(self.active_security_alerts) > 100:
            self.active_security_alerts.pop(0)

    def evaluate_transaction(self, tx: dict) -> dict:
        """
        AI Feature Matrix logic: correlates transactions against live security alerts
        based on timing, user access, network indicators, and quantum telemetry.
        """
        base_score = 0.0
        correlation_signals = []
        is_quantum_threat = False

        # Rule 1: High Transaction Amount
        if tx["amount"] > 100000.0:
            base_score += 30.0
            correlation_signals.append("High-Value Transfer Flag")

        # Rule 2: Intersecting Cyber Telemetry Alerts (Real-time correlation)
        for alert in self.active_security_alerts:
            # Check if there was a privilege escalation or brute force in the last 60 seconds
            alert_time = datetime.datetime.fromisoformat(alert["timestamp"])
            tx_time = datetime.datetime.fromisoformat(tx["timestamp"])
            time_diff_sec = abs((tx_time - alert_time).total_seconds())

            if time_diff_sec <= 60:
                if alert["event_type"] == "PRIVILEGE_ESCALATION":
                    base_score += 50.0
                    correlation_signals.append(
                        f"CRITICAL CORRELATION: Privileged User '{alert['user']}' modified system logs 60s before transaction"
                    )

                if alert["event_type"] == "DATA_ARCHIVE" and alert["metadata"].get("size_mb", 0) > self.quantum_risk_threshold_mb:
                    base_score += 45.0
                    is_quantum_threat = True
                    correlation_signals.append(
                        f"QUANTUM RISK WARNING: Massive encrypted data exfiltration detected ({alert['metadata']['size_mb']}MB) - Suspected Harvest-Now-Decrypt-Later"
                    )

        # Normalize score
        final_threat_score = min(base_score, 100.0)

        # Determine Action
        action = "ALLOW"
        if final_threat_score >= 80.0:
            action = "BLOCK_AND_ISOLATE_ACCOUNT"
        elif final_threat_score >= 50.0:
            action = "STEP_UP_AUTHENTICATION (MFA Required)"

        return {
            "transaction": tx,
            "unified_threat_score": final_threat_score,
            "decision": action,
            "correlation_signals": correlation_signals,
            "is_quantum_threat": is_quantum_threat,
        }


# ==========================================
# 4. EXECUTION RUNTIME (Demo Showcase)
# ==========================================
def main():
    print("=" * 70)
    print("    AEGISQUANTUM CORE ENGINE - BANK OF MAHARASHTRA HACKATHON 2026")
    print("    Developer: Anushka Pachade | Unified Behavioral Analytics & PQC")
    print("=" * 70)

    # Initialize Components
    pqc_vault = QuantumSafeVault()
    telemetry_stream = TelemetryStreamSimulator()
    tx_stream = TransactionStreamSimulator()
    correlation_engine = AegisCorrelationEngine()

    # Step 1: Demonstrate PQC Credential Vault Protection
    print("\n[Step 1] Protecting administrative credentials with Quantum-Proof Cryptography...")
    cipher, secret = pqc_vault.wrap_credential("sys_admin_01", "SuperSecurePassword123!")
    print(f" -> Wrapped Key using: {pqc_vault.get_vault_status()['sys_admin_01']['algorithm']}")
    print(f" -> Generated Ciphertext: {cipher[:45]}...")
    print(f" -> Created Shared Secret: {secret}")
    print(" -> Vault status: SECURED")
    time.sleep(1.5)

    # Step 2: Start Telemetry Correlation Streaming
    print("\n[Step 2] Spawning simulated live data streams (Ingesting SIEM Logs & Transactions)...")
    print("-" * 70)

    # We will run 5 iterations simulating live system activities
    for i in range(1, 6):
        print(f"\n[CYCLE #{i}]")
        
        # Simulate background security event
        sec_event = telemetry_stream.generate_siem_event()
        correlation_engine.ingest_security_event(sec_event)
        print(f"📡 [SIEM ALERT] {sec_event['event_type']} | User: {sec_event['user']} | Source IP: {sec_event['source_ip']} (Severity: {sec_event['severity']})")

        # Give a small microsecond pause to separate timestamps
        time.sleep(0.5)

        # Generate live transaction
        tx_event = tx_stream.generate_transaction()
        print(f"💰 [TX ATTEMPT] Account: {tx_event['account_id']} | Amt: ${tx_event['amount']:,} | Destination: {tx_event['destination_country']}")

        # Correlate
        result = correlation_engine.evaluate_transaction(tx_event)

        # Output Results
        print(f"🛡️ [AEGIS SYSTEM DECISION]: {result['decision']} (Unified Threat Score: {result['unified_threat_score']}/100)")
        if result["correlation_signals"]:
            print("   ↳ Signals Detected:")
            for signal in result["correlation_signals"]:
                print(f"     ⚠️ {signal}")
        
        if result["is_quantum_threat"]:
            print("   🔴 ACTION TAKEN: Quantum incident response payload dispatched. Logging network traffic.")

        time.sleep(1.5)

    print("\n" + "=" * 70)
    print("Simulation Complete successfully. AegisQuantum is fully operational.")
    print("=" * 70)


if __name__ == "__main__":
    main()