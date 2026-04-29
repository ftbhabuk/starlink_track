import React from "react";

function DroneShipTable({ data }) {
  const droneShips = [
    { id: "JRTI", name: "Just Read The Instructions (I)", homePort: "N/A", status: "scrapped" },
    { id: "OCISLY", name: "Of Course I Still Love You", homePort: "Long Beach", status: "active" },
    { id: "JRTI-II", name: "Just Read The Instructions (II)", homePort: "Port Canaveral", status: "active" },
    { id: "ASOG", name: "A Shortfall of Gravitas", homePort: "Port Canaveral", status: "active" }
  ];

  return (
    <section className="infra-panel">
      <h3>Autonomous Droneships</h3>

      <div className="droneship-intro">
        <div className="intro-card">
          <div className="intro-icon">⚓</div>
          <div className="intro-content">
            <h4>ASDS — Autonomous Spaceport Drone Ships</h4>
            <p>Seagoing mobile landing platforms for Falcon boosters. Enable landings for missions without enough fuel to return to launch site.</p>
          </div>
        </div>
        <div className="media-content">
          <iframe 
            width="100%" 
            height="160" 
            src="https://www.youtube.com/embed/sYmQQn_ZSys" 
            title="Falcon 9 Landing on Droneship" 
            frameBorder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowFullScreen
          />
        </div>
      </div>

      <div className="droneship-grid">
        {droneShips.map((ship) => (
          <div key={ship.id} className="droneship-card" data-active={ship.status === "active"}>
            <div className="droneship-header">
              <span className="droneship-id">{ship.id}</span>
              <span className={`status-indicator ${ship.status}`} />
            </div>
            <div className="droneship-name">{ship.name}</div>
            <div className="droneship-meta">
              <span className="meta-label">Home Port</span>
              <span className="meta-value">{ship.homePort}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default DroneShipTable;