<style>
  :root {
    --matrix-green: #39d353;
    --matrix-dark-green: #0d3d20;
    --matrix-black: #0a0e27;
    --matrix-gray: #1a1f3a;
    --matrix-dim: #1f7a3d;
  }

  body {
    background-color: var(--matrix-black);
    color: var(--matrix-green);
    font-family: 'JetBrains Mono', 'Courier New', Consolas, monospace;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
  }

  /* Subtle code rain background */
  @keyframes rain {
    0% { transform: translateY(-100%); opacity: 0; }
    10% { opacity: 0.02; }
    90% { opacity: 0.02; }
    100% { transform: translateY(100vh); opacity: 0; }
  }

  #code-rain {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
  }

  .rain-char {
    position: absolute;
    font-size: 12px;
    opacity: 0;
    animation: rain linear infinite;
    color: var(--matrix-dim);
  }

  .content {
    position: relative;
    z-index: 1;
    max-width: 1200px;
    margin: 0 auto;
  }

  /* Loading sequence */
  .system-init {
    text-align: center;
    margin: 60px 0;
    font-size: 14px;
    letter-spacing: 2px;
  }

  .init-line {
    margin: 12px 0;
    opacity: 0;
    animation: fadeIn 0.6s ease-out forwards;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .progress-bar {
    width: 200px;
    height: 4px;
    border: 1px solid var(--matrix-green);
    margin: 20px auto;
    background: linear-gradient(90deg, var(--matrix-green) 0%, var(--matrix-green) 100%);
    animation: progress 3s ease-in-out forwards;
  }

  @keyframes progress {
    0% { width: 0; }
    100% { width: 200px; }
  }

  /* Hero section */
  .hero {
    text-align: center;
    margin: 80px 0;
  }

  .hero img {
    max-width: 100%;
    height: auto;
    margin: 0 auto;
  }

  /* Status panel */
  .status-panel {
    border: 1px solid var(--matrix-dim);
    padding: 20px;
    margin: 40px auto;
    max-width: 400px;
    font-size: 13px;
    line-height: 1.8;
  }

  .status-line {
    margin: 8px 0;
  }

  .status-label {
    opacity: 0.6;
  }

  .status-value {
    opacity: 1;
    margin-left: 10px;
  }

  /* Divider */
  .divider {
    text-align: center;
    margin: 60px 0;
    opacity: 0.4;
    letter-spacing: 4px;
  }

  /* Section headers */
  .section-header {
    border-left: 2px solid var(--matrix-green);
    padding-left: 10px;
    margin: 60px 0 30px 0;
    font-size: 14px;
    letter-spacing: 2px;
    opacity: 0.8;
  }

  /* Content sections */
  .content-section {
    margin: 40px 0;
    line-height: 1.8;
    font-size: 13px;
  }

  .content-section p {
    margin: 12px 0;
    opacity: 0.9;
  }

  .tech-stack {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin: 20px 0;
  }

  .tech-item {
    border: 1px solid var(--matrix-dim);
    padding: 6px 12px;
    font-size: 12px;
    opacity: 0.7;
  }

  /* Project cards */
  .projects {
    display: grid;
    gap: 20px;
    margin: 30px 0;
  }

  .project {
    border: 1px solid var(--matrix-dim);
    padding: 20px;
    opacity: 0.8;
  }

  .project-title {
    font-weight: bold;
    margin-bottom: 8px;
    opacity: 1;
  }

  .project-desc {
    font-size: 12px;
    line-height: 1.6;
    opacity: 0.7;
  }

  /* Minimal footer */
  .footer {
    text-align: center;
    margin-top: 80px;
    opacity: 0.5;
    font-size: 12px;
  }

  /* Soft scanline effect */
  @keyframes scanlines {
    0% { transform: translateY(0); }
    100% { transform: translateY(4px); }
  }

  .scanlines {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background: repeating-linear-gradient(
      0deg,
      rgba(0, 0, 0, 0.15),
      rgba(0, 0, 0, 0.15) 1px,
      transparent 1px,
      transparent 2px
    );
    animation: scanlines 8s linear infinite;
    z-index: 2;
  }
</style>

<div id="code-rain"></div>
<div class="scanlines"></div>

<div class="content">

<!-- LOADING SEQUENCE -->
<div class="system-init">
  <div class="init-line" style="animation-delay: 0.2s;">SYSTEM INITIALIZING...</div>
  <div class="init-line" style="animation-delay: 0.8s;">Loading modules...</div>
  <div class="init-line" style="animation-delay: 1.4s;">Identity confirmed...</div>
  <div class="progress-bar" style="animation-delay: 1.8s;"></div>
  <div class="init-line" style="animation-delay: 5s;">CONNECTION ESTABLISHED</div>
</div>

<div class="divider" style="animation-delay: 5.5s;">█</div>

<!-- HERO: IBM TERMINAL -->
<div class="hero">
  <a href="#"><img src="https://raw.githubusercontent.com/agentred1999/agentred1999/main/assets/ibm-terminal.svg" alt="IBM PC/AT terminal" width="700"/></a>
</div>

<!-- STATUS PANEL -->
<div class="status-panel">
  <div class="status-line">
    <span class="status-label">NAME</span>
    <span class="status-value">Richard Dean</span>
  </div>
  <div class="status-line">
    <span class="status-label">ROLE</span>
    <span class="status-value">Software Developer</span>
  </div>
  <div class="status-line">
    <span class="status-label">STATUS</span>
    <span class="status-value">ONLINE</span>
  </div>
  <div class="status-line">
    <span class="status-label">LOCATION</span>
    <span class="status-value">Houston, Texas</span>
  </div>
  <div class="status-line">
    <span class="status-label">CURRENT PROJECT</span>
    <span class="status-value">1337 Wing</span>
  </div>
</div>

<div class="divider">────</div>

<!-- ABOUT SECTION -->
<div class="section-header">ABOUT</div>
<div class="content-section">
I build practical, user-facing software — from AI-powered web apps to real cybersecurity hardware. Based in Houston, I work with a terminal-first, Linux-native workflow. Most of what I ship goes through the same loop: build it, break it, fix it, ship it.
</div>

<div class="content-section">
- Full-stack development — Next.js, React, TypeScript, Firebase, Redux<br>
- Daily Ubuntu user — scripting, automation, self-hosting, terminal-first workflow<br>
- Founder of 1337 Wing — cybersecurity-themed pentesting hardware & merch<br>
- Mesh networking / Meshtastic tinkerer<br>
- Currently exploring AI-powered tooling and agentic dev workflows
</div>

<div class="divider">────</div>

<!-- TECH STACK -->
<div class="section-header">TECH STACK</div>
<div class="tech-stack">
  <div class="tech-item">Next.js</div>
  <div class="tech-item">React</div>
  <div class="tech-item">TypeScript</div>
  <div class="tech-item">Node.js</div>
  <div class="tech-item">Python</div>
  <div class="tech-item">Firebase</div>
  <div class="tech-item">Linux</div>
  <div class="tech-item">Docker</div>
  <div class="tech-item">Git</div>
</div>

<div class="divider">────</div>

<!-- FEATURED PROJECTS -->
<div class="section-header">FEATURED PROJECTS</div>
<div class="projects">
  <div class="project">
    <div class="project-title">🧴 Skinstric AI Clone (skin-ai)</div>
    <div class="project-desc">Next.js 15 / TypeScript rebuild of an AI skincare analysis flow — camera capture, gallery upload, live API-driven demographic analysis, full mobile-responsive UI.</div>
  </div>
  <div class="project">
    <div class="project-title">📚 Summarist</div>
    <div class="project-desc">Blinkist-style book summary app — Next.js App Router, Firebase Auth, Firestore, Redux Toolkit, and Stripe subscriptions end-to-end.</div>
  </div>
  <div class="project">
    <div class="project-title">🔐 1337 Wing</div>
    <div class="project-desc">A real cybersecurity brand I founded — pentesting hardware and hacker merch, with a full React/Vite storefront including a live HackerNews intel feed.</div>
  </div>
  <div class="project">
    <div class="project-title">🖼 NFT Marketplace</div>
    <div class="project-desc">React app built against a Firebase Cloud Functions API — dynamic carousels, countdown timers, localStorage-backed follow state, deployed on GitHub Pages.</div>
  </div>
</div>

<div class="divider">────</div>

<div class="footer">
  There is an entire world underneath this interface.
</div>

</div>

<script>
// Generate subtle code rain background
const codeRain = document.getElementById('code-rain');
const chars = '01アイウエオカキクケコ';
const container = codeRain;

for (let i = 0; i < 15; i++) {
  const char = chars[Math.floor(Math.random() * chars.length)];
  const span = document.createElement('span');
  span.className = 'rain-char';
  span.textContent = char;
  span.style.left = Math.random() * 100 + '%';
  span.style.animationDuration = (Math.random() * 10 + 10) + 's';
  span.style.animationDelay = Math.random() * 5 + 's';
  container.appendChild(span);
}
</script>

