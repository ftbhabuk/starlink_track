import React from "react";

function LandingPads({ data }) {
  return (
    <section className="infra-panel">
      <h3>Landing Pads</h3>
      <div className="infra-list">
        {/* Educational content about landing pads */}
        <div className="landing-pads-info">
          <div className="info-section">
            <h4>What are Landing Pads?</h4>
            <p>
              Landing pads are specialized ground-based facilities where SpaceX's Falcon 9 and Falcon Heavy
              first-stage boosters return for vertical landings after launching payloads into space. These
              concrete pads enable rocket reusability, significantly reducing launch costs.
            </p>
          </div>
          
          <div className="info-section">
            <h4>Landing Zone 1 (LZ-1) & Landing Zone 2 (LZ-2)</h4>
            <p>
              Located at Cape Canaveral Space Force Station in Florida, LZ-1 and LZ-2 are SpaceX's primary
              landing sites for return-to-launch-site (RTLS) missions. LZ-1 was used for the first successful
              booster landing in December 2015.
            </p>
            <div className="media-content">
              <img 
                src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Landing_Zones_1_and_2.jpg/800px-Landing_Zones_1_and_2.jpg" 
                alt="Landing Zones 1 and 2 at Cape Canaveral"
                className="info-image"
              />
              <div className="video-wrapper">
                <iframe 
                  width="100%" 
                  height="150" 
                  src="https://www.youtube.com/embed/ackZ-Ei4JB8?start=3" 
                  title="Falcon 9 Landing at LZ-1" 
                  frameBorder="0" 
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                  allowFullScreen
                ></iframe>
              </div>
            </div>
          </div>
          
          <div className="info-section">
            <h4>Actual Landing Pad Data</h4>
            <p>Current status of SpaceX landing pads:</p>
            <div className="data-list">
              {(data?.landpads || []).slice(0, 4).map((pad) => (
                <div key={pad.landpad_id} className="data-item">
                  <div>{pad.full_name || pad.name}</div>
                  <div className="mono dim">
                    {pad.landing_successes}/{pad.landing_attempts} landings 
                    ({pad.landing_success_rate ? `${pad.landing_success_rate}%` : "—"})
                  </div>
                </div>
              ))}
              {(data?.landpads || []).length > 4 && (
                <div className="data-item">
                  <div>And {(data.landpads || []).length - 4} more...</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default LandingPads;