"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

const NAV_ITEMS = [
  { href: "/", label: "오늘의 후보" },
  { href: "/tracking", label: "성과 검증" },
  { href: "/runs", label: "배치 이력" },
] as const;

const CHORD_TIMEOUT_MS = 900;

function isEditableTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  const tag = target.tagName;
  return tag === "INPUT" || tag === "TEXTAREA" || target.isContentEditable;
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [sheetOpen, setSheetOpen] = useState(false);
  const [announcement, setAnnouncement] = useState("");

  const pendingGRef = useRef(false);
  const pendingGTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const announce = useCallback((message: string) => {
    // 동일한 문구가 연달아 와도 aria-live가 다시 읽도록 한 틱 비웠다가 채운다.
    setAnnouncement("");
    requestAnimationFrame(() => setAnnouncement(message));
  }, []);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (isEditableTarget(event.target)) return;
      if (event.metaKey || event.ctrlKey || event.altKey) return;

      const key = event.key;

      if (pendingGRef.current) {
        pendingGRef.current = false;
        if (pendingGTimeoutRef.current) clearTimeout(pendingGTimeoutRef.current);

        if (key === "t") {
          event.preventDefault();
          router.push("/");
          announce("오늘의 후보로 이동했습니다.");
          return;
        }
        if (key === "v") {
          event.preventDefault();
          router.push("/tracking");
          announce("성과 검증으로 이동했습니다.");
          return;
        }
        // g로 시작하는 체인이 아니었을 뿐, 그 키 자체의 단축키는 그대로 살려야 한다
        // (예: g 다음 r을 누르면 새로고침이 씹히던 버그 수정).
      }

      switch (key) {
        case "g":
          pendingGRef.current = true;
          pendingGTimeoutRef.current = setTimeout(() => {
            pendingGRef.current = false;
          }, CHORD_TIMEOUT_MS);
          break;
        case "r":
          event.preventDefault();
          router.refresh();
          announce("새로고침했습니다.");
          break;
        case "Escape":
          setSheetOpen(false);
          break;
        case "j":
        case "k":
        case "Enter":
        case "/":
          // Epic 1은 후보 카드/검색 UI가 없어 no-op으로만 등록한다(향후 스토리에서 실제 타깃 연결).
          break;
        default:
          break;
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      if (pendingGTimeoutRef.current) clearTimeout(pendingGTimeoutRef.current);
    };
  }, [announce, router]);

  useEffect(() => {
    setSheetOpen(false);
  }, [pathname]);

  return (
    <div className="app-shell">
      <button
        type="button"
        className="app-shell__sheet-toggle"
        aria-expanded={sheetOpen}
        aria-controls="app-shell-nav"
        onClick={() => setSheetOpen((open) => !open)}
      >
        {sheetOpen ? "메뉴 닫기" : "메뉴 열기"}
      </button>

      {sheetOpen && (
        <div
          className="app-shell__scrim"
          aria-hidden="true"
          onClick={() => setSheetOpen(false)}
        />
      )}

      <nav
        id="app-shell-nav"
        className={
          sheetOpen ? "app-shell__nav app-shell__nav--open" : "app-shell__nav"
        }
        aria-label="주요 내비게이션"
      >
        <div className="app-shell__brand">wave-double</div>
        <ul>
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={
                    active
                      ? "app-shell__link app-shell__link--active"
                      : "app-shell__link"
                  }
                  aria-current={active ? "page" : undefined}
                >
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <main className="app-shell__content">{children}</main>

      <div className="sr-only" role="status" aria-live="polite">
        {announcement}
      </div>
    </div>
  );
}
