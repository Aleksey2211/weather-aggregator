// static/script.js

const API_BASE = '/api/weather';
const cityInput = document.getElementById('cityInput');
const searchBtn = document.getElementById('searchBtn');
const useCountryCheckbox = document.getElementById('useCountry');
const countryCodeInput = document.getElementById('countryCode');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('errorMessage');
const weatherResults = document.getElementById('weatherResults');
const cityInfo = document.getElementById('cityInfo');
const forecastsContainer = document.getElementById('forecastsContainer');

// Slowpoke эмодзи как картинка (для простоты используем текст, но можно и картинку)
const SLOWPOKE = '🐾';  // Или можно использовать: '🐢💤'

// Включение/отключение поля кода страны
useCountryCheckbox.addEventListener('change', (e) => {
    countryCodeInput.disabled = !e.target.checked;
    if (!e.target.checked) {
        countryCodeInput.value = '';
    }
});

// Поиск по кнопке и по Enter
searchBtn.addEventListener('click', searchWeather);
cityInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchWeather();
});

async function searchWeather() {
    const city = cityInput.value.trim();
    if (!city) {
        showError('Введите название города');
        return;
    }

    // Скрываем предыдущие результаты
    weatherResults.style.display = 'none';
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'block';

    // Формируем параметры запроса
    const params = new URLSearchParams();
    params.append('city', city);

    if (useCountryCheckbox.checked && countryCodeInput.value.trim()) {
        params.append('country', countryCodeInput.value.trim().toUpperCase());
    }

    try {
        const response = await fetch(`${API_BASE}?${params.toString()}`);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Ошибка ${response.status}`);
        }

        const data = await response.json();
        displayWeather(data);

    } catch (err) {
        showError(err.message || 'Не удалось получить данные о погоде');
    } finally {
        loadingDiv.style.display = 'none';
    }
}

function displayWeather(data) {
    // Отображаем информацию о городе
    cityInfo.innerHTML = `
        <h2>📍 ${escapeHtml(data.city)}</h2>
        <p>Код страны: ${escapeHtml(data.country_code || '—')}</p>
    `;

    // Очищаем контейнер с прогнозами
    forecastsContainer.innerHTML = '';

    // Получаем список источников
    const sources = Object.keys(data.forecasts);

    if (sources.length === 0) {
        forecastsContainer.innerHTML = '<div class="forecast-card" style="padding: 20px; text-align: center;">Нет данных от доступных сервисов</div>';
    } else {
        // Сортируем источники для наглядности
        sources.sort().forEach(source => {
            const forecast = data.forecasts[source];
            const card = createForecastCard(source, forecast);
            forecastsContainer.appendChild(card);
        });
    }

    // Показываем блок с результатами
    weatherResults.style.display = 'block';

    // Если есть ошибки агрегации или сбора — показываем внизу
    if (data.fetch_errors && Object.keys(data.fetch_errors).length > 0) {
        const errorsCard = document.createElement('div');
        errorsCard.className = 'forecast-card';
        errorsCard.style.borderColor = '#fecaca';
        errorsCard.innerHTML = `
            <div class="card-header" style="background: #fef2f2;">
                <h3 style="color: #dc2626;">⚠️ Ошибки при сборе данных</h3>
            </div>
            <div class="data-grid">
                ${Object.entries(data.fetch_errors).map(([source, err]) => `
                    <div class="data-row">
                        <span class="data-label">${escapeHtml(source)}</span>
                        <span class="data-value no-data">${escapeHtml(err)}</span>
                    </div>
                `).join('')}
            </div>
        `;
        forecastsContainer.appendChild(errorsCard);
    }

    if (data.parse_errors && Object.keys(data.parse_errors).length > 0) {
        const errorsCard = document.createElement('div');
        errorsCard.className = 'forecast-card';
        errorsCard.style.borderColor = '#fecaca';
        errorsCard.innerHTML = `
            <div class="card-header" style="background: #fef2f2;">
                <h3 style="color: #dc2626;">⚠️ Ошибки при парсинге</h3>
            </div>
            <div class="data-grid">
                ${Object.entries(data.parse_errors).map(([source, err]) => `
                    <div class="data-row">
                        <span class="data-label">${escapeHtml(source)}</span>
                        <span class="data-value no-data">${escapeHtml(err)}</span>
                    </div>
                `).join('')}
            </div>
        `;
        forecastsContainer.appendChild(errorsCard);
    }
}

function createForecastCard(source, forecast) {
    const card = document.createElement('div');
    card.className = 'forecast-card';

    // Определяем иконку для источника
    const sourceIcons = {
        'api.open-meteo.com': '🌍',
        'www.7timer.info': '⏱️',
        'power.larc.nasa.gov': '🚀'
    };
    const icon = sourceIcons[source] || '📡';

    // Формируем данные для отображения
    const fields = [
        { label: '🌡️ Температура', value: forecast.temperature_c, unit: '°C' },
        { label: '💨 Ветер', value: forecast.wind_speed_kmh, unit: 'км/ч' },
        { label: '🧭 Направление ветра', value: forecast.wind_direction_deg, unit: '°' },
        { label: '☔ Осадки', value: forecast.precipitation_mm, unit: 'мм' },
        { label: '☁️ Облачность', value: forecast.cloud_cover_pct, unit: '%' }
    ];

    // Формируем HTML строку с данными
    let dataRowsHtml = '';
    for (const field of fields) {
        const hasData = field.value !== null && field.value !== undefined;
        const valueDisplay = hasData ? `${field.value} ${field.unit}` : `${SLOWPOKE} нет данных`;
        const noDataClass = !hasData ? 'no-data' : '';

        dataRowsHtml += `
            <div class="data-row">
                <span class="data-label">${field.label}</span>
                <span class="data-value ${noDataClass}">${valueDisplay}</span>
            </div>
        `;
    }

    // Добавляем raw_data_info если оно не "no info"
    let rawInfoHtml = '';
    if (forecast.raw_data_info && forecast.raw_data_info !== 'no info') {
        rawInfoHtml = `
            <div class="data-row" style="background: #fef9c3;">
                <span class="data-label">ℹ️ Инфо</span>
                <span class="data-value" style="font-size: 0.8rem;">${escapeHtml(forecast.raw_data_info)}</span>
            </div>
        `;
    }

    card.innerHTML = `
        <div class="card-header">
            <h3>${icon} ${escapeHtml(source)}</h3>
        </div>
        <div class="data-grid">
            ${dataRowsHtml}
            ${rawInfoHtml}
        </div>
    `;

    return card;
}

function showError(message) {
    errorDiv.innerHTML = `
        <span style="font-size: 1.2rem;">⚠️</span>
        <p style="margin-top: 8px;">${escapeHtml(message)}</p>
        <p style="margin-top: 8px; font-size: 0.8rem;">Попробуйте другой город или укажите код страны (например, RU для Москвы)</p>
    `;
    errorDiv.style.display = 'block';
    weatherResults.style.display = 'none';
}

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}