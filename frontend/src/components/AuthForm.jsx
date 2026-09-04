import { Link } from "react-router-dom";

export default function AuthForm({
  title,
  subtitle,
  children,
  submitLabel,
  loading,
  error,
  alternateText,
  alternateLink,
  alternateLabel,
  onSubmit,
}) {
  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl bg-slate-900 border border-slate-800 p-8 shadow-xl">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
          <p className="text-slate-400 text-sm mt-2">{subtitle}</p>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          {children}

          {error && (
            <p className="text-sm text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 transition rounded-xl py-3 font-medium"
          >
            {loading ? "Please wait..." : submitLabel}
          </button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-6">
          {alternateText}{" "}
          <Link
            to={alternateLink}
            className="text-indigo-400 hover:text-indigo-300 transition"
          >
            {alternateLabel}
          </Link>
        </p>
      </div>
    </div>
  );
}
