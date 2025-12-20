"use client";

import * as Sentry from "@sentry/nextjs";
import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html>
      <body>
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#FDFCFA] via-[#FBF8F3] to-[#F5EFE6]">
          <div className="text-center p-8">
            <div className="text-6xl mb-4">😔</div>
            <h2 className="text-2xl font-bold text-[#2D2A26] mb-4">
              Что-то пошло не так
            </h2>
            <p className="text-[#8B8279] mb-6">
              Мы уже знаем о проблеме и работаем над её решением
            </p>
            <button
              onClick={reset}
              className="px-6 py-3 bg-gradient-to-r from-[#B08968] to-[#A67C52] text-white font-medium rounded-xl shadow-lg hover:shadow-xl transition-all"
            >
              Попробовать снова
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
