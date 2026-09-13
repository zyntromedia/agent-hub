import { createClient } from '@base44/sdk';
import { appParams } from '@/lib/app-params';

// Destructure with clear naming
const {
  appId,
  token,
  functionsVersion,
  appBaseUrl
} = appParams;

// 🛡️ Validate required fields — fail fast, clear errors
if (!appId) {
  throw new Error('[Base44] Missing required parameter: appId');
}
if (!token) {
  throw new Error('[Base44] Missing required parameter: token');
}

// Create client — safe, consistent, auto-auth
export const base44 = createClient({
  appId,
  token,
  functionsVersion,
  appBaseUrl,
  // ✅ Removed empty `serverUrl: ''` — let SDK use its default
  requiresAuth: !!token, // ✅ Auto-enable auth when token is present
});
