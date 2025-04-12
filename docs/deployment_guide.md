## 🚀 Deployment Guide for Plant Health Dashboard

The Plant Health Dashboard processes plant health environmental sensor data collected four times (morning, afternoon, evening, night) daily. This data is stored in **Google Cloud Storage (GCS)**, where it is ingested, cleaned, and transformed for weekly analysis (e.g., Week 46, 47, …), before being loaded into **BigQuery**. The **Airflow DAG** automates this batch processing, ensuring that the dashboard reflects up-to-date plant health insights.

---

### **Final Automated Workflow**
✅ **Airflow DAG** processes new sensor data (Week 46, 47, …), cleans it, and loads it into **BigQuery**.  
✅ **Dockerized App** fetches data from **BigQuery** and is deployed to **Cloud Run** for public access.  
✅ **Cloud Build** automates the build and redeployment process, ensuring seamless updates.

---

### 🔧 **Prerequisites**
Before deploying, ensure the following are set up:

- **Google Cloud SDK** installed and authenticated (`gcloud auth login`).
- **Google Cloud Project** (Example name: `plant-123456`) is active (`gcloud config set project plant-123456`).
- **Cloud Storage Bucket** (Example bucket: `gs://plant-bucket-123456`) created for raw and processed data.
- **BigQuery Dataset** exists to store processed data.
- **Cloud Composer (Airflow) environment** is set up for DAG execution.
- **Cloud Composer, Cloud Run, and Cloud Build APIs** are enabled:

  ```sh
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com composer.googleapis.com
  ```

---

