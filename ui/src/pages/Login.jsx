import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import AuthForm from "../components/AuthForm";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { login, isAuthenticated, loading: authLoading } = useAuth();
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
      await login(email, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthForm
      title="Welcome back"
      subtitle="Sign in to access the AI Swing Trade Assistant"
      submitLabel="Sign in"
      loading={loading}
      error={error}
      alternateText="Don't have an account?"
      alternateLink="/signup"
      alternateLabel="Create account"
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
          minLength={6}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 w-full rounded-xl bg-slate-950 border border-slate-700 px-4 py-3 outline-none focus:border-indigo-500"
          placeholder="••••••••"
        />
      </label>
    </AuthForm>
  );
}
