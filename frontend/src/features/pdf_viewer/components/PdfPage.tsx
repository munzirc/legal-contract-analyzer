import { useEffect, useRef } from "react";
import type { PDFPageProxy } from "pdfjs-dist";

interface PdfPageProps {
  page: PDFPageProxy;
  scale: number;
}

export default function PdfPage({ page, scale }: PdfPageProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;

    if (!canvas) return;

    let cancelled = false;

    const viewport = page.getViewport({ scale });
    const outputScale = window.devicePixelRatio || 1;

    canvas.width = Math.floor(viewport.width * outputScale);
    canvas.height = Math.floor(viewport.height * outputScale);

    canvas.style.width = `${viewport.width}px`;
    canvas.style.height = `${viewport.height}px`;

    const context = canvas.getContext("2d");

    if (!context) return;

    const renderTask = page.render({
      canvas,
      canvasContext: context,
      viewport,
      transform:
        outputScale !== 1
          ? [outputScale, 0, 0, outputScale, 0, 0]
          : null,
    });

    renderTask.promise.catch((error: unknown) => {
      if (!cancelled && error instanceof Error) {
        if (error.name !== "RenderingCancelledException") {
          console.error("PDF page rendering failed:", error);
        }
      }
    });

    return () => {
      cancelled = true;
      renderTask.cancel();
    };
  }, [page, scale]);

  return (
    <div className="flex w-max min-w-full justify-center">
      <canvas
        ref={canvasRef}
        className="shadow-md"
      />
    </div>
  );
}