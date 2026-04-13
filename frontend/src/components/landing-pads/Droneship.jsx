import React from "react";

function Droneship({ data }) {
  return (
    <section className="infra-panel">
      <h3>Droneships (ASDS)</h3>
      <div className="infra-list">
        {/* Educational content about droneships */}
        <div className="droneship-info">
          <div className="info-section">
            <h4>What are Autonomous Spaceport Drone Ships?</h4>
            <p>
              Autonomous Spaceport Drone Ships (ASDS) are seagoing vessels that serve as mobile landing 
              platforms for SpaceX's Falcon 9 and Falcon Heavy boosters. These ships enable landings for 
              missions that don't have enough fuel to return to the launch site, such as geostationary 
              transfers or high-inclination orbits.
            </p>
          </div>
          
          <div className="info-section">
            <h4>ASDS Fleet & Operations</h4>
            <p>
              SpaceX operates several droneships including "Just Read the Instructions" (JRTI) in 
              California, "A Shortfall of Gravitas" (ASOG) and "Of Course I Still Love You" (OCISLY) in 
              the Atlantic. These ships are equipped with thrusters to maintain position and capture 
              landing boosters.
            </p>
            <div className="media-content">
              <div className="video-wrapper">
                <iframe 
                  width="100%" 
                  height="150" 
                  src="https://www.youtube.com/embed/sYmQQn_ZSys" 
                  title="Falcon 9 Landing on Droneship" 
                  frameBorder="0" 
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                  allowFullScreen
                ></iframe>
              </div>
            </div>
          </div>
          
          <div className="info-section">
            <h4>Current Droneship Status</h4>
            <p>Status of SpaceX's autonomous drone ships:</p>
            <div className="data-list">
              {(data?.droneships || []).slice(0, 4).map((ship) => (
                <div key={ship.ship_id} className="data-item">
                  <div>{ship.name || "Unknown ship"}</div>
                  <div className="mono dim">
                    {ship.active ? "Active" : "Inactive"} · {ship.year_built || "—"}
                  </div>
                </div>
              ))}
              {(data?.droneships || []).length > 4 && (
                <div className="data-item">
                  <div>And {(data.droneships || []).length - 4} more...</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Droneship;