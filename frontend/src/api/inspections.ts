import apiClient from "./client";

export interface Inspection {
  id: string;
  bridge_id: string;
  name: string;
  status: string;
  notes: string | null;
  created_at: string;
}

export interface InspectionListResponse {
  count: number;
  items: Inspection[];
}

export interface InspectionSummary {
  inspection: Inspection;

  statistics: {
    component_count: number;
    media_count: number;
    finding_count: number;
  };

  findings: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    total: number;
  };
}

export interface InspectionIntelligence {
  inspection: Inspection;

  intelligence: {
    finding_count: number;
    media_count: number;
    highest_severity: string | null;
    risk_score: number;
    risk_level: string;
    priority: string;
    human_review_required: boolean;
  };

  severity_summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };

  components: Array<{
    component_id: string;
    component_name: string;
    component_type: string;
    finding_count: number;
    risk_score: number;
    condition: string;
  }>;

  recommendation: string;
}

export async function getInspections(): Promise<InspectionListResponse> {
  const response = await apiClient.get<InspectionListResponse>(
    "/api/v1/inspections/",
  );

  return response.data;
}

export async function getInspection(
  inspectionId: string,
): Promise<Inspection> {
  const response = await apiClient.get<Inspection>(
    `/api/v1/inspections/${inspectionId}`,
  );

  return response.data;
}

export async function getInspectionSummary(
  inspectionId: string,
): Promise<InspectionSummary> {
  const response = await apiClient.get<InspectionSummary>(
    `/api/v1/inspections/${inspectionId}/summary`,
  );

  return response.data;
}

export async function getInspectionIntelligence(
  inspectionId: string,
): Promise<InspectionIntelligence> {
  const response = await apiClient.get<InspectionIntelligence>(
    `/api/v1/inspections/${inspectionId}/intelligence`,
  );

  return response.data;
}