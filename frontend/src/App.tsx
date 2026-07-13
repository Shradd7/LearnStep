import { NavLink, Route, Routes } from "react-router-dom";

import { AboutPage } from "./pages/AboutPage";
import { HomePage } from "./pages/HomePage";
import { DemoPage } from "./pages/DemoPage";

export function App() {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <header className="site-header">
        <NavLink className="brand" to="/" aria-label="LearnStep home">
          <span className="brand__mark" aria-hidden="true">
            L
          </span>
          <span>LearnStep</span>
        </NavLink>
        <nav aria-label="Primary navigation">
          <NavLink to="/" end>
            Home
          </NavLink>
          <NavLink to="/demo">Demo</NavLink>
          <NavLink to="/about">About</NavLink>
        </nav>
      </header>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/demo" element={<DemoPage />} />
        <Route path="*" element={<HomePage />} />
      </Routes>
      <footer>
        <p>
          LearnStep · Upload. Learn. Ace it. · synthetic portfolio demonstration
        </p>
      </footer>
    </div>
  );
}
