provider "google" {
  project = var.project_id
  region  = var.region
}

# Data source to get project number
data "google_project" "current" {
  project_id = var.project_id
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "composer.googleapis.com",
    "run.googleapis.com"
  ])
  service = each.value
  disable_on_destroy = false
}

# Create Cloud Storage Bucket
resource "google_storage_bucket" "plant_data_dashboard" {
  name     = "${var.project_id}-plant-health-data"
  location = var.region
  force_destroy = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30
    }
  }
}

# Create "raw/" folder in GCS bucket
resource "google_storage_bucket_object" "raw_folder" {
  name    = "raw_data/.placeholder"
  content = ""
  bucket  = google_storage_bucket.plant_data_dashboard.name
}

# Create "processed/" folder in GCS bucket
resource "google_storage_bucket_object" "processed_folder" {
  name    = "processed_data/.placeholder"
  content = ""
  bucket  = google_storage_bucket.plant_data_dashboard.name
}

# Create BigQuery Dataset
resource "google_bigquery_dataset" "plant_health" {
  dataset_id = "plant_health_dataset"
  location   = var.region
}

# Create BigQuery Table
resource "google_bigquery_table" "plant_health_table" {
  dataset_id = google_bigquery_dataset.plant_health.dataset_id
  table_id   = "plant_health"
  schema     = file("${path.module}/schemas/plant_health_schema.json")
  time_partitioning {
    type = "DAY"
  }
}

# IAM Permissions for Cloud Composer service account
resource "google_project_iam_member" "cloud_composer_permissions" {
  for_each = toset([
    "roles/storage.admin",
    "roles/bigquery.dataEditor",
    "roles/run.admin",
    "roles/artifactregistry.writer"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${data.google_project.current.number}-compute@developer.gserviceaccount.com"
}

# IAM Permissions for Cloud Build service account
resource "google_project_iam_member" "cloud_build_permissions" {
  for_each = toset([
    "roles/storage.admin",
    "roles/bigquery.dataEditor",
    "roles/run.admin",
    "roles/artifactregistry.writer"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${data.google_project.current.number}@cloudbuild.gserviceaccount.com"
}
