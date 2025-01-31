# Frenglish
👉 https://frenglish.me/ or frenglish.me

**Frenglish**: A seamless blend of French and English, bridging language gaps through intuitive translation and learning

## Readability & Maintainability - Separation of Concerns
Separation of Concerns (SoC):
- **config/config.py**: Centralize and manage configuration settings and environment variables.
- **security/secretmanagerretriever.py**: Securely retrieve secrets from Google Cloud Secret Manager.
- **services/firestore_service.py**: Handle all Firestore database operations (CRUD and random entry retrieval).
- **services/translation_service.py**: Manage translation operations using the GeminiProcessor.
- **app.py**: Define Flask routes, handle HTTP requests, and integrate services and algorithms.
- **algorithms/data_processor.py**: Handle data processing logic, including interactions with the Gemini AI model.
- **algorithms/prompts.py**: Define prompts for different types of translations.
- **algorithms/firestore_adjuster.py**: Handle custom Firestore operations not covered by basic CRUD.
- **static/**: Store static files like CSS, JavaScript, and images.
- **templates/**: Store HTML templates for rendering web pages.
- **cloudbuild.yaml**: Define the build and deployment process using Google Cloud Build.
- **Dockerfile**: Define the Docker image for containerizing the application.
- **README.md**: Provide documentation on setting up, running, and deploying the application.
- **requirements.txt**: List the dependencies required by the application.
  
```
.github/
├── algorithms/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── data_processor.py
│   ├── firestore_adjuster.py
│   └── prompts.py
├── config/
│   ├── __init__.py
│   └── config.py
├── security/
│   ├── __init__.py
│   └── secretmanagerretriever.py
├── services/
│   ├── __init__.py
│   ├── firestore_service.py
│   └── translation_service.py
├── static/
├── templates/
│   └── index.html
├── app.py
├── cloudbuild.yaml
├── Dockerfile
├── README.md
└── requirements.txt
```

# Security

## 1 - Secure our secrets

## Readability & Maintainability - Separation of Concerns
```
.github/
├── algorithms/
│   ├── __init__.py
│   ├── data_processor.py
│   ├── firestore_service.py
│   ├── prompts.py
├── security/
│   ├── __init__.py
│   ├── secret_manager.py
├── static/
├── templates/
│   ├── index.html
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── services.py
├── config/
│   ├── __init__.py
│   ├── settings.py
├── tests/
│   ├── test_routes.py
│   ├── test_services.py
│   ├── test_data_processor.py
├── app.py
├── cloudbuild.yaml
├── Dockerfile
├── README.md
└── requirements.txt
```

# Security

## 1 - Secure our secrets

| Solution                                      | Description | Advantages | Drawbacks | Complexity | Security Level |
|-----------------------------------------------|-------------|------------|-----------|------------|----------------|
| **Google Cloud Secret Manager** | Store secrets securely in GCP's Secret Manager and retrieve them in your app using the Google Cloud SDK. | Secure, managed by Google, IAM-controlled access, audit logs available. | Requires API calls, may add latency. | Medium | ⭐⭐⭐⭐⭐ |
| **Service-to-Service IAM Authentication** | Use Google Cloud IAM for service authentication without handling raw secrets. | No secrets stored, managed automatically by GCP. | Limited to GCP services, requires IAM roles. | Medium | ⭐⭐⭐⭐⭐ |
| **Environment Variables** | Store secrets as environment variables in Cloud Run and access them via `os.environ`. | Simple, no extra API calls. | Secrets are visible in Cloud Run UI and logs if not handled properly. | Low | ⭐⭐⭐ |
| **GCP Config Connector / Terraform** | Use IaC (Infrastructure as Code) to manage and inject secrets securely into Cloud Run services. | Automated deployment, version-controlled. | Requires additional setup, may be complex for small projects. | High | ⭐⭐⭐⭐⭐ |
| **Database with Encryption** | Store secrets in a database with encryption-at-rest. | Secure, access can be logged. | Requires database setup and management. | Medium | ⭐⭐⭐⭐ |

# Routing

- External IP Address <mark>frenglish-ip</mark>
-

![image](https://github.com/user-attachments/assets/73703419-e228-4211-8d72-f15f44b469e4)

