(function () {
    let portfolioChartInstance = null;

    function destroyMocktradePanel() {
        if (portfolioChartInstance) {
            portfolioChartInstance.destroy();
            portfolioChartInstance = null;
        }
    }

    function formatStatus(panel, message, tone) {
        const statusBox = panel.querySelector("[data-mocktrade-status]");

        if (!statusBox) {
            return;
        }

        statusBox.textContent = message;
        statusBox.classList.remove(
            "status-message--info",
            "status-message--success",
            "status-message--warning",
            "status-message--error"
        );
        statusBox.classList.add(`status-message--${tone || "info"}`);
    }

    function initChart(panel) {
        const dataElement = panel.querySelector("#mocktrade-portfolio-chart-data");
        const assetDataElement = panel.querySelector("#mocktrade-asset-chart-data");
        const canvas = panel.querySelector("#mocktradePortfolioChart");
        const metaText = panel.querySelector("#mocktradeChartMetaText");
        const chartNote = panel.querySelector("#mocktradeChartNote");
        const overviewButton = panel.querySelector("#mocktradePortfolioOverviewBtn");
        const assetButtons = Array.from(panel.querySelectorAll(".asset-slot-button[data-item-id]"));
        const searchInput = panel.querySelector("#item_name");

        if (!dataElement || !assetDataElement || !canvas || typeof Chart === "undefined") {
            return;
        }

        const chartData = JSON.parse(dataElement.textContent);
        const assetChartData = JSON.parse(assetDataElement.textContent);
        const ctx = canvas.getContext("2d");

        destroyMocktradePanel();
        portfolioChartInstance = new Chart(ctx, {
            type: "line",
            data: { labels: [], datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "top",
                    },
                    title: {
                        display: true,
                        text: "",
                    },
                },
                scales: {
                    x: {
                        ticks: {
                            maxTicksLimit: 6,
                        },
                    },
                    y: {
                        beginAtZero: false,
                    },
                },
            },
        });

        function setSelectedAsset(itemId) {
            assetButtons.forEach((button) => {
                button.classList.toggle("is-selected", button.dataset.itemId === String(itemId));
            });
            if (overviewButton) {
                overviewButton.classList.toggle("is-active", !itemId);
            }
        }

        function renderPortfolioOverview() {
            if (!portfolioChartInstance) {
                return;
            }

            portfolioChartInstance.data.labels = chartData.labels;
            portfolioChartInstance.data.datasets = [
                {
                    label: "Cash Balance",
                    data: chartData.cash,
                    borderColor: "#2563eb",
                    backgroundColor: "rgba(37, 99, 235, 0.08)",
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.2,
                },
                {
                    label: "Asset Market Value",
                    data: chartData.asset_values,
                    borderColor: "#f97316",
                    backgroundColor: "rgba(249, 115, 22, 0.08)",
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.2,
                },
                {
                    label: "Total Account Value",
                    data: chartData.total_values,
                    borderColor: "#16a34a",
                    backgroundColor: "rgba(22, 163, 74, 0.14)",
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 2,
                    tension: 0.25,
                },
            ];
            portfolioChartInstance.options.plugins.title.text = "Portfolio Overview";
            portfolioChartInstance.update();

            if (metaText) {
                metaText.textContent = `Tracked assets: ${chartData.asset_names.join(", ")}`;
            }
            if (chartNote) {
                chartNote.textContent = "Click an asset on the left to switch the chart.";
            }
            setSelectedAsset(null);
        }

        function renderAssetChart(itemId) {
            const assetEntry = assetChartData[String(itemId)];

            if (!assetEntry || !assetEntry.labels || assetEntry.labels.length === 0 || !portfolioChartInstance) {
                return;
            }

            portfolioChartInstance.data.labels = assetEntry.labels;
            portfolioChartInstance.data.datasets = [
                {
                    label: "Price",
                    data: assetEntry.prices,
                    borderColor: "#2563eb",
                    backgroundColor: "rgba(37, 99, 235, 0.12)",
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 2,
                    tension: 0.25,
                },
                {
                    label: "Quantity",
                    data: assetEntry.quantities,
                    borderColor: "#f97316",
                    backgroundColor: "rgba(249, 115, 22, 0.08)",
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.2,
                    hidden: true,
                },
            ];
            portfolioChartInstance.options.plugins.title.text = `${assetEntry.name} Price Trend`;
            portfolioChartInstance.update();

            if (metaText) {
                metaText.textContent = `Selected asset: ${assetEntry.name}`;
            }
            if (chartNote) {
                chartNote.textContent = "Click Portfolio Overview to switch back.";
            }
            setSelectedAsset(itemId);

            if (searchInput) {
                searchInput.value = assetEntry.name;
            }
        }

        if (overviewButton) {
            overviewButton.addEventListener("click", renderPortfolioOverview);
        }

        assetButtons.forEach((button) => {
            button.addEventListener("click", () => {
                renderAssetChart(button.dataset.itemId);
            });
        });

        renderPortfolioOverview();
    }

    function initMocktradePanel(scope) {
        const panel = scope.querySelector("#home-mocktrade-panel");

        if (!panel || panel.dataset.mocktradeInitialised === "1") {
            return;
        }

        panel.dataset.mocktradeInitialised = "1";
        initChart(panel);

        const form = panel.querySelector(".trade-form");
        const priceBox = panel.querySelector("[data-mocktrade-price-box]");
        const itemInput = form ? form.querySelector("#item_name") : null;
        const formActionUrl = form ? form.getAttribute("action") : null;

        if (!form || !priceBox || !formActionUrl) {
            return;
        }

        async function runAsyncAction(action, submitter) {
            const formData = new FormData(form);
            const currentScroll = window.scrollY;

            formData.set("action", action);
            submitter.disabled = true;
            submitter.classList.add("is-loading");

            try {
                const response = await fetch(formActionUrl, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: formData,
                });

                if (!response.ok) {
                    throw new Error(`Unexpected status: ${response.status}`);
                }

                const payload = await response.json();

                if (action === "search") {
                    priceBox.textContent = payload.price || "-";
                    if (itemInput && typeof payload.item_name === "string") {
                        itemInput.value = payload.item_name;
                    }
                    formatStatus(
                        panel,
                        payload.status_message || "Latest recorded price loaded.",
                        payload.status_tone || "info"
                    );
                    return;
                }

                if (!payload.html) {
                    throw new Error("Missing HTML payload.");
                }

                if (window.homePanelController && typeof window.homePanelController.renderPanelPayload === "function") {
                    window.homePanelController.renderPanelPayload(payload, {
                        pushHistory: false,
                        scrollY: currentScroll,
                    });
                    return;
                }

                throw new Error("Home panel controller is unavailable.");
            } catch (error) {
                console.error("Mock trading request failed.", error);
                formatStatus(panel, "The request failed. Please try again.", "error");
            } finally {
                submitter.disabled = false;
                submitter.classList.remove("is-loading");
            }
        }

        form.addEventListener("submit", (event) => {
            const submitter = event.submitter;

            if (submitter && ["search", "buy", "sell"].includes(submitter.value)) {
                event.preventDefault();
                runAsyncAction(submitter.value, submitter);
            }
        });
    }

    window.destroyMocktradePanel = destroyMocktradePanel;
    window.initMocktradePanel = initMocktradePanel;

    document.addEventListener("DOMContentLoaded", () => {
        initMocktradePanel(document);
    });
})();
