import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../App";

const readyPayload = {
  status: "ready",
  checks: { database: true, pgvector: true, vector_dimension: true },
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2",
  embedding_dimension: 384,
};

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("application shell", () => {
  it("shows loading and then the backend ready state", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(readyPayload), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );

    expect(
      screen.getByText("Checking the learning service…"),
    ).toBeInTheDocument();
    expect(
      await screen.findByText("Learning service ready"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/384-dimension vector storage/),
    ).toBeInTheDocument();
  });

  it("offers a keyboard-accessible retry after a network failure", async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new Error("Network unavailable"))
      .mockResolvedValueOnce(
        new Response(JSON.stringify(readyPayload), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );

    expect(
      await screen.findByText("Learning service unavailable"),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Try again" }));
    await waitFor(() =>
      expect(screen.getByText("Learning service ready")).toBeInTheDocument(),
    );
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("routes to the honest scope page", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(readyPayload), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );
    await user.click(screen.getByRole("link", { name: "About" }));
    expect(
      screen.getByRole("heading", {
        name: "Upload. Learn. Ace it.",
      }),
    ).toBeVisible();
  });
});
