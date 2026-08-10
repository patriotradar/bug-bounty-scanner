const HOURS = [
  { day: "Tuesday – Thursday", time: "09:00 – 18:00" },
  { day: "Friday", time: "09:00 – 15:00" },
  { day: "Saturday", time: "By arrangement" },
  { day: "Sunday – Monday", time: "Closed" },
];

export default function SiteFooter() {
  return (
    <footer className="foot">
      <div className="shell">
        <div className="foot-grid">
          <div>
            <p className="foot-mark">Corium</p>
            <address style={{ fontStyle: "normal", marginTop: "16px" }}>
              14a Margaret&rsquo;s Buildings
              <br />
              Bath BA1 2LP
              <br />
              Somerset
            </address>
            <p style={{ marginTop: "16px" }}>
              <a className="foot-link" href="tel:+441225000000">
                01225 000 000
              </a>
              <br />
              <a className="foot-link" href="mailto:clinic@corium.example">
                clinic@corium.example
              </a>
            </p>
          </div>

          <div>
            <p className="foot-title">Opening hours</p>
            <ul className="foot-list">
              {HOURS.map((h) => (
                <li key={h.day}>
                  {h.day}
                  <br />
                  <span className="datum">{h.time}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="foot-title">Practice</p>
            <ul className="foot-list">
              <li>
                <a className="foot-link" href="#treatments">
                  Treatments
                </a>
              </li>
              <li>
                <a className="foot-link" href="#pathway">
                  What happens
                </a>
              </li>
              <li>
                <a className="foot-link" href="#clinician">
                  Clinician
                </a>
              </li>
              <li>
                <a className="foot-link" href="#enquire">
                  Request a consultation
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="foot-legal">
          <p className="foot-legal-note">
            Corium is registered with the Care Quality Commission. Treatments
            involving prescription-only medicines require a face-to-face
            consultation with the prescriber, and are never advertised by brand
            name in line with the CAP Code. Results vary between individuals and
            no outcome is guaranteed.
          </p>
          <p>
            © {new Date().getFullYear()} Corium Clinic Ltd · Registered in
            England &amp; Wales · Fictional business created for demonstration.
          </p>
        </div>
      </div>
    </footer>
  );
}
