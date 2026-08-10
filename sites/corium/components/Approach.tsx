import Reveal from "./Reveal";

const PRINCIPLES = [
  {
    key: "Declining",
    title: "We turn work away",
    body: "Roughly one consultation in five ends with us recommending nothing at all, or recommending something we do not sell. If a treatment will not achieve what you are describing, saying so is the service you are paying for.",
  },
  {
    key: "Prescribing",
    title: "The prescriber sees you first",
    body: "Prescription-only medicines are prescribed face to face by the clinician who will treat you. No remote prescribing, no prescriber who never meets you, no signing off a list of names before a clinic day.",
  },
  {
    key: "Reversal",
    title: "We stock what undoes it",
    body: "Hyaluronidase dissolves hyaluronic acid filler and is kept on site with an emergency protocol for vascular occlusion. A clinic that places filler without holding the reversal agent is one you should leave.",
  },
];

export default function Approach() {
  return (
    <section className="approach" id="approach">
      <div className="shell band">
        <Reveal>
          <p className="eyebrow approach-eyebrow">Approach</p>
          <h2 className="display-lg approach-title">
            The safeguards matter more than the menu
          </h2>
        </Reveal>

        <div className="approach-grid">
          {PRINCIPLES.map((p, i) => (
            <Reveal key={p.key} className="approach-item" delay={i * 90}>
              <span className="approach-index">{p.key}</span>
              <h3 className="approach-item-title">{p.title}</h3>
              <p className="approach-item-body">{p.body}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
