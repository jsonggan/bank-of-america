import tradeSchema from "../../examples/trade-schema.json";
import tradeRows from "../../examples/trade-rows.json";
import tradeDashboard from "../../examples/trade-dashboard.json";
import customerSchema from "../../examples/customer-schema.json";
import customerRows from "../../examples/customer-rows.json";
import customerDashboard from "../../examples/customer-dashboard.json";
import type { DashboardConfig, Schema } from "./types";
export const examples = { trade: { schema: tradeSchema as Schema, rows: tradeRows, dashboard: tradeDashboard as DashboardConfig }, customer: { schema: customerSchema as Schema, rows: customerRows, dashboard: customerDashboard as DashboardConfig } };
export const pretty = (value: unknown) => JSON.stringify(value, null, 2);
