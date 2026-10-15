import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import Home from "./page";

test("landing page offers sign-up and sign-in", () => {
  render(<Home />);
  expect(screen.getByRole("heading", { level: 1 }).textContent).toContain("executive team");
  expect(screen.getByRole("link", { name: "Get started" }).getAttribute("href")).toBe("/sign-up");
  expect(screen.getByRole("link", { name: "Sign in" }).getAttribute("href")).toBe("/sign-in");
});
