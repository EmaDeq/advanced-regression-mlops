# Architecture (starter)

```text
Laptop:  PowerShell -> venv -> OpenML data -> sklearn training -> joblib bundle
                                   |                    |
                                   v                    v
                             offline pytest          FastAPI /predict
                                   |                    |
                                   v                    v
                             GitHub repository -> GitHub Actions CI
                                                          |
                                          manual, opt-in deploy workflow
                                                          |
                                           Render free DEV / PROD APIs
```

The two Render services are separate web services. This version trains a deterministic
model during each image build to eliminate external model-storage requirements.

**Next production-style upgrade:** GitHub Actions builds one image per source SHA,
pushes to a free public container registry (subject to provider limits), deploys that
immutable image digest to DEV, performs smoke tests, then promotes the *same digest*
to PROD after manual approval. Add rate limiting, authentication, structured logs,
input/data drift checks, dependency scanning, model registry and rollback procedures.
