# Impact Email Verification Checklist

This sequence verifies that the custom email routing on the newly deployed domain is functioning perfectly before live customer communications are activated.

### Pre-Flight Verification
1. [ ] **Verify Registrar Forwarding Rule:** Log into the domain registrar (e.g., Porkbun, Namecheap) and confirm that an email forwarding rule is actively configured: `*@cardscout.pro` -> `[Your Personal Target Email]`.
2. [ ] **Verify DNS Propagation:** Ensure the MX records associated with the forwarding service are correctly mapped and propagated via a quick MX lookup (`dig MX cardscout.pro`).

### Live Domain Verification
3. [ ] **Send Test Inbound:** Send a plain-text test email from an external account (e.g., a secondary Gmail) addressed specifically to `support@cardscout.pro`.
4. [ ] **Confirm Delivery:** Verify that the test email successfully arrives in your personal target inbox without hitting the spam folder or encountering bounce-back delays.
5. [ ] **Send Reply (Optional/Recommended):** If you intend to reply to customers *from* the custom domain, ensure your inbox client's "Send As" configuration is verified via SMTP, and fire a test reply back to the external account.
