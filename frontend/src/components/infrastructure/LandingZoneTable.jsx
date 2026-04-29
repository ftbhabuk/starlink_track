import React from "react";

function LandingZoneTable({ data }) {
  const landingZones = [
    { zone: "LZ-1", status: "retired", firstLanding: "Dec 21, 2015", lastLanding: "Aug 1, 2025", landings: "54", note: "Falcon 9 & Heavy" },
    { zone: "LZ-2", status: "retired", firstLanding: "Feb 6, 2018", lastLanding: "Dec 9, 2025", landings: "16", note: "Falcon Heavy" }
  ];

  const newZones = [
    { zone: "LZ-3", status: "construction", note: "Cape Canaveral" },
    { zone: "LZ-4", status: "construction", note: "Vandenberg SFB" }
  ];

  return (
    <section className="infra-panel">
      <h3>Landing Zones</h3>

      <div className="lz-intro">
        <div className="intro-card">
          <div className="intro-icon">🛬</div>
          <div className="intro-content">
            <h4>Return to Launch Site</h4>
            <p>Ground-based concrete pads at Cape Canaveral and Vandenberg. Enable vertical booster landings for reusability.</p>
          </div>
        </div>
        <div className="lz-media">
          <img 
            src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Landing_Zones_1_and_2.jpg/800px-Landing_Zones_1_and_2.jpg" 
            alt="Landing Zones at Cape Canaveral"
            className="lz-image"
          />
          <iframe 
            width="100%" 
            height="140" 
            src="https://www.youtube.com/embed/ackZ-Ei4JB8?start=3" 
            title="Falcon 9 Landing at LZ-1" 
            frameBorder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowFullScreen
          />
        </div>
      </div>

      <div className="lz-grid">
        {landingZones.map((z) => (
          <div key={z.zone} className="lz-card retired">
            <div className="lz-header">
              <span className="lz-name">{z.zone}</span>
              <span className="lz-status">RETIRED</span>
            </div>
            <div className="lz-timeline">
              <div className="timeline-row">
                <span>First</span>
                <span>{z.firstLanding}</span>
              </div>
              <div className="timeline-row">
                <span>Last</span>
                <span>{z.lastLanding}</span>
              </div>
              <div className="timeline-row highlight">
                <span>Landings</span>
                <span>{z.landings}</span>
              </div>
            </div>
            <div className="lz-note">{z.note}</div>
          </div>
        ))}
        {newZones.map((z) => (
          <div key={z.zone} className="lz-card construction">
            <div className="lz-header">
              <span className="lz-name">{z.zone}</span>
              <span className="lz-status">UNDER CONSTRUCTION</span>
            </div>
            <div className="lz-note">{z.note}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default LandingZoneTable;