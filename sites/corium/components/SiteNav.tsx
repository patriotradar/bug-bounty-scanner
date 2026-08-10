"use client";

import { useEffect, useState } from "react";

const LINKS = [
  { href: "#treatments", label: "Treatments" },
  { href: "#approach", label: "Approach" },
  { href: "#pathway", label: "What happens" },
  { href: "#clinician", label: "Clinician" },
];

export default function SiteNav() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    // A sentinel observer instead of a scroll handler: no work on the main
    // thread while scrolling.
    const sentinel = document.createElement("div");
    sentinel.style.cssText = "position:absolute;top:0;height:8px;width:1px;";
    document.body.prepend(sentinel);

    const observer = new IntersectionObserver(
      ([entry]) => setScrolled(!entry.isIntersecting),
      { threshold: 0 },
    );
    observer.observe(sentinel);

    return () => {
      observer.disconnect();
      sentinel.remove();
    };
  }, []);

  return (
    <header className={`nav${scrolled ? " nav-scrolled" : ""}`}>
      <nav className="shell nav-inner" aria-label="Primary">
        <a className="nav-mark" href="#top">
          Corium
          <span className="nav-mark-sub">Bath</span>
        </a>

        <div className="nav-links">
          {LINKS.map((link) => (
            <a key={link.href} className="nav-link" href={link.href}>
              {link.label}
            </a>
          ))}
        </div>

        <a className="btn btn-primary nav-cta" href="#enquire">
          Request a consultation
        </a>
      </nav>
    </header>
  );
}
