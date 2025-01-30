# Frenglish
Frenglish: A seamless blend of French and English, bridging language gaps through intuitive translation and learning

| Solution                                      | Description | Advantages | Drawbacks | Complexity | Security Level |
|-----------------------------------------------|-------------|------------|-----------|------------|----------------|
| **Google Cloud Secret Manager** | Store secrets securely in GCP's Secret Manager and retrieve them in your app using the Google Cloud SDK. | Secure, managed by Google, IAM-controlled access, audit logs available. | Requires API calls, may add latency. | Medium | ⭐⭐⭐⭐⭐ |
| **Service-to-Service IAM Authentication** | Use Google Cloud IAM for service authentication without handling raw secrets. | No secrets stored, managed automatically by GCP. | Limited to GCP services, requires IAM roles. | Medium | ⭐⭐⭐⭐⭐ |
| **Environment Variables** | Store secrets as environment variables in Cloud Run and access them via `os.environ`. | Simple, no extra API calls. | Secrets are visible in Cloud Run UI and logs if not handled properly. | Low | ⭐⭐⭐ |
| **GCP Config Connector / Terraform** | Use IaC (Infrastructure as Code) to manage and inject secrets securely into Cloud Run services. | Automated deployment, version-controlled. | Requires additional setup, may be complex for small projects. | High | ⭐⭐⭐⭐⭐ |
| **Database with Encryption** | Store secrets in a database with encryption-at-rest. | Secure, access can be logged. | Requires database setup and management. | Medium | ⭐⭐⭐⭐ |
