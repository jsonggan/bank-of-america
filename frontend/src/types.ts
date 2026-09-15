export type Field = { name: string; type: "string" | "number"; required?: boolean };
export type Schema = { name: string; fields: Field[] };
export type ConfigView = | { type: "summary"; field: string; aggregation: "sum" } | { type: "table"; columns: string[] };
export type DashboardConfig = { name: string; schema: string; views: ConfigView[] };
