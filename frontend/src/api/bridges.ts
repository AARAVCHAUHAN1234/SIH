import apiClient from "./client";

export interface Bridge {
  id: string;
  project_id: string;
  name: string;
  bridge_type: string | null;
  location: string | null;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
}

export interface BridgeListResponse {
  items: Bridge[];
}

export interface ComponentCondition {
  component_id: string;
  component_name: string;
  component_type: string;
  finding_count: number;
  risk_score: number;
  condition: string;
  priority: string;
}

export interface ComponentConditionResponse {
  bridge_id: string;
  component_count: number;
  components: ComponentCondition[];
}

export interface BridgeRisk {
  bridge_id: string;
  bridge_name: string;
  inspection_count: number;
  finding_count: number;
  risk_score: number;
  risk_level: string;
  priority: string;
  human_review_required: boolean;
  risk_breakdown: {
    base_risk: number;
    progression_bonus: number;
    recurrence_bonus: number;
    critical_findings: number;
    high_findings: number;
  };
}

export async function getBridges(): Promise<BridgeListResponse> {
  const response = await apiClient.get<BridgeListResponse>("/api/v1/bridges/");
  return response.data;
}

export async function getBridge(bridgeId: string): Promise<Bridge> {
  const response = await apiClient.get<Bridge>(
    `/api/v1/bridges/${bridgeId}`,
  );

  return response.data;
}

export async function getComponentConditions(
  bridgeId: string,
): Promise<ComponentConditionResponse> {
  const response = await apiClient.get<ComponentConditionResponse>(
    `/api/v1/bridges/${bridgeId}/components/condition`,
  );

  return response.data;
}

export async function getBridgeRisk(
  bridgeId: string,
): Promise<BridgeRisk> {
  const response = await apiClient.get<BridgeRisk>(
    `/api/v1/bridges/${bridgeId}/risk`,
  );

  return response.data;
}