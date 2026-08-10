const CREDS = [
  "GMC-registered doctor",
  "JCCP practitioner register",
  "Save Face accredited",
  "CQC registered clinic",
];

function CheckMark() {
  return (
    <svg
      className="creds-icon"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      aria-hidden="true"
    >
      <path d="m5 12.5 4.5 4.5L19 7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function Accreditations() {
  return (
    <section className="creds" aria-label="Accreditations">
      <div className="shell creds-inner">
        {CREDS.map((c) => (
          <span key={c} className="creds-item">
            <CheckMark />
            <span className="datum">{c}</span>
          </span>
        ))}
      </div>
    </section>
  );
}
