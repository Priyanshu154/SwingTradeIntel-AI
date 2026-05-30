import { createContext, useCallback, useContext, useEffect, useState } from "react";
import {
  AUTH_EMAIL_KEY,
  AUTH_TOKEN_KEY,
  BACKEND_URL,
} from "../api/config";

const AuthContext = createContext(null);

function parseApiError(data, fallback) {
  const detail = data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join(", ");
  }
  return fallback;
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(AUTH_TOKEN_KEY));
  const [email, setEmail] = useState(() => localStorage.getItem(AUTH_EMAIL_KEY));
  const [loading, setLoading] = useState(true);

  const persistSession = useCallback((accessToken, userEmail) => {
    localStorage.setItem(AUTH_TOKEN_KEY, accessToken);
    localStorage.setItem(AUTH_EMAIL_KEY, userEmail);
    setToken(accessToken);
    setEmail(userEmail);
  }, []);

  const clearSession = useCallback(() => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_EMAIL_KEY);
    setToken(null);
    setEmail(null);
  }, []);

  const authFetch = useCallback(
    async (path, options = {}) => {
      const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      };
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      return fetch(`${BACKEND_URL}${path}`, { ...options, headers });
    },
    [token],
  );

  useEffect(() => {
    let cancelled = false;

    async function validateSession() {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`${BACKEND_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) {
          clearSession();
        } else {
          const data = await response.json();
          if (!cancelled) {
            setEmail(data.email);
            localStorage.setItem(AUTH_EMAIL_KEY, data.email);
          }
        }
      } catch {
        clearSession();
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    validateSession();
    return () => {
      cancelled = true;
    };
  }, [token, clearSession]);

  const signup = async (userEmail, password) => {
    const response = await fetch(`${BACKEND_URL}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: userEmail, password }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(parseApiError(data, "Sign up failed"));
    }
    persistSession(data.access_token, data.email);
    return data;
  };

  const login = async (userEmail, password) => {
    const response = await fetch(`${BACKEND_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: userEmail, password }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(parseApiError(data, "Login failed"));
    }
    persistSession(data.access_token, data.email);
    return data;
  };

  const logout = async () => {
    try {
      if (token) {
        await authFetch("/auth/logout", { method: "POST" });
      }
    } catch {
      // Clear local session even if the server call fails
    } finally {
      clearSession();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        email,
        loading,
        isAuthenticated: Boolean(token),
        signup,
        login,
        logout,
        authFetch,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
