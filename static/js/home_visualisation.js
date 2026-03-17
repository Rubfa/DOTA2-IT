(function () {
    let visualisationChart = null;

    function destroyHomeVisualisation() {
        if (visualisationChart) {
            visualisationChart.destroy();
            visualisationChart = null;
        }
    }

    function setFeedback(root, message, tone) {
        const feedback = root.querySelector("[data-hv-feedback]");

        if (!feedback) {
            return;
        }

        feedback.textContent = message;
        feedback.classList.remove(
            "hv-feedback--success",
            "hv-feedback--warning",
            "hv-feedback--error"
        );

        if (tone && tone !== "info") {
            feedback.classList.add(`hv-feedback--${tone}`);
        }
    }

    function initHomeVisualisation() {
        const root = document.querySelector("[data-home-visualisation]");
        const searchItemsElement = document.getElementById("home-visualization-search-items");

        if (!root || !searchItemsElement || root.dataset.visualisationInitialised === "1") {
            return;
        }

        root.dataset.visualisationInitialised = "1";

        const searchItems = JSON.parse(searchItemsElement.textContent);
        const searchInput = root.querySelector("#hvSearchHero");
        const searchResults = root.querySelector("#hvSearchResults");
        const heroCards = Array.from(root.querySelectorAll(".hv-hero-card"));
        const filterButtons = Array.from(root.querySelectorAll("[data-hv-hero-type]"));
        const timeButtons = Array.from(root.querySelectorAll("[data-hv-time-range]"));
        const chartTypeButtons = Array.from(root.querySelectorAll("[data-hv-chart-type]"));
        const selectedList = root.querySelector("#hvSelectedList");
        const popupHost = root.querySelector("#hvPopup");
        const chartCaption = root.querySelector("[data-hv-chart-caption]");
        const canvas = root.querySelector("#hvChart");
        let requestToken = 0;

        if (!searchInput || !searchResults || !selectedList || !popupHost || !chartCaption || !canvas) {
            return;
        }

        const state = {
            currentItemId: null,
            currentTimeRange: "365d",
            currentChartType: "time-price",
            currentItemLabel: "",
            selectedItems: [],
            currentHeroType: "All",
            currentHeroId: null,
        };

        function normalizeText(value) {
            return String(value || "").toLowerCase();
        }

        function getCosmeticsForHero(heroId) {
            return searchItems.filter((item) => String(item.hero_id) === String(heroId));
        }

        function setActiveButtons(buttons, datasetName, activeValue) {
            buttons.forEach((button) => {
                button.classList.toggle("is-active", button.dataset[datasetName] === String(activeValue));
            });
        }

        function updateHeroSelection(heroId) {
            heroCards.forEach((card) => {
                card.classList.toggle("is-selected", card.dataset.heroId === String(heroId));
            });
        }

        function applyHeroFilters() {
            const query = normalizeText(searchInput.value);

            heroCards.forEach((card) => {
                const heroId = card.dataset.heroId;
                const heroName = card.dataset.heroName;
                const heroType = card.dataset.heroType;
                const matchesType = state.currentHeroType === "All" || heroType === state.currentHeroType;
                const matchesHeroName = normalizeText(heroName).includes(query);
                const matchesCosmeticName = searchItems.some((item) => (
                    String(item.hero_id) === String(heroId) &&
                    (
                        normalizeText(item.name).includes(query) ||
                        normalizeText(item.hero_name).includes(query)
                    )
                ));
                const isVisible = !query ? matchesType : (matchesType && (matchesHeroName || matchesCosmeticName));

                card.classList.toggle("is-hidden", !isVisible);
            });
        }

        function renderSearchResults(query) {
            searchResults.innerHTML = "";

            if (!query) {
                return;
            }

            const matches = searchItems
                .filter((item) => (
                    normalizeText(item.hero_name).includes(query) ||
                    normalizeText(item.name).includes(query)
                ))
                .slice(0, 12);

            if (matches.length === 0) {
                const emptyState = document.createElement("div");
                emptyState.className = "hv-search-result is-empty";
                emptyState.textContent = "No matching cosmetics.";
                searchResults.appendChild(emptyState);
                return;
            }

            matches.forEach((item) => {
                const button = document.createElement("button");
                button.type = "button";
                button.className = "hv-search-result";
                button.innerHTML = `${item.name}<small>${item.hero_name} | ${item.hero_type}</small>`;
                button.addEventListener("click", () => {
                    searchInput.value = item.name;
                    searchResults.innerHTML = "";
                    updateHeroSelection(item.hero_id);
                    state.currentHeroId = item.hero_id;
                    selectCosmetic(item);
                    applyHeroFilters();
                });
                searchResults.appendChild(button);
            });
        }

        function renderSelectedList() {
            selectedList.innerHTML = "";

            if (state.selectedItems.length === 0) {
                const emptyCopy = document.createElement("p");
                emptyCopy.className = "hv-empty-copy";
                emptyCopy.textContent = "Selected cosmetics will appear here so you can quickly revisit them.";
                selectedList.appendChild(emptyCopy);
                return;
            }

            state.selectedItems.forEach((item) => {
                const pill = document.createElement("span");
                pill.className = "hv-selected-pill";
                pill.textContent = `${item.hero_name} - ${item.name}`;
                selectedList.appendChild(pill);
            });
        }

        function closePopup() {
            popupHost.innerHTML = "";
        }

        function openHeroPopup(heroCard) {
            const heroId = heroCard.dataset.heroId;
            const heroName = heroCard.dataset.heroName;
            const cosmetics = getCosmeticsForHero(heroId);

            updateHeroSelection(heroId);
            state.currentHeroId = heroId;

            if (cosmetics.length === 0) {
                setFeedback(root, "This hero does not have cosmetic history yet.", "warning");
                return;
            }

            const overlay = document.createElement("button");
            overlay.type = "button";
            overlay.className = "hv-popup-overlay";
            overlay.setAttribute("aria-label", "Close cosmetic picker");
            overlay.addEventListener("click", closePopup);

            const card = document.createElement("div");
            card.className = "hv-popup-card";

            const title = document.createElement("h3");
            title.textContent = heroName;
            card.appendChild(title);

            const description = document.createElement("p");
            description.textContent = "Choose a cosmetic to load its market history into the chart.";
            card.appendChild(description);

            const options = document.createElement("div");
            options.className = "hv-popup-options";

            cosmetics.forEach((cosmetic) => {
                const option = document.createElement("button");
                option.type = "button";
                option.className = "hv-popup-option";
                option.textContent = cosmetic.name;
                option.addEventListener("click", () => {
                    selectCosmetic(cosmetic);
                });
                options.appendChild(option);
            });

            card.appendChild(options);

            const closeButton = document.createElement("button");
            closeButton.type = "button";
            closeButton.className = "hv-control-button hv-popup-close";
            closeButton.textContent = "Close";
            closeButton.addEventListener("click", closePopup);
            card.appendChild(closeButton);

            popupHost.innerHTML = "";
            popupHost.appendChild(overlay);
            popupHost.appendChild(card);
        }

        function buildChartConfig(chartType, payload) {
            const config = {
                type: "line",
                data: {},
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: true },
                        title: { display: true, text: `${state.currentItemLabel} | ${chartType.toUpperCase()}` },
                    },
                },
            };

            if (chartType === "time-price") {
                config.data = {
                    labels: payload.labels,
                    datasets: [
                        {
                            label: "Price",
                            data: payload.prices,
                            borderColor: "rgb(37, 99, 235)",
                            backgroundColor: "rgba(37, 99, 235, 0.12)",
                            pointRadius: 2,
                            fill: true,
                            tension: 0.18,
                        },
                        {
                            label: "Price Trend",
                            data: payload.trend_price,
                            borderColor: "rgb(15, 118, 110)",
                            borderDash: [6, 6],
                            pointRadius: 0,
                            tension: 0.18,
                        },
                    ],
                };
                return config;
            }

            if (chartType === "time-quantity") {
                config.data = {
                    labels: payload.labels,
                    datasets: [
                        {
                            label: "Quantity",
                            data: payload.quantities,
                            borderColor: "rgb(249, 115, 22)",
                            backgroundColor: "rgba(249, 115, 22, 0.12)",
                            pointRadius: 0,
                            fill: true,
                            stepped: true,
                            tension: 0,
                        },
                        {
                            label: "Quantity Trend",
                            data: payload.trend_qty,
                            borderColor: "rgb(37, 99, 235)",
                            borderDash: [6, 6],
                            pointRadius: 0,
                            tension: 0.18,
                        },
                    ],
                };
                return config;
            }

            config.type = "scatter";
            config.data = {
                datasets: [{
                    label: "Quantity vs Price",
                    data: payload.quantities.map((quantity, index) => ({ x: quantity, y: payload.prices[index] })),
                    backgroundColor: "rgba(124, 58, 237, 0.7)",
                }],
            };
            config.options.scales = {
                x: { title: { display: true, text: "Quantity" } },
                y: { title: { display: true, text: "Price" } },
            };
            return config;
        }

        async function loadChart(chartType) {
            if (!state.currentItemId) {
                setFeedback(root, "Choose a hero or search for a cosmetic to update the chart.", "warning");
                return;
            }

            state.currentChartType = chartType;
            setActiveButtons(chartTypeButtons, "hvChartType", chartType);
            chartCaption.textContent = `Loading ${state.currentItemLabel} over ${state.currentTimeRange}...`;
            setFeedback(root, `Fetching market history for ${state.currentItemLabel}.`, "info");

            const currentToken = ++requestToken;

            try {
                const response = await fetch(`/api/items/${state.currentItemId}/history/?range=${state.currentTimeRange}`);

                if (!response.ok) {
                    throw new Error(`Unexpected status: ${response.status}`);
                }

                const payload = await response.json();

                if (currentToken !== requestToken) {
                    return;
                }

                if (!Array.isArray(payload.labels) || payload.labels.length === 0) {
                    setFeedback(root, "No market data was found for this cosmetic.", "warning");
                    chartCaption.textContent = "This cosmetic does not have enough market history to plot yet.";
                    return;
                }

                destroyHomeVisualisation();
                visualisationChart = new Chart(canvas.getContext("2d"), buildChartConfig(chartType, payload));
                chartCaption.textContent = `${state.currentItemLabel} loaded with ${payload.labels.length} historical points.`;
                setFeedback(root, `${state.currentItemLabel} is now displayed in the chart.`, "success");
            } catch (error) {
                console.error("Failed to load visualisation data.", error);
                setFeedback(root, "The chart request failed. Please try again.", "error");
                chartCaption.textContent = "The chart could not be refreshed.";
            }
        }

        function selectCosmetic(item) {
            state.currentItemId = item.id;
            state.currentItemLabel = `${item.hero_name} - ${item.name}`;
            state.currentHeroId = item.hero_id;

            if (!state.selectedItems.some((selected) => selected.id === item.id)) {
                state.selectedItems.push(item);
                renderSelectedList();
            }

            updateHeroSelection(item.hero_id);
            closePopup();
            loadChart(state.currentChartType);
        }

        function setTimeRange(range) {
            state.currentTimeRange = range;
            setActiveButtons(timeButtons, "hvTimeRange", range);

            if (state.currentItemId) {
                loadChart(state.currentChartType);
            }
        }

        searchInput.addEventListener("input", () => {
            applyHeroFilters();
            renderSearchResults(normalizeText(searchInput.value));
        });

        filterButtons.forEach((button) => {
            button.addEventListener("click", () => {
                state.currentHeroType = button.dataset.hvHeroType;
                setActiveButtons(filterButtons, "hvHeroType", state.currentHeroType);
                applyHeroFilters();
            });
        });

        heroCards.forEach((card) => {
            const image = card.querySelector("img");
            if (image) {
                image.addEventListener("error", () => {
                    const fallbackIcon = image.dataset.fallbackIcon;
                    if (fallbackIcon && image.src !== fallbackIcon) {
                        image.src = fallbackIcon;
                    }
                }, { once: true });
            }

            card.addEventListener("click", () => {
                openHeroPopup(card);
            });
        });

        timeButtons.forEach((button) => {
            button.addEventListener("click", () => {
                setTimeRange(button.dataset.hvTimeRange);
            });
        });

        chartTypeButtons.forEach((button) => {
            button.addEventListener("click", () => {
                loadChart(button.dataset.hvChartType);
            });
        });

        renderSelectedList();
        setActiveButtons(filterButtons, "hvHeroType", state.currentHeroType);
        setActiveButtons(timeButtons, "hvTimeRange", state.currentTimeRange);
        setActiveButtons(chartTypeButtons, "hvChartType", state.currentChartType);
        applyHeroFilters();

        if (searchItems.length > 0) {
            selectCosmetic(searchItems[0]);
        } else {
            setFeedback(root, "No cosmetic history is available yet.", "warning");
        }
    }

    window.destroyHomeVisualisation = destroyHomeVisualisation;
    document.addEventListener("DOMContentLoaded", initHomeVisualisation);
})();
