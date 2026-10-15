import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import Home from "./page";

test("home renders inside the app shell", () => {
  render(<Home />);
  expect(screen.getByRole("heading", { level: 1 })).toBeDefined();
  expect(screen.getByRole("navigation", { name: "Primary" })).toBeDefined();
});
