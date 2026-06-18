import { AlertCircle, Loader2 } from "lucide-react";

export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <div className="flex min-h-32 items-center gap-3 rounded-lg border border-line bg-white p-5 text-sm text-slate-600">
      <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex min-h-32 items-center gap-3 rounded-lg border border-red-200 bg-red-50 p-5 text-sm text-red-800">
      <AlertCircle className="h-4 w-4" aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-lg border border-dashed border-line bg-white p-6">
      <h3 className="text-sm font-semibold text-ink">{title}</h3>
      <p className="mt-1 text-sm text-slate-600">{body}</p>
    </div>
  );
}
