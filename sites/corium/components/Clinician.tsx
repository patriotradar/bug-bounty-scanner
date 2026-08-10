import Reveal from "./Reveal";

const REGISTRATIONS = [
  { label: "GMC reference", value: "7412998" },
  { label: "JCCP practitioner register", value: "Entry level 7" },
  { label: "Save Face accredited", value: "Renewed 2026" },
  { label: "CQC registered", value: "1-8842019" },
  { label: "Indemnity", value: "Hamilton Fraser" },
];

export default function Clinician() {
  return (
    <section className="shell band" id="clinician">
      <div className="clin-grid">
        <Reveal>
          <div className="clin-card">
            {/* Deliberately an empty frame rather than stock photography: a
                clinic's trust rests on the real clinician's face, and a
                generic model undermines exactly what this section is for.
                Drop the commissioned portrait in here. */}
            <div className="clin-portrait">
              <span className="clin-portrait-note">
                Portrait
                <br />
                to be commissioned
              </span>
            </div>

            <ul className="clin-reg">
              {REGISTRATIONS.map((r) => (
                <li key={r.label} className="clin-reg-item">
                  <span className="datum">{r.label}</span>
                  <span className="tx-spec-val">{r.value}</span>
                </li>
              ))}
            </ul>
          </div>
        </Reveal>

        <Reveal delay={90}>
          <p className="eyebrow">Clinician</p>
          <h2 className="display-lg head-title">Dr Anneka Reid</h2>
          <p className="datum" style={{ marginTop: "8px" }}>
            MBChB · MRCGP · PGDip Clinical Dermatology
          </p>

          <blockquote className="clin-quote">
            “Most people who come here are frightened of two things: looking
            obviously treated, and being sold something. Both are avoidable.”
          </blockquote>

          <div className="prose" style={{ marginTop: "24px" }}>
            <p>
              Anneka trained in general practice before moving into medical
              dermatology, and has been treating full time in Bath since 2018.
              They still hold an NHS dermatology clinic one day a week, which is
              where most of the skin cancer referrals and the difficult acne
              cases go.
            </p>
            <p style={{ marginTop: "16px" }}>
              That NHS work is deliberate. It keeps the threshold for what counts
              as a medical problem calibrated against something other than a
              private price list — and it means a suspicious lesion spotted
              during an aesthetic consultation goes down a referral pathway the
              same week rather than being mentioned in passing.
            </p>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
