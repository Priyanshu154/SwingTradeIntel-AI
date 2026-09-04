export const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL ||
  "https://qbu4ie2nmpgblejrjaydw7rlkq0csvgi.lambda-url.us-east-1.on.aws";

/** Shared secret sent as x-demo-key — must match backend DEMO_API_KEY / SSM */
export const DEMO_API_KEY =
  import.meta.env.VITE_DEMO_API_KEY || "change-me-before-deploy";

export const DEMO_UNLOCKED_KEY = "swingtrade_demo_unlocked";
export const DEMO_EMAIL_KEY = "swingtrade_demo_email";
