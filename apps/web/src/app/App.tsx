import { ProjectMetadata } from "./ProjectMetadata";
import { useSectionNavigation } from "./useSectionNavigation";
import { useWorkspaceMotion } from "./useWorkspaceMotion";
import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
  Link,
} from "react-router";
import { DatasetPage } from "../components/Dataset";
import {
  ForecastOverview,
  ForecastWorkspace,
  ForecastEvaluation,
  ForecastMethodology,
} from "../features/task-05/Workspace";

export function App() {
  const location = useLocation();
  const sectionNavRef = useSectionNavigation(location.pathname);
  const mainRef = useWorkspaceMotion(location.pathname);
  return (
    <>
      <ProjectMetadata />
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <header className="masthead">
        <Link
          className="brand"
          to="/overview"
          aria-label="Netflix Trend Forecasting home"
        >
          <span className="brand-mark" aria-hidden="true">
            <img src="/logo.svg?v=2" width="64" height="64" alt="" />
          </span>
          <span>
            TREND FORECASTING<small>NETFLIX / HISTORICAL TIME SERIES</small>
          </span>
        </Link>
        <div className="masthead-meta">
          <strong>INDEPENDENT ML PROJECT</strong>
          <span>CATALOG SNAPSHOT / 25 SEP 2021</span>
        </div>
      </header>
      <div className="workspace">
        <nav
          ref={sectionNavRef}
          className="section-nav"
          aria-label="Project sections"
        >
          {[
            ["overview", "Overview"],
            ["dataset", "About Dataset"],
            ["forecast", "Forecast"],
            ["evaluation", "Evaluation"],
            ["methodology", "Methodology"],
          ].map(([path, label], i) => (
            <NavLink key={path} to={`/${path}${location.search}`}>
              <small aria-hidden="true">{String(i + 1).padStart(2, "0")}</small>
              {label}
            </NavLink>
          ))}
        </nav>
        <main
          ref={mainRef}
          id="main"
          tabIndex={-1}
          key={location.pathname}
          className="page-enter"
        >
          <Routes>
            <Route path="/" element={<Navigate to="/overview" replace />} />
            <Route path="/dataset" element={<DatasetPage />} />
            <Route path="/overview" element={<ForecastOverview />} />
            <Route path="/forecast" element={<ForecastWorkspace />} />
            <Route path="/evaluation" element={<ForecastEvaluation />} />
            <Route path="/methodology" element={<ForecastMethodology />} />
            <Route
              path="*"
              element={
                <div className="not-found">
                  <p className="eyebrow">404 / UNKNOWN SECTION</p>
                  <h1>Page not found</h1>
                  <Link to="/overview">Return to project</Link>
                </div>
              }
            />
          </Routes>
        </main>
        <footer>
          <span>Netflix / Trend Forecasting</span>
          <span>
            Independent portfolio project. Not affiliated with Netflix.
          </span>
          <Link className="footer-index" to="/dataset">
            Dataset &amp; decisions
          </Link>
        </footer>
      </div>
    </>
  );
}
