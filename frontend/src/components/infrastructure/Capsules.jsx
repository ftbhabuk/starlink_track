import React from "react";

function Capsules({ data }) {
  return (
    <section className="infra-panel">
      <h3>Dragon Capsules</h3>
      
      <div className="capsules-info">
        <div className="info-card">
          <div className="info-card-header">
            <span className="info-icon">∞</span>
            <h4>SpaceX Dragon Spacecraft</h4>
          </div>
          <p className="info-lead">
            Reusable spacecraft designed to transport humans and cargo to the International Space Station and other orbital destinations.
          </p>
          <div className="info-grid">
            <div className="info-col">
              <h5>Dragon 1</h5>
              <p>Original cargo variant (2010-2020). First private spacecraft to reach orbit and berth with the ISS.</p>
            </div>
            <div className="info-col">
              <h5>Dragon 2</h5>
              <p>Current generation in two configurations:</p>
              <ul className="inline-list">
                <li><span className="badge crew">Crew Dragon</span> — Astronaut transport</li>
                <li><span className="badge cargo">Cargo Dragon</span> — Supply missions</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="info-card highlight">
          <h4>Reusability</h4>
          <p>Dragon capsules are designed for multiple flights. Heat shields, avionics, and systems are refurbished between missions, significantly reducing space access costs. Each capsule has a serial number tracking its flight history.</p>
        </div>
      </div>

      <div className="data-section">
        <div className="data-header">
          <h4>Active Capsule Fleet</h4>
          <span className="data-count">{(data?.capsules || []).length} capsules</span>
        </div>
        <div className="capsule-grid">
          {(data?.capsules || []).slice(0, 6).map((capsule) => (
            <div key={capsule.capsule_id} className="capsule-card">
              <div className="capsule-header">
                <span className="capsule-serial">{capsule.capsule_id}</span>
                <span 
                  className="status-pill"
                  data-status={(capsule.status || "").toLowerCase()}
                >
                  {capsule.status || "unknown"}
                </span>
              </div>
              <div className="capsule-name">{capsule.name || capsule.capsule_id}</div>
              <div className="capsule-stats">
                <span><strong>{capsule.missions_reported ?? "—"}</strong> missions</span>
                <span><strong>{capsule.reuses_reported ?? "—"}</strong> reuses</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="achievements-section">
        <h4>Notable Firsts</h4>
        <div className="achievements-timeline">
          <div className="timeline-item">
            <span className="timeline-year">2010</span>
            <span>First private spacecraft to reach orbit</span>
          </div>
          <div className="timeline-item">
            <span className="timeline-year">2012</span>
            <span>First private spacecraft to berth with ISS</span>
          </div>
          <div className="timeline-item">
            <span className="timeline-year">2017</span>
            <span>First reflight of an orbital spacecraft</span>
          </div>
          <div className="timeline-item">
            <span className="timeline-year">2020</span>
            <span>First private spacecraft to transport humans</span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Capsules;