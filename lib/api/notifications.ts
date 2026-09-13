import { api } from "./client";

export interface AppNotification {
  id: string;
  type: "critical" | "warning" | "info" | "success";
  title: string;
  message: string;
  link: string;
  isRead: boolean;
  createdAt: string;
}

export interface NotificationsResponse {
  unreadCount: number;
  notifications: AppNotification[];
}

export const getNotifications = () => api<NotificationsResponse>("/api/notifications");
export const markNotificationAsRead = (id: string) => api<void>(`/api/notifications/${id}/read`, { method: "POST" });
export const markAllNotificationsAsRead = () => api<void>("/api/notifications/read-all", { method: "POST" });
export const getNavBadges = () => api<{ requests: number; responses: number; threads: number }>("/api/nav/badges");
