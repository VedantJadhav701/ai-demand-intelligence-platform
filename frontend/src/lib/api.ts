/**
 * API client helper for communicating with the AI Demand Intelligence API.
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "https://demand-intelligence-api.onrender.com";

export interface ForecastRequestPayload {
  horizon: number;
  store_id: string;
  product_id: string;
  date: string;
  features?: Record<string, any>;
}

export interface ForecastResponseData {
  prediction_id: string;
  forecast: number;
  horizon: number;
  store_id: string;
  product_id: string;
  date: string;
  model: string;
  model_registry_name: string;
  model_alias: string;
  feature_version: string;
  inference_time_ms: number;
  forecast_timestamp: string;
}

export interface FeatureDriver {
  feature: string;
  feature_value: any;
  shap_value: number;
}

export interface ExplainResponseData {
  prediction_id: string;
  prediction: number;
  base_value: number;
  horizon: number;
  store_id: string;
  product_id: string;
  date: string;
  model: string;
  model_registry_name: string;
  model_alias: string;
  top_positive: FeatureDriver[];
  top_negative: FeatureDriver[];
  shap_values: Record<string, number>;
}

export interface ModelMetric {
  horizon: number;
  model: string;
  registry_name: string;
  selection_source: string;
  cv_wape: number;
  test_wape: number;
}

export interface MetricsResponseData {
  status: string;
  total_horizons: number;
  metrics: ModelMetric[];
}

export interface FeatureDriftItem {
  feature_name: string;
  psi: number;
  ks_statistic?: number;
  p_value?: number;
  status: string;
  message: string;
}

export interface ResidualAnalysisData {
  sample_count: number;
  mae: number;
  rmse: number;
  wape: number;
  mean_residual: number;
  forecast_bias: number;
  tracking_signal: number;
  status: string;
}

export interface DriftReportResponseData {
  status: string;
  overall_status: string;
  summary_message: string;
  feature_drift: Record<string, FeatureDriftItem>;
  prediction_drift?: {
    mean_reference: number;
    mean_current: number;
    variance_reference: number;
    variance_current: number;
    psi: number;
    ks_statistic: number;
    p_value: number;
    status: string;
    message: string;
  };
  residual_analysis?: ResidualAnalysisData;
  timestamp: string;
}

export interface DatasetSummaryData {
  total_rows: number;
  total_stores: number;
  total_products: number;
  date_range: string;
  missing_pct: number;
  data_quality: string;
  stores: string[];
  products: string[];
  is_valid: boolean;
  warnings: string[];
}

export async function fetchHealth(): Promise<{ status: string; timestamp: string }> {
  const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function fetchReadiness(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/ready`, { cache: "no-store" });
  if (!res.ok) throw new Error("Readiness check failed");
  return res.json();
}

export async function fetchMetrics(): Promise<MetricsResponseData> {
  const res = await fetch(`${API_BASE_URL}/metrics`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch metrics");
  return res.json();
}

export async function postForecast(payload: ForecastRequestPayload): Promise<ForecastResponseData> {
  const res = await fetch(`${API_BASE_URL}/forecast`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Forecast generation failed");
  return res.json();
}

export async function postExplain(payload: ForecastRequestPayload & { top_n?: number }): Promise<ExplainResponseData> {
  const res = await fetch(`${API_BASE_URL}/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Explanation generation failed");
  return res.json();
}

export async function fetchDriftReport(): Promise<DriftReportResponseData> {
  const res = await fetch(`${API_BASE_URL}/drift`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch drift report");
  return res.json();
}

export async function uploadSalesDataFile(file: File): Promise<DatasetSummaryData> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE_URL}/data/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to upload dataset file");
  return res.json();
}

export async function fetchDatasetSummary(): Promise<DatasetSummaryData> {
  const res = await fetch(`${API_BASE_URL}/data/summary`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch dataset summary");
  return res.json();
}

export async function fetchDerivedFeatures(storeId: string, productId: string): Promise<Record<string, any>> {
  const res = await fetch(`${API_BASE_URL}/data/lookup-features?store_id=${encodeURIComponent(storeId)}&product_id=${encodeURIComponent(productId)}`, { cache: "no-store" });
  if (!res.ok) return {};
  const data = await res.json();
  return data.derived_features || {};
}
