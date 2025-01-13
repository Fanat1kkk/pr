function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');

    // Создаем элемент уведомления
    const toast = document.createElement('div');
    toast.className = `flex items-center p-4 max-w-sm rounded-lg shadow-lg transition-opacity duration-500 opacity-0 pointer-events-none ${
        type === 'success'
            ? 'bg-green-100 border border-green-400 text-green-800'
            : 'bg-red-100 border border-red-400 text-red-800'
    }`;
    toast.innerHTML = `
        <svg class="w-6 h-6 ${
            type === 'success' ? 'text-green-600' : 'text-red-600'
        }" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${
              type === 'success'
                  ? 'M5 13l4 4L19 7'
                  : 'M6 18L18 6M6 6l12 12'
          }" />
        </svg>
        <p class="ml-3">${message}</p>
    `;

    // Добавляем уведомление в контейнер
    container.appendChild(toast);

    // Анимация появления
    setTimeout(() => {
        toast.classList.add('opacity-100', 'pointer-events-auto');
    }, 100);

    // Удаление через 5 секунд
    setTimeout(() => {
        toast.classList.remove('opacity-100');
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}
