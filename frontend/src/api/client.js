import { BACKEND_URL, DEMO_API_KEY } from "./config";

export async function apiFetch(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    "x-demo-key": DEMO_API_KEY,
    ...(options.headers || {}),
  };
  return fetch(`${BACKEND_URL}${path}`, { ...options, headers });
}

/** Best-effort ticker extraction for the request body. */
export function guessTicker(query) {
  const match = query.toUpperCase().match(
    /\b(RELIANCE|TCS|INFY|HDFCBANK|ICICIBANK|SBIN|BHARTIARTL|ITC|LT|AXISBANK|KOTAKBANK|HINDUNILVR|BAJFINANCE|MARUTI|ASIANPAINT|HCLTECH|SUNPHARMA|TITAN|WIPRO|ULTRACEMCO|NTPC|POWERGRID|TATAMOTORS|TATASTEEL|TECHM|NESTLEIND|ONGC|COALINDIA|JSWSTEEL|ADANIENT|ADANIPORTS|BAJAJ-AUTO|BAJAJFINSV|BPCL|BRITANNIA|CIPLA|DRREDDY|EICHERMOT|GRASIM|HDFCLIFE|HEROMOTOCO|HINDALCO|INDUSINDBK|M&M|APOLLOHOSP|DIVISLAB|SBILIFE|TATACONSUM|TRENT|BEL|ZOMATO|UPL)\b/,
  );
  return match ? match[1] : null;
}
