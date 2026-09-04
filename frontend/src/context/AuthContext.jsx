import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { DEMO_EMAIL_KEY, DEMO_UNLOCKED_KEY } from "../api/config";

const AuthContext = createContext(null);

/**
 * Cosmetic gate only — not real auth.
 * Any non-empty email/password unlocks the demo UI in localStorage.
 */
export function AuthProvider({ children }) {
  const [unlocked, setUnlocked] = useState(
    () => localStorage.getItem(DEMO_UNLOCKED_KEY) === "1",
  );
  const [email, setEmail] = useState(
    () => localStorage.getItem(DEMO_EMAIL_KEY) || "",
  );

  const login = useCallback(async (userEmail, _password) => {
    localStorage.setItem(DEMO_UNLOCKED_KEY, "1");
    localStorage.setItem(DEMO_EMAIL_KEY, userEmail);
    setEmail(userEmail);
    setUnlocked(true);
  }, []);

  const signup = useCallback(async (userEmail, password) => {
    return login(userEmail, password);
  }, [login]);

  const logout = useCallback(async () => {
    localStorage.removeItem(DEMO_UNLOCKED_KEY);
    localStorage.removeItem(DEMO_EMAIL_KEY);
    setEmail("");
    setUnlocked(false);
  }, []);

  const value = useMemo(
    () => ({
      email,
      loading: false,
      isAuthenticated: unlocked,
      login,
      signup,
      logout,
    }),
    [email, unlocked, login, signup, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
