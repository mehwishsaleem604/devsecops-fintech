
# ──────────────────────────────────────────────────────────
# OPA Rego Policy — PCI DSS Compliance Gate
# Owner: Developer 3 (Compliance Lead)
# Path: opa-policies/pci_dss.rego (As per image_efbb98.png)
# ──────────────────────────────────────────────────────────

package pci_dss

import future.keywords.if
import future.keywords.in

# ── Top-level allow decision ─────────────────────────────
default allow := false

# Agar koi violation nahi hy, toh deployment allow hy
allow if {
    count(violations) == 0
}

# ── Violation Rules (PCI DSS Controls) ───────────────────

# Requirement 6.3: Software Development Security (SAST)
violations[msg] if {
    input.sast_passed == false
    msg := "REQ-6.3: SAST scan failed — insecure code detected"
}

# Requirement 2.2: Remove Hardcoded Credentials
violations[msg] if {
    input.secret_scan_passed == false
    msg := "REQ-2.2: Secret scan failed — credentials found in source"
}

# Requirement 6.3: Container Security
violations[msg] if {
    input.container_scan_passed == false
    msg := "REQ-6.3: Container scan failed — CRITICAL CVEs detected"
}

# Requirement 11.3: DAST / Penetration Testing
violations[msg] if {
    input.dast_passed == false
    msg := "REQ-11.3: DAST scan failed — dynamic vulnerabilities found"
}

# Requirement 4.1: Encryption in Transit
violations[msg] if {
    input.tls_enabled == false
    msg := "REQ-4.1: Encryption (TLS) is required for cardholder data"
}

# Requirement 3.3: Storage of Sensitive Auth Data (CVV)
violations[msg] if {
    input.cvv_stored == true
    msg := "REQ-3.3: STRICT PROHIBITION — CVV cannot be stored after auth"
}

# Requirement 3.4: PAN Masking/Encryption
violations[msg] if {
    input.pan_encrypted == false
    msg := "REQ-3.4: Primary Account Number (PAN) must be masked/encrypted"
}

# Requirement 8.2: Strong Authentication (MFA/JWT)
violations[msg] if {
    input.auth_required == false
    msg := "REQ-8.2: Authentication mechanism is missing or weak"
}

# ── Final Summary Output ────────────────────────────────
summary := {
    "allow": allow,
    "violations": violations,
    "violation_count": count(violations),
    "pci_dss_status": status
}

status := "COMPLIANT" if { allow }
else := "NON_COMPLIANT"
