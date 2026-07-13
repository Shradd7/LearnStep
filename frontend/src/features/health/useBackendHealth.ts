import { useCallback, useEffect, useRef, useState } from "react";

import { getBackendReadiness } from "../../api/health";
import type { HealthViewState } from "../../types/health";

export function useBackendHealth(): {
  state: HealthViewState;
  retry: () => void;
} {
  const [state, setState] = useState<HealthViewState>({ phase: "loading" });
  const activeController = useRef<AbortController | null>(null);

  const retry = useCallback(() => {
    activeController.current?.abort();
    const controller = new AbortController();
    activeController.current = controller;
    setState({ phase: "loading" });
    void getBackendReadiness(controller.signal)
      .then((health) => {
        if (!controller.signal.aborted) {
          setState(
            health.status === "ready"
              ? { phase: "ready", health }
              : { phase: "unavailable", health },
          );
        }
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setState({
            phase: "error",
            message:
              error instanceof Error
                ? error.message
                : "The backend could not be reached.",
          });
        }
      });
  }, []);

  useEffect(() => {
    retry();
    return () => activeController.current?.abort();
  }, [retry]);

  return { state, retry };
}
