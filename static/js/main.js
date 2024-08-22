document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded");
    const searchBtn = document.getElementById('search-btn');
    const tickerInput = document.getElementById('ticker-input');
    const aiForm = document.getElementById('ai-form');
    const fullAnalysisBtn = document.getElementById('full-analysis-btn');

    if (searchBtn) {
        console.log("Search button found");
        searchBtn.addEventListener('click', function() {
            console.log("Search button clicked");
            const ticker = tickerInput.value.toUpperCase();
            if (ticker) {
                console.log("Searching for ticker:", ticker);
                getStockData(ticker);
            }
        });
    } else {
        console.error("Search button not found");
    }

    if (aiForm) {
        aiForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("AI form submitted");
            const ticker = document.querySelector('input[name="ticker"]').value;
            const question = document.querySelector('input[name="question"]').value;
            getAIAnalysis(ticker, question);
        });
    }

    if (fullAnalysisBtn) {
        fullAnalysisBtn.addEventListener('click', function() {
            console.log("Full analysis button clicked");
            const ticker = tickerInput.value.toUpperCase();
            if (ticker) {
                console.log("Getting full analysis for ticker:", ticker);
                // Add your code here to perform the full analysis
            }
        });
    }
});

function getStockData(ticker) {
    console.log("Getting stock data for:", ticker);
    fetch('/get_stock_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `ticker=${ticker}`
    })
    .then(response => response.json())
    .then(data => {
        console.log("Received stock data:", data);
        updateDashboard(data);
    })
    .catch(error => console.error('Error:', error));
}

function updateDashboard(data) {
    console.log("Updating dashboard with data:", data);
    updateStockOverview(data);
    updateKeyMetrics(data);
    updateCharts(data);
    updateNews(data.news);
    updateSentiment(data.sentiment);
    updateKeyStatistics(data);
    updateCompetitorAnalysis(data.competitors);
}

function updateStockOverview(data) {
    console.log("Updating stock overview");
    document.getElementById('stock-name').textContent = data.name;
    document.getElementById('stock-price').textContent = `$${data.price.toFixed(2)}`;
    const changeElement = document.getElementById('stock-change');
    const changePercent = (data.change * 100).toFixed(2);
    changeElement.textContent = `${changePercent}%`;
    changeElement.style.color = changePercent >= 0 ? 'green' : 'red';
    document.getElementById('stock-volume').textContent = `Volume: ${data.volume.toLocaleString()}`;
    document.getElementById('stock-market-cap').textContent = `Market Cap: $${(data.market_cap / 1e9).toFixed(2)}B`;
    // Assuming these properties exist in your data object
    document.getElementById('stock-52w-high').textContent = `52W High: $${data.fiftyTwoWeekHigh.toFixed(2)}`;
    document.getElementById('stock-52w-low').textContent = `52W Low: $${data.fiftyTwoWeekLow.toFixed(2)}`;
}

function updateKeyMetrics(data) {
    console.log("Updating key metrics");
    const metricsContent = document.getElementById('metrics-content');
    metricsContent.innerHTML = `
        <div>P/E Ratio: ${data.pe_ratio ? data.pe_ratio.toFixed(2) : 'N/A'}</div>
        <div>Dividend Yield: ${data.dividend_yield ? (data.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}</div>
        <div>EPS (TTM): ${data.eps ? '$' + data.eps.toFixed(2) : 'N/A'}</div>
        <div>Beta: ${data.beta ? data.beta.toFixed(2) : 'N/A'}</div>
    `;
}

function updateCharts(data) {
    console.log("Updating charts");
    updateStockChart(data.historical_dates, data.historical_data);
    updateSectorChart(data.sector_performance);
    updateTechnicalChart(data);
    updateFinancialMetricsChart(data.financial_metrics);
}

function updateStockChart(labels, data) {
    console.log("Updating stock chart");
    const ctx = document.getElementById('stockChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Stock Price',
                data: data,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

function updateSectorChart(sectorData) {
    console.log("Updating sector chart");
    const ctx = document.getElementById('sectorChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(sectorData),
            datasets: [{
                label: 'Sector Performance',
                data: Object.values(sectorData),
                backgroundColor: 'rgba(75, 192, 192, 0.6)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateTechnicalChart(data) {
    console.log("Updating technical chart");
    const ctx = document.getElementById('technicalChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.historical_dates.slice(-30),
            datasets: [{
                label: 'Price',
                data: data.historical_data.slice(-30),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }, {
                label: '50-day SMA',
                data: Array(30).fill(data.sma_50),
                borderColor: 'rgb(255, 99, 132)',
                borderDash: [5, 5]
            }, {
                label: '200-day SMA',
                data: Array(30).fill(data.sma_200),
                borderColor: 'rgb(54, 162, 235)',
                borderDash: [5, 5]
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

function updateFinancialMetricsChart(metricsData) {
    console.log("Updating financial metrics chart");
    const ctx = document.getElementById('metricsChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(metricsData),
            datasets: [{
                label: 'Financial Metrics',
                data: Object.values(metricsData),
                backgroundColor: 'rgba(75, 192, 192, 0.6)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateNews(news) {
    console.log("Updating news");
    const newsList = document.querySelector('.news-list');
    newsList.innerHTML = news.map(item => `
        <li><a href="${item.url}" target="_blank">${item.title}</a></li>
    `).join('');
}

function updateSentiment(sentiment) {
    console.log("Updating sentiment chart");
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [sentiment.positive, sentiment.neutral, sentiment.negative],
                backgroundColor: ['#4CAF50', '#FFC107', '#F44336']
            }]
        },
        options: {
            responsive: true
        }
    });
}

function updateKeyStatistics(data) {
    console.log("Updating key statistics");
    const table = document.getElementById('statistics-table');
    table.innerHTML = `
        <tr><td>52 Week High</td><td>$${data.fiftyTwoWeekHigh.toFixed(2)}</td></tr>
        <tr><td>52 Week Low</td><td>$${data.fiftyTwoWeekLow.toFixed(2)}</td></tr>
        <tr><td>50 Day Average</td><td>$${data.fiftyDayAverage.toFixed(2)}</td></tr>
        <tr><td>200 Day Average</td><td>$${data.twoHundredDayAverage.toFixed(2)}</td></tr>
        <tr><td>Volume</td><td>${data.volume.toLocaleString()}</td></tr>
        <tr><td>Avg Volume</td><td>${data.averageVolume.toLocaleString()}</td></tr>
        <tr><td>Market Cap</td><td>$${(data.marketCap / 1e9).toFixed(2)}B</td></tr>
        <tr><td>Beta</td><td>${data.beta.toFixed(2)}</td></tr>
    `;
}

function updateCompetitorAnalysis(competitors) {
    console.log("Updating competitor analysis");
    const competitorContent = document.getElementById('competitor-content');
    competitorContent.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Company</th>
                    <th>Price</th>
                    <th>Market Cap</th>
                    <th>P/E Ratio</th>
                </tr>
            </thead>
            <tbody>
                ${competitors.map(comp => `
                    <tr>
                        <td>${comp.name}</td>
                        <td>$${comp.price.toFixed(2)}</td>
                        <td>$${(comp.marketCap / 1e9).toFixed(2)}B</td>
                        <td>${comp.peRatio ? comp.peRatio.toFixed(2) : 'N/A'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ... (keep the existing code and add/modify the following functions)

function updateStockOverview(data) {
    document.getElementById('stock-name').textContent = data.name;
    document.getElementById('stock-price').textContent = `$${data.price.toFixed(2)}`;
    const changeElement = document.getElementById('stock-change');
    const changePercent = (data.change * 100).toFixed(2);
    changeElement.textContent = `${changePercent}%`;
    changeElement.style.color = changePercent >= 0 ? 'var(--secondary-color)' : 'var(--accent-color)';
    
    document.getElementById('stock-volume').textContent = data.volume.toLocaleString();
    document.getElementById('stock-market-cap').textContent = `$${(data.market_cap / 1e9).toFixed(2)}B`;
    document.getElementById('stock-52w-high').textContent = `$${data.fiftyTwoWeekHigh.toFixed(2)}`;
    document.getElementById('stock-52w-low').textContent = `$${data.fiftyTwoWeekLow.toFixed(2)}`;
}

function updateKeyMetrics(data) {
    const metricsContent = document.getElementById('metrics-content');
    metricsContent.innerHTML = `
        <div class="metric">
            <span class="metric-label">P/E Ratio</span>
            <span class="metric-value">${data.pe_ratio ? data.pe_ratio.toFixed(2) : 'N/A'}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Dividend Yield</span>
            <span class="metric-value">${data.dividend_yield ? (data.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}</span>
        </div>
        <div class="metric">
            <span class="metric-label">EPS (TTM)</span>
            <span class="metric-value">$${data.eps ? data.eps.toFixed(2) : 'N/A'}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Beta</span>
            <span class="metric-value">${data.beta ? data.beta.toFixed(2) : 'N/A'}</span>
        </div>
    `;
}

function updateCompetitorAnalysis(competitors) {
    const competitorContent = document.getElementById('competitor-content');
    competitorContent.innerHTML = `
        <table class="competitor-table">
            <thead>
                <tr>
                    <th>Company</th>
                    <th>Price</th>
                    <th>Market Cap</th>
                    <th>P/E Ratio</th>
                </tr>
            </thead>
            <tbody>
                ${competitors.map(comp => `
                    <tr>
                        <td>${comp.name}</td>
                        <td>$${comp.price.toFixed(2)}</td>
                        <td>$${(comp.marketCap / 1e9).toFixed(2)}B</td>
                        <td>${comp.peRatio ? comp.peRatio.toFixed(2) : 'N/A'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}



