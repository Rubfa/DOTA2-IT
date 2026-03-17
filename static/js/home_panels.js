(function () {
    function initHomePanels() {
        const homeLower = document.getElementById("home-lower");
        const tabs = document.getElementById("home-panel-tabs");
        const switchContent = document.getElementById("home-switch-content");

        if (!homeLower || !tabs || !switchContent) {
            return;
        }

        let requestToken = 0;

        function updateActiveTab(panel) {
            tabs.querySelectorAll(".tab").forEach((tab) => {
                tab.classList.toggle("active", tab.dataset.panel === panel);
            });
        }

        function initialiseDynamicPanel(panel) {
            if (panel === "messageboard" && typeof window.initMessageboardUI === "function") {
                window.initMessageboardUI(switchContent);
            }

            if (panel === "mocktrade" && typeof window.initMocktradePanel === "function") {
                window.initMocktradePanel(switchContent);
            }
        }

        function destroyDynamicPanel() {
            if (typeof window.destroyMocktradePanel === "function") {
                window.destroyMocktradePanel();
            }
        }

        function renderPanelPayload(payload, options) {
            const settings = options || {};
            const resolvedPanel = payload.panel || switchContent.dataset.currentPanel || "messageboard";

            destroyDynamicPanel();
            switchContent.innerHTML = (payload.html || "").trim();
            switchContent.dataset.currentPanel = resolvedPanel;
            updateActiveTab(resolvedPanel);
            initialiseDynamicPanel(resolvedPanel);

            if (typeof settings.scrollY === "number") {
                window.requestAnimationFrame(() => {
                    window.scrollTo(0, settings.scrollY);
                });
            }

            if (settings.pushHistory) {
                const nextUrl = new URL(settings.targetUrl || window.location.href, window.location.origin);
                nextUrl.searchParams.set("panel", resolvedPanel);
                nextUrl.hash = "home-lower";
                window.history.pushState({ panel: resolvedPanel }, "", nextUrl.toString());
            }
        }

        async function loadPanel(targetUrl, options) {
            const settings = options || {};
            const pushHistory = settings.pushHistory !== false;
            const fetchUrl = new URL(targetUrl, window.location.origin);
            const currentToken = ++requestToken;

            fetchUrl.hash = "";
            switchContent.classList.add("is-loading");

            try {
                const response = await fetch(fetchUrl.toString(), {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                    },
                });

                if (!response.ok) {
                    throw new Error(`Unexpected status: ${response.status}`);
                }

                const payload = await response.json();

                if (!payload.html) {
                    throw new Error("Missing panel HTML.");
                }

                if (currentToken !== requestToken) {
                    return;
                }

                renderPanelPayload(payload, {
                    pushHistory: pushHistory,
                    targetUrl: fetchUrl.toString(),
                });
            } catch (error) {
                console.error("Home panel request failed.", error);
                window.location.href = targetUrl;
            } finally {
                switchContent.classList.remove("is-loading");
            }
        }

        window.homePanelController = {
            loadPanel: loadPanel,
            renderPanelPayload: renderPanelPayload,
            getCurrentPanel: function () {
                return switchContent.dataset.currentPanel || "messageboard";
            },
        };

        tabs.addEventListener("click", (event) => {
            const tab = event.target.closest(".tab[data-panel]");

            if (!tab) {
                return;
            }

            event.preventDefault();
            loadPanel(tab.href);
        });

        window.addEventListener("popstate", () => {
            loadPanel(window.location.href, { pushHistory: false });
        });

        initialiseDynamicPanel(switchContent.dataset.currentPanel || "messageboard");
    }

    document.addEventListener("DOMContentLoaded", initHomePanels);
})();
