# **Peer Review Guide: Plant Health Dashboard Project**

### **1. Problem Description**
- Read the project README.md and confirm that the problem statement is clearly defined.
- Check if the solution aligns with the problem.

### **2. Cloud Usage**
- Verify Terraform scripts for infrastructure deployment.
- Confirm that cloud services such as GCS, BigQuery, Cloud Run, and Airflow are being used.

### **3. Data Ingestion**
- Check if Airflow DAGs automate data ingestion from GCS to BigQuery.
- Confirm data is stored in a structured format in the warehouse.

### **4. Data Warehouse**
- Verify that BigQuery tables are **partitioned and clustered** efficiently.
- Run sample queries to check if partitioning is utilized correctly.

### **5. Data Transformations**
- Check if transformations are implemented in BigQuery
- Confirm if any dbt/Spark transformations are used (not used).

### **6. Dashboard**
- Open the Cloud Run dashboard URL and verify:
  - It loads correctly.
  - Both tiles are functional and display meaningful data.
  - Dropdown filters (time period & plant id selection) work as expected.

  <p align="center">
    <img src="img\dashboard_1.png" alt="" width="800">
  </p>
  

  <p align="center">
    <img src="img\dashboard_2.png" alt="" width="800">
  </p>
  

### **7. Reproducibility**
- Follow the provided **setup instructions** in the documentation.
- Deploy the pipeline and confirm that it works end-to-end.

---

## **Final Review Checklist**
✅ Problem statement is clearly defined.  
✅ Cloud resources (GCP, Terraform) are used.  
✅ Data ingestion is fully automated with Airflow.  
✅ BigQuery tables are structured for efficient querying.  
✅ Dashboard contains **two functional tiles**.  
✅ Instructions are clear for running the project.  

> **Note for Reviewer:** If any of these points are missing or unclear, please provide feedback to improve the documentation or implementation.

