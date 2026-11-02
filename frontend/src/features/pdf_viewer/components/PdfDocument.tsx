import { useEffect, useRef, useState } from "react";
import type { PDFDocumentProxy } from "pdfjs-dist";

import type { CitationTarget } from "../../../stores/useAppStore";
import { usePdfPage } from "../hooks/usePdfPage";
import PdfPage from "./PdfPage";

interface PdfDocumentProps {
    document: PDFDocumentProxy;
    zoom: number;
    citationTarget: CitationTarget | null;
}

interface PdfPageItemProps {
    document: PDFDocumentProxy;
    pageNumber: number;
    scrollContainer: HTMLDivElement | null;
    scale: number;
    citationTarget: CitationTarget | null;
}

interface PageDimensions {
    width: number;
    height: number;
}

function PdfPageItem({
    document,
    pageNumber,
    scrollContainer,
    scale,
    citationTarget,
}: PdfPageItemProps) {
    const pageRef = useRef<HTMLDivElement>(null);
    const [shouldLoad, setShouldLoad] = useState(false);

    const pageRegions =
        citationTarget?.regions.filter(
            (region) => region.page_number === pageNumber
        ) ?? [];

    const isCitationPage = pageRegions.length > 0;

    const firstCitationPage =
        citationTarget && citationTarget.regions.length > 0
            ? Math.min(
                ...citationTarget.regions.map(
                    (region) => region.page_number
                )
            )
            : null;

    // Load pages when they approach the viewport.
    useEffect(() => {
        const element = pageRef.current;

        if (!element || !scrollContainer) return;

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setShouldLoad(true);
                    observer.disconnect();
                }
            },
            {
                root: scrollContainer,
                rootMargin: "800px 0px",
            }
        );

        observer.observe(element);

        return () => observer.disconnect();
    }, [scrollContainer]);

    const { page, loading, error } = usePdfPage(
        shouldLoad ? document : null,
        pageNumber
    );

    useEffect(() => {
        setShouldLoad(false);
    }, [document]);

    useEffect(() => {
        if (!isCitationPage) return;

        setShouldLoad(true);
    }, [citationTarget?.evidenceId, isCitationPage]);


    useEffect(() => {
        if (!isCitationPage || !page || loading) return;

        if (pageNumber !== firstCitationPage) return;

        const animationFrame = requestAnimationFrame(() => {
            pageRef.current?.scrollIntoView({
                behavior: "smooth",
                block: "center",
            });
        });

        return () => cancelAnimationFrame(animationFrame);
    }, [
        citationTarget?.evidenceId,
        isCitationPage,
        page,
        loading,
        pageNumber,
        firstCitationPage,
    ]);



    return (
        <div
            ref={pageRef}
            className="w-max min-w-full"
        >
            <div className="mb-2 text-center text-xs font-medium text-slate-500">
                Page {pageNumber}
            </div>

            <div className="flex min-h-40 justify-center">
                {page && (
                    <PdfPage
                        page={page}
                        scale={scale}
                        regions={pageRegions}
                    />
                )}

                {loading && (
                    <div className="flex min-h-40 items-center justify-center text-sm text-slate-400">
                        Loading page {pageNumber}...
                    </div>
                )}

                {error && (
                    <div className="flex min-h-40 items-center justify-center text-sm text-red-600">
                        Failed to load page {pageNumber}: {error}
                    </div>
                )}

                {!shouldLoad && (
                    <div className="flex min-h-40 items-center justify-center text-sm text-slate-400">
                        Page {pageNumber}
                    </div>
                )}
            </div>
        </div>
    );
}

export default function PdfDocument({
    document,
    zoom,
    citationTarget,
}: PdfDocumentProps) {
    const [scrollContainer, setScrollContainer] =
        useState<HTMLDivElement | null>(null);

    const [containerSize, setContainerSize] = useState({
        width: 0,
        height: 0,
    });

    const [pageDimensions, setPageDimensions] =
        useState<PageDimensions | null>(null);

    // Get the dimensions of the first PDF page.
    useEffect(() => {
        let cancelled = false;

        setPageDimensions(null);

        document
            .getPage(1)
            .then((page) => {
                if (cancelled) return;

                const viewport = page.getViewport({ scale: 1 });

                setPageDimensions({
                    width: viewport.width,
                    height: viewport.height,
                });
            })
            .catch((error: unknown) => {
                if (!cancelled) {
                    console.error(
                        "Failed to get PDF page dimensions:",
                        error
                    );
                }
            });

        return () => {
            cancelled = true;
        };
    }, [document]);

    // Observe the available scrolling area.
    useEffect(() => {
        if (!scrollContainer) return;

        const observer = new ResizeObserver(([entry]) => {
            setContainerSize({
                width: entry.contentRect.width,
                height: entry.contentRect.height,
            });
        });

        observer.observe(scrollContainer);

        return () => observer.disconnect();
    }, [scrollContainer]);

    // Calculate a scale that fits both width and height.
    const fitScale =
        pageDimensions &&
            containerSize.width > 32 &&
            containerSize.height > 32
            ? Math.min(
                (containerSize.width - 32) / pageDimensions.width,
                (containerSize.height - 32) / pageDimensions.height
            )
            : 1;

    const scale = fitScale * zoom;

    return (
        <div
            ref={setScrollContainer}
            className="h-full w-full min-h-0 custom-scrollbar overflow-auto p-4"
        >
            <div className="space-y-8">
                {Array.from(
                    { length: document.numPages },
                    (_, index) => index + 1
                ).map((pageNumber) => (
                    <PdfPageItem
                        key={pageNumber}
                        document={document}
                        pageNumber={pageNumber}
                        scrollContainer={scrollContainer}
                        scale={scale}
                        citationTarget={citationTarget}
                    />
                ))}
            </div>
        </div>
    );
}