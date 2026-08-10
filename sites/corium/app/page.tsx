import SiteNav from "@/components/SiteNav";
import Hero from "@/components/Hero";
import Accreditations from "@/components/Accreditations";
import Treatments from "@/components/Treatments";
import Approach from "@/components/Approach";
import Pathway from "@/components/Pathway";
import Clinician from "@/components/Clinician";
import EnquiryForm from "@/components/EnquiryForm";
import SiteFooter from "@/components/SiteFooter";
import Reveal from "@/components/Reveal";

export default function Page() {
  return (
    <>
      <SiteNav />

      <main id="main">
        <Hero />
        <Accreditations />
        <Treatments />
        <Approach />
        <Pathway />

        <hr className="rule" />
        <Clinician />

        <section className="enq" id="enquire">
          <div className="shell band">
            <div className="enq-grid">
              <Reveal>
                <p className="eyebrow">Enquire</p>
                <h2 className="display-lg head-title">
                  Start with a conversation
                </h2>
                <p className="lede" style={{ marginTop: "24px" }}>
                  Consultations are £50 and last forty-five minutes. That fee
                  comes off the cost of treatment if you decide to go ahead, and
                  stands as the price of an honest opinion if you do not.
                </p>

                <ul className="enq-aside-list">
                  <li className="enq-aside-item">
                    <p className="datum">Reply time</p>
                    <p style={{ marginTop: "4px" }}>
                      One working day, from the clinician
                    </p>
                  </li>
                  <li className="enq-aside-item">
                    <p className="datum">Earliest treatment</p>
                    <p style={{ marginTop: "4px" }}>
                      Fourteen days after consultation
                    </p>
                  </li>
                  <li className="enq-aside-item">
                    <p className="datum">Where</p>
                    <p style={{ marginTop: "4px" }}>
                      14a Margaret&rsquo;s Buildings, Bath BA1 2LP
                    </p>
                  </li>
                </ul>
              </Reveal>

              <Reveal delay={80}>
                <EnquiryForm />
              </Reveal>
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </>
  );
}
