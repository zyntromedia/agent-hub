// src/lib/api.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";
import { loadEnv } from "./env";

// ─── Constants ───
const DEFAULT_TIMEOUT = 20_000;
const HEADER_SECRET = "X-WebApp-Secret" as const;

// ─── Types ───
interface EnvConfig {
  webAppUrl: string;
  webAppSecret?: string;
}

type ApiResponse<T = unknown> = Promise<T>;

// ─── API Response Types ───
export interface StatsResponse {
  inboxCount: number;
  processedToday: number;
  dlqCount: number;
  lastRunAt: string; // ISO string
}

export interface OkResponse {
  ok: boolean;
}

// ─── Create Instance ───
const api: AxiosInstance = axios.create({
  timeout: DEFAULT_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
  },
});

// ─── Request Interceptor ───
api.interceptors.request.use(
  (config): AxiosRequestConfig => {
    const { webAppUrl, webAppSecret } = loadEnv() as EnvConfig;

    if (!webAppUrl?.trim()) {
      throw new Error("❌ Web App URL is not configured. Check your env variables.");
    }

    // Build full URL
    if (config.url && !config.url.startsWith("http")) {
      const separator = webAppUrl.includes("?") ? "&" : "?";
      const actionPath = config.url.replace(/^\?/, "");
      config.url = `${webAppUrl}${separator}${actionPath}`;
    }

    // Inject secret header
    if (webAppSecret?.trim()) {
      config.headers = {
        ...config.headers,
        [HEADER_SECRET]: webAppSecret,
      };
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response Interceptor — Optional but highly recommended ───
api.interceptors.response.use(
  (response): AxiosResponse => response,
  (error) => {
    const message = error.response?.data?.message ?? error.message ?? "Unknown error";
    const status = error.response?.status;
    console.error(`[API Error ${status}]: ${message}`);
    return Promise.reject(error);
  }
);

// ─── API Client ───
export const Api = {
  /** Get dashboard statistics */
  async getStats(): ApiResponse<StatsResponse> {
    const { data } = await api.get<StatsResponse>("action=stats");
    return data;
  },

  /** Reprocess a specific DLQ entry */
  async reprocessDLQ(id: string): ApiResponse<OkResponse> {
    if (!id?.trim()) throw new Error("❌ DLQ entry ID is required");
    const { data } = await api.post<OkResponse>("action=dlq.reprocess", { id });
    return data;
  },
};
