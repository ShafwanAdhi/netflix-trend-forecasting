# Data visualization

The interface uses neutral surfaces, typography and structural borders. Color identifies data categories, series and magnitude. Text, symbols and values complement color throughout the workspace.

| Data | Encoding | Additional cue |
| --- | --- | --- |
| Observations | Blue solid line | Observed label and historical periods |
| Forecasts | Orange dashed line | Forecast label and historical fitting origin |
| Empirical error band | Separate orange area | Explicit CV-error-band legend and documented coverage limitations |

The palette is defined in `apps/web/src/lib/dataColors.ts`; presentation rules live in `apps/web/src/data-visualization.css`. About Dataset uses text and tables for variables and row accounting. Methodology uses neutral workflow steps. Charts retain labelled axes, legends or tooltips; data tables scroll within their own region.

## Interpretation and accessibility

Forecast bands are pooled CV-error bands, not calibrated confidence intervals. Distinguishing observations from projections does not establish predictive quality; held-out errors and baseline comparisons remain visible.

Reduced motion, keyboard navigation, focus indicators, error states and responsive layout remain part of the chart interactions. Color styling does not modify input data, model selection, predictions or saved results.

## Verification

`scripts/browser-check-data-colors.js` inspects the rendered charts and relevant interactions. Run it against a built application preview on port 8000 using Playwright CLI. [Recorded production checks](../../verification/production/data-color-result.json) and [verification guidance](../VERIFICATION.md) identify the checked run and source revision.
