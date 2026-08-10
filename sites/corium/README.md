# Corium — aesthetics clinic site

A marketing site for a **fictional** doctor-led aesthetics clinic in Bath, built
as a demonstration piece. It is a standalone Next.js app and shares nothing with
the scanner at the repository root.

```bash
cd sites/corium
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npm run typecheck
```

## Design direction

The brief was a premium beauty site with elegant, device-friendly animation. The
obvious answer for this sector — Playfair Display, soft pink, gold accents,
full-bleed spa photography — was rejected deliberately: it is what every
template in the category already looks like, and it sells a spa rather than a
medical practice.

The direction taken instead is **clinical-editorial**. An aesthetics clinic's
real advantage over a spa is precision, so measurement is the ornament.

| Decision | Choice | Why |
|---|---|---|
| Palette | Surgical-drape green, skin-marker violet, porcelain | Both accents are the colours of real objects in a treatment room. Violet is what surgeons mark faces with. |
| Display face | Bodoni Moda | Extreme stroke contrast — hairlines that read as precision at large sizes. |
| Body face | Instrument Sans | Neutral, slightly narrow, not Inter. |
| Data face | IBM Plex Mono | Carries every measurement, depth and duration. |
| Signature | The depth diagram | Each treatment drawn as a needle descending to the depth it actually works at. |

### The depth diagram

`components/DepthDiagram.tsx` renders its geometry from `lib/treatments.ts`, so
the drawing cannot drift from the stated data — edit a depth and the needle
moves. The vertical axis is square-rooted rather than linear, because at linear
scale the epidermis is a 1%-tall sliver and every shallow treatment collapses
into it. The diagram is labelled as non-linear for that reason.

Structural markers throughout are real quantities (`0.5–1.5 mm`, `day 3–14`)
rather than decorative `01 / 02 / 03` numbering. The one section that *is*
sequential — the 28-day pathway — is numbered by day, because there the order
carries information.

## Animation

No animation library. Load choreography is CSS keyframes; scroll reveals use a
single `IntersectionObserver` per element with no scroll listener anywhere.
Everything animates `opacity` and `transform` only, so nothing triggers layout.

`prefers-reduced-motion` collapses all of it to a static page.

Scroll-reveal hides content with `opacity: 0`, which is only safe if something
is guaranteed to reveal it again. The hidden state is therefore scoped to a
`.js` class set by an inline script before first paint — without JavaScript the
page renders complete and static. `<html>` carries `suppressHydrationWarning`
because that script mutates the class list before React hydrates.

## Verified

- Production build passes, TypeScript clean.
- No horizontal overflow at 320px.
- 171 text nodes checked for contrast: none below WCAG AA.
- Form validates on blur, moves focus to the first invalid field, announces
  errors via `role="alert"`, and the API re-validates server-side.
- Renders fully with JavaScript disabled.
- No hydration errors, no 404s.

Touch targets: primary controls are 48px and the consent checkbox is 24px,
meeting the WCAG 2.5.8 AA minimum of 24px. Stacked footer links are 31px. These
do not all reach the 44px Apple HIG figure, which is a mobile-app guideline
rather than the applicable web standard.

## Before this could go live

1. **The enquiry form does not deliver anywhere.** `app/api/enquiry/route.ts`
   validates and acknowledges, then logs. Wire it to a transactional email
   provider or the clinic's practice-management system. Patient enquiries are
   health-adjacent personal data under UK GDPR, so it needs a lawful basis, a
   retention period matching the six months promised in the consent text, and a
   processor agreement.
2. **Commission a portrait.** The clinician card is an intentionally empty
   frame. Stock photography of a model undermines precisely the trust that
   section exists to build.
3. **Replace the invented content.** Name, address, phone, GMC number,
   registration IDs and prices are all fabricated. The prices are plausible for
   premium UK aesthetics in 2026 but are not researched against real competitors.

### Regulatory note

UK advertising rules (CAP Code 12.12) prohibit advertising prescription-only
medicines to the public. Botulinum toxin brand names are therefore never used in
the copy — the treatment is called "anti-wrinkle treatment" throughout, which is
what compliant UK clinics do. Keep it that way when real content goes in.

This is guidance drawn from how the rules are commonly applied, not legal
advice. A real clinic should have its copy reviewed before publication.
