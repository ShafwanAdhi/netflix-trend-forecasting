import { useQuery } from "@tanstack/react-query";
import type { components } from "./schema";
export type ForecastResults = components["schemas"]["ForecastResults"];
export type ForecastSeries = components["schemas"]["ForecastSeries"];
export type ForecastResponse = components["schemas"]["ForecastResponse"];
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1${path}`, init);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const fields = data.field_errors
      ?.map(
        (e: { field: string; message: string }) => `${e.field}: ${e.message}`,
      )
      .join("; ");
    throw new ApiError(
      response.status,
      fields ||
        data.detail ||
        data.message ||
        "The service could not complete this request.",
    );
  }
  return response.json();
}
export const useForecastResults = () =>
  useQuery({
    queryKey: ["forecast-results"],
    queryFn: () => request<ForecastResults>("/tasks/5/results"),
  });
export const useForecast = (target: string, group: string, horizon: number) =>
  useQuery({
    queryKey: ["forecast", target, group, horizon],
    queryFn: () =>
      request<ForecastResponse>(
        `/tasks/5/forecast?${new URLSearchParams({ target, group, horizon: String(horizon) })}`,
      ),
  });
export const percent = (value: number) => `${(value * 100).toFixed(1)}%`;
export const modelName = (name: string) =>
  name.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
