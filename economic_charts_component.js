/**
 * Компонент для отображения экономических графиков
 * Интеграция с существующим WebApp
 */

class EconomicChartsComponent {
    constructor() {
        this.charts = {};
        this.isChartJsLoaded = false;
        this.loadChartJs();
    }

    /**
     * Загружает Chart.js библиотеку
     */
    loadChartJs() {
        if (typeof Chart !== 'undefined') {
            this.isChartJsLoaded = true;
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = () => {
            this.isChartJsLoaded = true;
            console.log('Chart.js загружен');
        };
        script.onerror = () => {
            console.error('Ошибка загрузки Chart.js');
        };
        document.head.appendChild(script);
    }

    /**
     * Создает HTML структуру для графиков
     */
    createChartsContainer() {
        const container = document.createElement('div');
        container.className = 'economic-charts-container';
        container.innerHTML = `
            <div class="charts-section">
                <h3 class="charts-title">📊 Экономические данные</h3>
                
                <div class="charts-grid">
                    <div class="chart-wrapper">
                        <div class="chart-title">📈 Динамика роста ВВП</div>
                        <div class="chart-container">
                            <canvas id="gdpChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="chart-wrapper">
                        <div class="chart-title">📉 Динамика инфляции</div>
                        <div class="chart-container">
                            <canvas id="inflationChart"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card gdp">
                        <div class="stat-value" id="latestGdp">-</div>
                        <div class="stat-label">Последний рост ВВП</div>
                        <div class="trend-indicator" id="gdpTrend">-</div>
                    </div>
                    
                    <div class="stat-card inflation">
                        <div class="stat-value" id="latestInflation">-</div>
                        <div class="stat-label">Последняя инфляция</div>
                        <div class="trend-indicator" id="inflationTrend">-</div>
                    </div>
                </div>
            </div>
        `;

        // Добавляем стили
        this.addStyles();
        
        return container;
    }

    /**
     * Добавляет CSS стили для графиков
     */
    addStyles() {
        if (document.getElementById('economic-charts-styles')) {
            return;
        }

        const styles = document.createElement('style');
        styles.id = 'economic-charts-styles';
        styles.textContent = `
            .economic-charts-container {
                margin: 20px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #e9ecef;
            }
            
            .charts-title {
                text-align: center;
                color: #495057;
                margin-bottom: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            
            .charts-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 20px;
            }
            
            .chart-wrapper {
                background: white;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .chart-title {
                font-size: 16px;
                font-weight: bold;
                color: #495057;
                margin-bottom: 10px;
                text-align: center;
            }
            
            .chart-container {
                position: relative;
                height: 300px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
            
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .stat-card.inflation {
                background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            }
            
            .stat-value {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .stat-label {
                font-size: 12px;
                opacity: 0.9;
                margin-bottom: 5px;
            }
            
            .trend-indicator {
                font-size: 11px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 4px;
                display: inline-block;
            }
            
            .trend-up {
                background: #28a745;
                color: white;
            }
            
            .trend-down {
                background: #dc3545;
                color: white;
            }
            
            .trend-stable {
                background: #6c757d;
                color: white;
            }
            
            @media (max-width: 768px) {
                .charts-grid {
                    grid-template-columns: 1fr;
                }
                
                .stats-grid {
                    grid-template-columns: 1fr;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }

    /**
     * Получает экономические данные с сервера
     */
    async fetchEconomicData(countryCode = 'TUR', yearsBack = 10) {
        try {
            const response = await fetch('/api/economic_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    country_code: countryCode,
                    years_back: yearsBack
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.chart_data;
        } catch (error) {
            console.error('Ошибка получения экономических данных:', error);
            return null;
        }
    }

    /**
     * Создает графики с полученными данными
     */
    createCharts(chartData) {
        if (!this.isChartJsLoaded) {
            console.warn('Chart.js еще не загружен');
            setTimeout(() => this.createCharts(chartData), 100);
            return;
        }

        // Создаем график ВВП
        const gdpCtx = document.getElementById('gdpChart');
        if (gdpCtx && chartData.gdp_chart) {
            this.charts.gdp = new Chart(gdpCtx, {
                type: 'line',
                data: chartData.gdp_chart,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Рост ВВП (%)'
                            }
                        }
                    }
                }
            });
        }

        // Создаем график инфляции
        const inflationCtx = document.getElementById('inflationChart');
        if (inflationCtx && chartData.inflation_chart) {
            this.charts.inflation = new Chart(inflationCtx, {
                type: 'line',
                data: chartData.inflation_chart,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Инфляция (%)'
                            }
                        }
                    }
                }
            });
        }

        // Обновляем статистику
        this.updateStats(chartData);
    }

    /**
     * Обновляет статистические данные
     */
    updateStats(chartData) {
        const latest = chartData.latest;
        const trends = chartData.trends;

        // Обновляем последние значения ВВП
        if (latest.gdp) {
            const gdpElement = document.getElementById('latestGdp');
            if (gdpElement) {
                gdpElement.textContent = `${latest.gdp.value}% (${latest.gdp.year})`;
            }
        }

        // Обновляем последние значения инфляции
        if (latest.inflation) {
            const inflationElement = document.getElementById('latestInflation');
            if (inflationElement) {
                inflationElement.textContent = `${latest.inflation.value}% (${latest.inflation.year})`;
            }
        }

        // Обновляем тренды
        if (trends.gdp_trend !== undefined) {
            const gdpTrendElement = document.getElementById('gdpTrend');
            if (gdpTrendElement) {
                const trend = trends.gdp_trend * 100;
                const trendClass = trend > 0 ? 'trend-up' : trend < 0 ? 'trend-down' : 'trend-stable';
                const trendSymbol = trend > 0 ? '↑' : trend < 0 ? '↓' : '→';
                
                gdpTrendElement.textContent = `${trendSymbol} ${Math.abs(trend).toFixed(1)}%`;
                gdpTrendElement.className = `trend-indicator ${trendClass}`;
            }
        }

        if (trends.inflation_trend !== undefined) {
            const inflationTrendElement = document.getElementById('inflationTrend');
            if (inflationTrendElement) {
                const trend = trends.inflation_trend * 100;
                const trendClass = trend > 0 ? 'trend-up' : trend < 0 ? 'trend-down' : 'trend-stable';
                const trendSymbol = trend > 0 ? '↑' : trend < 0 ? '↓' : '→';
                
                inflationTrendElement.textContent = `${trendSymbol} ${Math.abs(trend).toFixed(1)}%`;
                inflationTrendElement.className = `trend-indicator ${trendClass}`;
            }
        }
    }

    /**
     * Инициализирует компонент и отображает графики
     */
    async init(container, countryCode = 'TUR') {
        // Создаем контейнер для графиков
        const chartsContainer = this.createChartsContainer();
        container.appendChild(chartsContainer);

        // Получаем данные
        const chartData = await this.fetchEconomicData(countryCode);
        
        if (chartData) {
            // Создаем графики
            this.createCharts(chartData);
        } else {
            // Показываем сообщение об ошибке
            chartsContainer.innerHTML = `
                <div style="text-align: center; color: #6c757d; padding: 20px;">
                    <p>Не удалось загрузить экономические данные</p>
                    <button onclick="location.reload()" style="padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Попробовать снова
                    </button>
                </div>
            `;
        }
    }

    /**
     * Обновляет данные графиков
     */
    async updateData(countryCode = 'TUR') {
        const chartData = await this.fetchEconomicData(countryCode);
        if (chartData) {
            // Уничтожаем старые графики
            Object.values(this.charts).forEach(chart => {
                if (chart) chart.destroy();
            });
            this.charts = {};

            // Создаем новые графики
            this.createCharts(chartData);
        }
    }

    /**
     * Уничтожает компонент
     */
    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Экспортируем для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EconomicChartsComponent;
} else {
    window.EconomicChartsComponent = EconomicChartsComponent;
} 