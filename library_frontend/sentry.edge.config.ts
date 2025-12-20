import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: "https://f14229bc489604f68803e7026dcf292c@o4510567686733824.ingest.us.sentry.io/4510567691911168",
  
  tracesSampleRate: 0.1,
  
  enabled: process.env.NODE_ENV === "production",
});
