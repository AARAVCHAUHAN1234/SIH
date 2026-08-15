import apiClient from "./client";

export interface Finding {
  id: string;
  inspection_id: string;
  component_id: string | null;
  defect_type: string;
  description: string | null;
  severity: string;
  confidence: number | null;
  created_at: string;
}

export interface FindingListResponse {
  count: number;
  items: Finding[];
}

export async function getInspectionFindings(
  inspectionId: string,
): Promise<Finding[]> {
  const response = await apiClient.get<FindingListResponse>(
    "/api/v1/findings/",
    {
      params: {
        inspection_id: inspectionId,
      },
    },
  );
return response.data.items ?? [];
}