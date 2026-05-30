import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import AuthForm from "../components/AuthForm";
import { useAuth } from "../context/AuthContext";

export default function Signup() {
  const navigate = useNavigate();
  const { signup, isAuthenticated, loading: authLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!authLoading && isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

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
      title="Create account"
      subtitle="Sign up to start using the swing trade assistant"
      submitLabel="Sign up"
      loading={loading}
      error={error}
      alternateText="Already have an account?"
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
          minLength={6}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 w-full rounded-xl bg-slate-950 border border-slate-700 px-4 py-3 outline-none focus:border-indigo-500"
          placeholder="At least 6 characters"
        />
      </label>

      <label className="block">
        <span className="text-sm text-slate-400">Confirm password</span>
        <input
          type="password"
          required
          minLength={6}
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className="mt-1 w-full rounded-xl bg-slate-950 border border-slate-700 px-4 py-3 outline-none focus:border-indigo-500"
          placeholder="Repeat password"
        />
      </label>
    </AuthForm>
  );
}
