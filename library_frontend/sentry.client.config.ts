import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: "https://f14229bc489604f68803e7026dcf292c@o4510567686733824.ingest.us.sentry.io/4510567691911168",
  
  // Включаем логи (console.log/warn/error будут в Sentry)
  _experiments: {
    enableLogs: true,
  },
  
  // Интеграция для автоматического логирования console
  integrations: [
    Sentry.consoleLoggingIntegration({ levels: ["warn", "error"] }),
  ],
  
  // Процент трейсов для performance monitoring (10%)
  tracesSampleRate: 0.1,
  
  // Включаем replay для записи сессий при ошибках
  replaysSessionSampleRate: 0,
  replaysOnErrorSampleRate: 1.0,
  
  // Отключаем в dev режиме
  enabled: process.env.NODE_ENV === "production",
  
  // Игнорируем некритичные ошибки
  ignoreErrors: [
    "ResizeObserver loop limit exceeded",
    "ResizeObserver loop completed with undelivered notifications",
    "Non-Error promise rejection captured",
  ],
  
  // Добавляем контекст
  beforeSend(event) {
    // Можно фильтровать или модифицировать события
    return event;
  },
});
