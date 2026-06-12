import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import StatsCard from "./StatsCard.jsx";

test("renders metric label and value", () => {
  render(<StatsCard label="Files processed" value="8" />);

  expect(screen.getByText("Files processed")).toBeInTheDocument();
  expect(screen.getByText("8")).toBeInTheDocument();
});
