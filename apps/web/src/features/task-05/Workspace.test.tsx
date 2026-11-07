import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { ForecastWorkspace, ForecastEvaluation } from "./Workspace";

const { useForecast, useForecastResults } = vi.hoisted(() => ({
  useForecast: vi.fn(),
  useForecastResults: vi.fn(),
}));
vi.mock("../../lib/api", () => ({
  useForecast,
  useForecastResults,
  modelName: (name: string) => name,
}));
vi.mock("recharts", () => ({
  ResponsiveContainer: () => null,
  ComposedChart: () => null,
  Area: () => null,
  CartesianGrid: () => null,
  Legend: () => null,
  Line: () => null,
  ReferenceLine: () => null,
  Tooltip: () => null,
  XAxis: () => null,
  YAxis: () => null,
}));
const row = {
  target: "releases",
  group: "all",
  model: "ridge_1",
  forecast_origin: "2020-01-01",
  history: [{ period: "2020-01-01", value: 900 }],
  forecast: [{ period: "2021-01-01", predicted: 910, lower: 800, upper: 1020 }],
  band_residual_count: 10,
  test_start: "2017-01-01",
  test_end: "2020-01-01",
  test: [
    {
      period: "2017-01-01",
      actual: 100,
      predicted: 200,
      lower: 180,
      upper: 220,
    },
  ],
  test_band_coverage: 0,
  test_metrics: { mae: 100, rmse: 110, smape: 40, mase: 2, wape: 1 },
  comparison: [
    {
      model: "ridge_1",
      cv_mae: 10,
      cv_rmse: 11,
      test_metrics: { mae: 100, rmse: 110 },
      folds: [
        {
          origin: "2010-01-01",
          fit_end: "2010-01-01",
          validation_start: "2011-01-01",
          validation_end: "2012-01-01",
          mae: 10,
        },
      ],
    },
    {
      model: "last_value",
      cv_mae: 12,
      cv_rmse: 13,
      test_metrics: { mae: 20, rmse: 25 },
      folds: [],
    },
  ],
};
describe("Task 5 historical forecasting", () => {
  it("reports failure against baseline and historic projection origin", () => {
    useForecast.mockReturnValue({ data: { run_id: "test-run", series: row } });
    render(
      <MemoryRouter>
        <ForecastWorkspace />
      </MemoryRouter>,
    );
    expect(
      screen.getByText("Held-out warning: worse than last-value baseline."),
    ).toBeInTheDocument();
    expect(screen.getByText("Origin 2020")).toBeInTheDocument();
    expect(
      screen.getByText(/not a calibrated confidence interval/),
    ).toBeInTheDocument();
  });
  it("changes target and resets an incompatible horizon", async () => {
    useForecast.mockReturnValue({ data: { run_id: "test-run", series: row } });
    render(
      <MemoryRouter
        initialEntries={["/tasks/5/forecast?target=releases&horizon=3"]}
      >
        <ForecastWorkspace />
      </MemoryRouter>,
    );
    await userEvent
      .setup()
      .selectOptions(
        screen.getByRole("combobox", { name: "Time target" }),
        "additions",
      );
    expect(useForecast).toHaveBeenLastCalledWith("additions", "all", 6);
    expect(
      screen.getByRole("combobox", { name: "Forecast horizon" }),
    ).toHaveValue("6");
  });
  it("shows unavailable state without invented outputs", () => {
    useForecast.mockReturnValue({
      error: new Error("Task 5 bundle unavailable"),
      isPending: false,
    });
    render(
      <MemoryRouter>
        <ForecastWorkspace />
      </MemoryRouter>,
    );
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Task 5 bundle unavailable",
    );
    expect(
      screen.queryByRole("button", { name: "Export CSV" }),
    ).not.toBeInTheDocument();
  });
  it("does not reselect from lower test error", () => {
    useForecastResults.mockReturnValue({
      data: { run_id: "test-run", series: [row] },
    });
    render(
      <MemoryRouter>
        <ForecastEvaluation />
      </MemoryRouter>,
    );
    expect(screen.getByText("Selected by CV").closest("tr")).toHaveTextContent(
      "ridge_1",
    );
    expect(screen.getByText("last_value").closest("tr")).toHaveTextContent(
      "Comparison",
    );
  });
});
