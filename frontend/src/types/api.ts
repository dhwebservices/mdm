export type DashboardSummary = {
  devices: number;
  enrolled_devices: number;
  users: number;
  open_tickets: number;
  failed_commands: number;
  unread_notifications: number;
};

export type Device = {
  id: string;
  serial_number: string;
  udid: string | null;
  model: string | null;
  platform: string;
  os_version: string | null;
  supervised: boolean;
  enrolled: boolean;
  last_checkin_at: string | null;
};

export type AuditEntry = {
  id: string;
  action: string;
  target_type: string | null;
  target_id: string | null;
  created_at: string;
};
