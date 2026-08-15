import apiClient from "./client";

export interface Finding {
  id: string;
  inspection_id: string;
  component_id: string | null;
  media_id: string | null;
  defect_type: string;
  description: string | null;
  severity: "low" | "medium" | "high" | "critical";
  confidence: number | null;
  created_at: string;
}

export async function getFindings(
  inspectionId: string,
): Promise<Finding[]> {
  const response = await apiClient.get<Finding[]>(
    "/api/v1/findings/",
    {
      params: {
        inspection_id: inspectionId,
      },
    },
  );

  return response.data;
}

export async function getFinding(
  findingId: string,
): Promise<Finding> {
  const response = await apiClient.get<Finding>(
    `/api/v1/findings/${findingId}`,
  );

  return response.data;
}