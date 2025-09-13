/**
 * Telegram WebApp проверка и перенаправление
 * Этот файл содержит общие функции для проверки, запущено ли приложение из Telegram
 */

// Проверка, запущено ли приложение из Telegram
function isTelegramWebApp() {
    // Проверяем наличие Telegram WebApp API
    if (typeof window.Telegram !== 'undefined' && window.Telegram.WebApp) {
        // Проверяем, что это действительно Telegram WebApp, а не просто загруженный скрипт
        const tg = window.Telegram.WebApp;
        return tg.initData && tg.initDataUnsafe && tg.initDataUnsafe.user;
    }
    return false;
}

// Функция перенаправления на официальный сайт
function redirectToOfficialSite() {
    console.log('⚠️ Приложение запущено не из Telegram, перенаправляем на сайт...');
    
    // Показываем сообщение пользователю
    document.body.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 20px;">
            <div style="background: white; color: #333; padding: 40px; border-radius: 20px; max-width: 400px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                <h2 style="margin-bottom: 20px; color: #667eea;">Aaadviser</h2>
                <p style="margin-bottom: 20px; line-height: 1.5;">Это приложение предназначено для использования в Telegram. Пожалуйста, откройте его через Telegram бота.</p>
                <p style="margin-bottom: 30px; font-size: 14px; color: #666;">Перенаправление на официальный сайт через 3 секунды...</p>
                <div style="width: 100%; height: 4px; background: #f0f0f0; border-radius: 2px; overflow: hidden;">
                    <div id="progressBar" style="width: 0%; height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); transition: width 3s linear;"></div>
                </div>
            </div>
        </div>
    `;
    
    // Запускаем прогресс-бар
    setTimeout(() => {
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.style.width = '100%';
        }
    }, 100);
    
    // Перенаправляем через 3 секунды
    setTimeout(() => {
        window.location.href = 'https://aaadviser.online/';
    }, 3000);
}

// Функция инициализации проверки Telegram WebApp
function initTelegramCheck() {
    // Проверяем, запущено ли приложение из Telegram
    if (!isTelegramWebApp()) {
        redirectToOfficialSite();
        return false; // Возвращаем false, если не из Telegram
    }
    return true; // Возвращаем true, если из Telegram
}

// Автоматическая проверка при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Небольшая задержка для корректной инициализации Telegram WebApp
    setTimeout(() => {
        initTelegramCheck();
    }, 100);
});
