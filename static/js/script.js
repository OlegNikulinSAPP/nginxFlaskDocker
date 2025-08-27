// Загружаем данные о посещениях через API
async function loadVisitData() {
    try {
        const response = await fetch('/api/visit');
        const data = await response.json();

        displayVisitData(data);
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        document.getElementById('visit-data').innerHTML = `
            <p style="color: red;">❌ Ошибка загрузки данных: ${error.message}</p>
        `;
    }
}

// Отображаем данные о посещениях
function displayVisitData(data) {
    const visitData = document.getElementById('visit-data');

    visitData.innerHTML = `
        <div class="visit-message">${data.message}</div>
        <div class="visit-count">${data.total_visits}</div>
        <div class="visit-label">Всего посещений</div>
    `;
}

// Обновляем данные каждые 30 секунд
function startAutoRefresh() {
    setInterval(loadVisitData, 30000);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    loadVisitData();
    startAutoRefresh();

    console.log('🚀 Приложение загружено!');
});