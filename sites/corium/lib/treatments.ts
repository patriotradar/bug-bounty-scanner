/**
 * Treatment data for Corium.
 *
 * `depthMin` / `depthMax` are the working depths in millimetres below the skin
 * surface. They drive the depth diagram directly — the diagram is generated from
 * this file rather than drawn by hand, so editing a depth here moves the needle.
 *
 * Naming note: UK advertising rules (CAP Code 12.12) prohibit advertising
 * prescription-only medicines to the public, so botulinum toxin brand names are
 * never used in patient-facing copy. See README.
 */

export type Treatment = {
  id: string;
  name: string;
  /** Anatomical layer the treatment acts on, in clinical terms. */
  plane: string;
  depthMin: number;
  depthMax: number;
  onset: string;
  duration: string;
  downtime: string;
  from: number;
  summary: string;
};

export const TREATMENTS: Treatment[] = [
  {
    id: "peel",
    name: "Medical peel",
    plane: "Epidermis to papillary dermis",
    depthMin: 0.06,
    depthMax: 0.5,
    onset: "7–14 days",
    duration: "Course dependent",
    downtime: "2–5 days of visible shedding",
    from: 120,
    summary:
      "A controlled chemical injury to the outer layers, prescribed by strength rather than by brand. Used for pigmentation, texture and congestion.",
  },
  {
    id: "laser",
    name: "Laser resurfacing",
    plane: "Epidermis to reticular dermis",
    depthMin: 0.1,
    depthMax: 1.5,
    onset: "3–6 weeks",
    duration: "12–24 months",
    downtime: "4–7 days",
    from: 450,
    summary:
      "Fractional 1927 nm and 2940 nm wavelengths, chosen against your skin type on the Fitzpatrick scale. Not suitable for every skin.",
  },
  {
    id: "booster",
    name: "Skin boosters",
    plane: "Superficial dermis",
    depthMin: 0.5,
    depthMax: 1.5,
    onset: "2–4 weeks",
    duration: "6–9 months",
    downtime: "24–48 hours of small bumps",
    from: 275,
    summary:
      "Microinjections of hyaluronic acid or polynucleotides placed across the dermis. Changes skin quality. Does not change facial shape.",
  },
  {
    id: "microneedling",
    name: "RF microneedling",
    plane: "Papillary to reticular dermis",
    depthMin: 0.5,
    depthMax: 3.0,
    onset: "4–8 weeks",
    duration: "12–18 months",
    downtime: "24–72 hours",
    from: 395,
    summary:
      "Insulated needles deliver radiofrequency at a set depth, so energy lands in the dermis and spares the surface. Depth is adjusted per facial zone.",
  },
  {
    id: "antiwrinkle",
    name: "Anti-wrinkle treatment",
    plane: "Intramuscular",
    depthMin: 2.5,
    depthMax: 5.0,
    onset: "3–14 days",
    duration: "3–4 months",
    downtime: "None",
    from: 195,
    summary:
      "A prescription-only medicine, so it requires a face-to-face consultation with the prescriber before any treatment is given. Dosed in units, per muscle.",
  },
  {
    id: "filler",
    name: "Dermal filler",
    plane: "Deep dermis to supraperiosteal",
    depthMin: 3.0,
    depthMax: 8.0,
    onset: "Immediate, settles at 14 days",
    duration: "6–18 months",
    downtime: "48 hours of swelling",
    from: 340,
    summary:
      "Hyaluronic acid placed on or near bone to restore structural volume. Reversible with hyaluronidase, which we stock on site.",
  },
];

/**
 * Skin strata, with their lower boundary in millimetres.
 *
 * `label` is deliberately short: the papillary dermis band is only ~24px tall
 * in the diagram, so its name has to fit on a single line beside it.
 */
export const STRATA = [
  { id: "epidermis", label: "Epidermis", to: 0.1 },
  { id: "papillary", label: "Papillary", to: 0.3 },
  { id: "reticular", label: "Reticular", to: 2.0 },
  { id: "subcutis", label: "Subcutis", to: 8.0 },
  { id: "periosteum", label: "Periosteum", to: 10 },
];

export const MAX_DEPTH = 10;

/**
 * Depth-to-position mapping, as a fraction of diagram height.
 *
 * A linear millimetre scale would render the epidermis as a 1% sliver and make
 * the shallow treatments unreadable, so depth is square-rooted to give the
 * surface layers proportionally more room. The diagram is labelled as
 * non-linear because of this.
 */
export function depthToFraction(mm: number): number {
  return Math.sqrt(Math.min(mm, MAX_DEPTH) / MAX_DEPTH);
}
