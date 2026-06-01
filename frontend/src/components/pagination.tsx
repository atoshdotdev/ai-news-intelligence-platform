"use client";

import {
  Pagination as PaginationComponent,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

type Props = {
  page: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
  onPageChange: (page: number) => void;
};

export function Pagination({
  page,
  totalPages,
  hasNext,
  hasPrev,
  onPageChange,
}: Props) {
  const getPages = () => {
    const pages: (number | "...")[] = [];

    for (let i = 1; i <= totalPages; i++) {
      if (i === 1 || i === totalPages || (i >= page - 1 && i <= page + 1)) {
        pages.push(i);
      } else if (pages[pages.length - 1] !== "...") {
        pages.push("...");
      }
    }

    return pages;
  };

  const pages = getPages();

  return (
    <PaginationComponent className="justify-end">
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious
            onClick={() => onPageChange(Math.max(1, page - 1))}
            className={!hasPrev ? "pointer-events-none opacity-50" : ""}
          />
        </PaginationItem>

        {pages.map((p, idx) => (
          <PaginationItem key={idx}>
            {p === "..." ? (
              <PaginationEllipsis />
            ) : (
              <PaginationLink
                isActive={p === page}
                onClick={() => onPageChange(p)}
              >
                {p}
              </PaginationLink>
            )}
          </PaginationItem>
        ))}

        <PaginationItem>
          <PaginationNext
            onClick={() => onPageChange(Math.min(totalPages, page + 1))}
            className={!hasNext ? "pointer-events-none opacity-50" : ""}
          />
        </PaginationItem>
      </PaginationContent>
    </PaginationComponent>
  );
}
