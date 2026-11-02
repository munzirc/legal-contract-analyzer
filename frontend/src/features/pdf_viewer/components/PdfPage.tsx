import { useEffect, useRef } from "react";
import type { PDFPageProxy } from "pdfjs-dist";

import type { EvidenceRegion } from "../../../stores/useAppStore";

interface PdfPageProps {
    page: PDFPageProxy;
    scale: number;
    regions: EvidenceRegion[];
}

export default function PdfPage({
    page,
    scale,
    regions,
}: PdfPageProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const viewport = page.getViewport({ scale });

    useEffect(() => {
        const canvas = canvasRef.current;

        if (!canvas) return;

        let cancelled = false;

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
                    ? [
                          outputScale,
                          0,
                          0,
                          outputScale,
                          0,
                          0,
                      ]
                    : undefined,
        });

        renderTask.promise.catch((error: unknown) => {
            if (!cancelled && error instanceof Error) {
                if (error.name !== "RenderingCancelledException") {
                    console.error(
                        "PDF page rendering failed:",
                        error
                    );
                }
            }
        });

        return () => {
            cancelled = true;
            renderTask.cancel();
        };
    }, [page, viewport]);

    return (
        <div
            className="relative w-max"
            style={{
                width: viewport.width,
                height: viewport.height,
            }}
        >
            <canvas
                ref={canvasRef}
                className="block shadow-md"
            />

            {regions.length > 0 && (
                <svg
                    className="pointer-events-none absolute inset-0"
                    width={viewport.width}
                    height={viewport.height}
                    viewBox={`0 0 ${viewport.width} ${viewport.height}`}
                >
                    {regions.map((region, index) => (
                        <rect
                            key={`${region.page_number}-${index}`}
                            x={region.x1 * scale}
                            y={region.y1 * scale}
                            width={(region.x2 - region.x1) * scale}
                            height={(region.y2 - region.y1) * scale}
                            fill="rgba(173, 255, 47, 0.35)"
                            rx={2}
                        />
                    ))}
                </svg>
            )}
        </div>
    );
}