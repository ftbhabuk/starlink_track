import { useState } from "react";

const DRAGON_BOOSTER_IMAGE = "https://wallpaperaccess.com/full/1094574.jpg";
const HERO_SPACEX_IMAGE = "https://wallpaperaccess.com/full/1094610.jpg";
const STARLINK_IMAGE_WEB = "https://images.hdqwalls.com/download/starlink-fe-2048x2048.jpg";
const FALCON_FLEET_IMAGE = "https://wallpaperaccess.com/full/1094566.jpg";
const STARSHIP_IMAGE_WEB = "https://wallpaperaccess.com/full/1094611.jpg";

function num(v) {
  return v == null ? "—" : v.toLocaleString();
}

function pct(v) {
  return v == null ? "—" : `${v}%`;
}

function dateOnly(v) {
  return v ? v.slice(0, 10) : "—";
}

export default function HomeLanding({
  stats,
  rocketStats,
  boosterIntel,
  loading,
  onOpenBoosters,
  onOpenStarlink,
}) {
  const launches = rocketStats?.overall?.total_launches;
  const landings = rocketStats?.overall?.booster_landings;
  const reuse = rocketStats?.overall?.reusability_rate;
  const boosters = boosterIntel?.overall?.total_boosters;
  const maxReuse = boosterIntel?.overall?.max_reuse_count;
  const capsules = boosterIntel?.overall?.total_capsules;
  const activeStarlink = stats?.active;
  const totalSatellites = stats?.total;

  const recent = rocketStats?.recent_launches || [];
  const upcoming = rocketStats?.upcoming_launches || [];
  const launchesSource = rocketStats?.data_sources?.launches_list?.source || "unknown";
  const upcomingSource = rocketStats?.data_sources?.upcoming_launches?.source || "unknown";

  const images = {
    hero: HERO_SPACEX_IMAGE,
    falcon9: FALCON_FLEET_IMAGE,
    falconheavy: FALCON_FLEET_IMAGE,
    dragon: DRAGON_BOOSTER_IMAGE,
    starship: STARSHIP_IMAGE_WEB,
    starlink: STARLINK_IMAGE_WEB,
  };

  const quickStats = [
    { label: "Falcon 9 Launches", value: num(launches) },
    { label: "Booster Landings", value: num(landings) },
    { label: "Booster Reuse", value: pct(reuse) },
    { label: "Active Starlink", value: num(activeStarlink) },
  ];

  const starterFlow = [
    {
      badge: "[STARLINK]",
      title: "Starlink Constellation",
      text: "Live constellation tracking with status filters, orbit shell grouping, and searchable satellite records.",
      metric: `${num(totalSatellites)} tracked · ${num(activeStarlink)} active`,
      action: onOpenStarlink,
      actionLabel: "Open Starlink",
      image: images.starlink,
    },
    {
      badge: "[FALCON]",
      title: "Falcon Booster Fleet",
      text: "Core-level booster tracking focused on reuse depth, landing outcomes, and current fleet status.",
      metric: `${num(boosters)} boosters · Max reuse ${num(maxReuse)}`,
      action: onOpenBoosters,
      actionLabel: "Open Boosters",
      image: images.falconheavy,
    },
    {
      badge: "[DRAGON]",
      title: "Dragon Vehicle",
      text: "Crew and cargo spacecraft profile with capsule tracking context connected to current mission operations.",
      metric: `${num(capsules)} capsules tracked`,
      action: null,
      actionLabel: "",
      image: images.dragon,
    },
    {
      badge: "[STARSHIP]",
      title: "Starship Program",
      text: "Heavy-lift development overview for next-generation missions, integrated into the same launch context view.",
      metric: "Next-gen heavy lift context",
      action: null,
      actionLabel: "",
      image: images.starship,
    },
  ];

  return (
    <section className="home-landing">
      <div className="hero hero-z reveal-up">
        <div className="hero-copy">
          <p className="kicker">Mission Orientation</p>
          <h2>Get In Sync With The Current SpaceX Fleet State.</h2>
          <p className="hero-sub">
            This platform tracks Falcon booster performance and Starlink constellation state,
            with Dragon and Starship context in the same view.
          </p>
          <div className="hero-actions">
            <button className="cta-btn" onClick={onOpenBoosters}>Start With Boosters</button>
            <button className="ghost-btn" onClick={onOpenStarlink}>Start With Starlink</button>
          </div>
        </div>

        <div className="hero-orbit-card">
          <SmartImage
            className="hero-orbit-image"
            srcs={[images.hero, images.falcon9, DRAGON_BOOSTER_IMAGE]}
            alt="SpaceX"
          />
          <div className="hero-orbit-overlay">
            {quickStats.map((item) => (
              <div key={item.label} className="orbit-stat">
                <div className="orbit-stat-value">{loading ? "..." : item.value}</div>
                <div className="orbit-stat-label">{item.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="starter-z-grid">
        {starterFlow.map((item, idx) => (
          <article key={item.title} className={`starter-z-panel reveal-up delay-${idx + 1} ${idx % 2 === 1 ? "reverse" : ""}`}>
            <div className="starter-z-media">
              <SmartImage
                srcs={[item.image, images.starlink, images.starship, DRAGON_BOOSTER_IMAGE]}
                alt={item.title}
              />
            </div>
            <div className="starter-z-copy">
              <p className="kicker">{item.badge}</p>
              <h3>{item.title}</h3>
              <p>{item.text}</p>
              <div className="starter-z-metric mono">{item.metric}</div>
              {item.action && (
                <button className="ghost-btn" onClick={item.action}>{item.actionLabel}</button>
              )}
            </div>
          </article>
        ))}
      </div>

      <div className="infra-grid home-grid reveal-up delay-2">
        <section className="infra-panel">
          <h3>Latest Launches</h3>
          <div className="source-note">
            <span className="mono">Source: {launchesSource}</span>
          </div>
          <div className="infra-list">
            {recent.slice(0, 6).map((l) => (
              <div key={`${l.name}-${l.date_utc}`} className="infra-item">
                {l.image_url && (
                  <img className="launch-thumb" src={l.image_url} alt={l.name || "Launch"} loading="lazy" />
                )}
                <div className="name-cell">{l.name}</div>
                <div className="mono dim">
                  {dateOnly(l.date_utc)} · {l.rocket_name || "Unknown rocket"} · {l.success ? "Success" : "Failure/Unknown"}
                </div>
                {l.site_summary && <div className="home-summary">{l.site_summary}</div>}
                {l.site_url && (
                  <a className="home-link mono" href={l.site_url} target="_blank" rel="noreferrer">
                    Launch Page
                  </a>
                )}
              </div>
            ))}
          </div>
        </section>

        <section className="infra-panel">
          <h3>Next Launches</h3>
          <div className="source-note">
            <span className="mono">Source: {upcomingSource}</span>
          </div>
          <div className="infra-list">
            {upcoming.slice(0, 5).map((l) => (
              <div key={`${l.name}-${l.date_utc}`} className="infra-item">
                {l.image_url && (
                  <img className="launch-thumb" src={l.image_url} alt={l.name || "Launch"} loading="lazy" />
                )}
                <div className="name-cell">{l.name}</div>
                <div className="mono dim">
                  {dateOnly(l.date_utc)} · {l.rocket_name || "Unknown rocket"}
                </div>
                {l.site_summary && <div className="home-summary">{l.site_summary}</div>}
                {l.site_url && (
                  <a className="home-link mono" href={l.site_url} target="_blank" rel="noreferrer">
                    Mission Details
                  </a>
                )}
              </div>
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}

function SmartImage({ srcs, alt, className = "" }) {
  const filtered = (srcs || []).filter(Boolean);
  const [index, setIndex] = useState(0);
  const current = filtered[index] || DRAGON_BOOSTER_IMAGE;

  return (
    <img
      className={className}
      src={current}
      alt={alt}
      loading="lazy"
      onError={() => {
        if (index < filtered.length - 1) setIndex(index + 1);
      }}
    />
  );
}
