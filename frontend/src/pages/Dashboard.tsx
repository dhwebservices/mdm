import { useQuery } from "@tanstack/react-query";
import { Laptop, ScrollText, Ticket, Users } from "lucide-react";
import { api } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/State";

const metricIcons = [Laptop, Laptop, Users, Ticket, ScrollText, ScrollText];

export function Dashboard() {
  const dashboard = useQuery({ queryKey: ["dashboard"], queryFn: api.dashboard });
  const devices = useQuery({ queryKey: ["devices"], queryFn: api.devices });
  const audit = useQuery({ queryKey: ["audit"], queryFn: api.audit });

  if (dashboard.isLoading) {
    return <LoadingState label="Loading fleet summary" />;
  }

  if (dashboard.isError) {
    return <ErrorState message="Unable to load live dashboard data. Check authentication and API availability." />;
  }

  const summary = dashboard.data ?? {
    devices: 0,
    enrolled_devices: 0,
    users: 0,
    open_tickets: 0,
    failed_commands: 0,
    unread_notifications: 0
  };
  const deviceRows = devices.data ?? [];
  const auditRows = audit.data ?? [];
  const metrics = [
    ["Devices", summary.devices],
    ["Enrolled", summary.enrolled_devices],
    ["Users", summary.users],
    ["Open tickets", summary.open_tickets],
    ["Failed commands", summary.failed_commands],
    ["Unread notifications", summary.unread_notifications]
  ] as const;

  return (
    <div className="space-y-6">
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-6" aria-label="Fleet metrics">
        {metrics.map(([label, value], index) => {
          const Icon = metricIcons[index];
          return (
            <div key={label} className="rounded-lg border border-line bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">{label}</span>
                <Icon className="h-4 w-4 text-teal-700" aria-hidden="true" />
              </div>
              <div className="mt-3 text-2xl font-bold text-ink">{value}</div>
            </div>
          );
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_380px]">
        <div className="rounded-lg border border-line bg-white">
          <div className="border-b border-line px-4 py-3">
            <h2 className="text-sm font-semibold text-ink">Devices</h2>
          </div>
          {devices.isLoading ? (
            <div className="p-4">
              <LoadingState label="Loading devices" />
            </div>
          ) : devices.isError ? (
            <div className="p-4">
              <ErrorState message="Unable to load devices." />
            </div>
          ) : deviceRows.length === 0 ? (
            <div className="p-4">
              <EmptyState title="No devices enrolled" body="Devices will appear here after ABM/ADE enrolment or manual inventory creation." />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Serial</th>
                    <th className="px-4 py-3 font-semibold">Model</th>
                    <th className="px-4 py-3 font-semibold">OS</th>
                    <th className="px-4 py-3 font-semibold">State</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {deviceRows.map((device) => (
                    <tr key={device.id}>
                      <td className="px-4 py-3 font-medium text-ink">{device.serial_number}</td>
                      <td className="px-4 py-3 text-slate-600">{device.model ?? "Unknown"}</td>
                      <td className="px-4 py-3 text-slate-600">{device.os_version ?? "Unknown"}</td>
                      <td className="px-4 py-3">
                        <span className={`rounded-full px-2 py-1 text-xs ${device.enrolled ? "bg-teal-50 text-teal-800" : "bg-slate-100 text-slate-700"}`}>
                          {device.enrolled ? "Enrolled" : "Not enrolled"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="rounded-lg border border-line bg-white">
          <div className="border-b border-line px-4 py-3">
            <h2 className="text-sm font-semibold text-ink">Audit Log</h2>
          </div>
          <div className="p-4">
            {audit.isLoading ? (
              <LoadingState label="Loading audit entries" />
            ) : audit.isError ? (
              <ErrorState message="Unable to load audit log." />
            ) : auditRows.length === 0 ? (
              <EmptyState title="No audit entries" body="Administrative actions and MDM events will be recorded here." />
            ) : (
              <ol className="space-y-3">
                {auditRows.slice(0, 8).map((entry) => (
                  <li key={entry.id} className="rounded-md border border-line p-3">
                    <div className="text-sm font-semibold text-ink">{entry.action}</div>
                    <div className="mt-1 text-xs text-slate-500">{new Date(entry.created_at).toLocaleString()}</div>
                  </li>
                ))}
              </ol>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
