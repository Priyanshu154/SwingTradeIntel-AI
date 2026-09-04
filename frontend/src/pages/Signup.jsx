import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import AuthForm from "../components/AuthForm";
import { useAuth } from "../context/AuthContext";

/** Cosmetic signup — mirrors login; stores nothing server-side. */
export default function Signup() {
  const navigate = useNavigate();
  const { signup, isAuthenticated, loading: authLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!authLoading && isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signup(email, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthForm
      title="Create demo profile"
      subtitle="Local unlock only — no accounts are created on the server"
      submitLabel="Continue"
      loading={loading}
      error={error}
      alternateText="Already unlocked?"
      alternateLink="/login"
      alternateLabel="Sign in"
      onSubmit={handleSubmit}
    >
      <label className="block">
        <span className="text-sm text-slate-400">Email</span>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 w-full rounded-xl bg-slate-950 border border-slate-700 px-4 py-3 outline-none focus:border-indigo-500"
          placeholder="you@example.com"
        />
      </label>

      <label className="block">
        <span className="text-sm text-slate-400">Password</span>
        <input
          type="password"
          required
          minLength={1}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 w-full rounded-xl bg-slate-950 border border-slate-700 px-4 py-3 outline-none focus:border-indigo-500"
          placeholder="any password for demo"
        />
      </label>
    </AuthForm>
  );
}
