function select_payment(clickedElemet) {
    if (clickedElemet.classList.contains('selected')) {
        return;
    }
    let payments = document.getElementsByClassName('payments');
    for(let e of payments){
        if (e === clickedElemet) {
            let img = e.lastElementChild;
            img.classList.toggle('hidden');
            e.classList.remove('hover:ring-2', 'hover:offset-blue-500');
            e.classList.add('selected', 'ring-2', 'ring-blue-600');
            continue
        }
        let img = e.lastElementChild;
        img.classList.add('hidden');
        e.classList.remove('selected', 'ring-2', 'ring-blue-600');
        e.classList.add('hover:ring-2', 'hover:offset-blue-500');

    }
}

async function pay() {
    // Получаем сумму
    let elementSum = document.getElementById('id_sum');
    let sum = elementSum.value;
    let errorMethod = document.getElementById('method-error');
    let errorSum = document.getElementById('sum-error');

    errorMethod.innerHTML = '';
    errorSum.innerHTML = '';

    // Проверяем, что сумма введена
    if (!sum || parseFloat(sum) <= 0) {
        errorSum.innerHTML = "Введите корректную сумму";
        return;
    }

    // Получаем выбранный метод оплаты
    let elementPayMethod = document.querySelector('.selected');
    if (!elementPayMethod) {
        errorMethod.innerHTML = "Выберите способ оплаты";
        return;
    }
    let payProvider = elementPayMethod.getAttribute('data-method');

    // Формируем данные для отправки
    let postData = {
        sum: sum,
        pay_provider: payProvider,
    };

    try {
        // Отправляем POST-запрос
        let response = await fetch("http://127.0.0.1:8000/profile/pay-balance/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken() // Получаем CSRF токен
            },
            body: JSON.stringify(postData),
        });

        // Проверяем ответ от сервера
        if (response.ok) {
            let result = await response.json();
            console.log(result.redirect);
            window.open(result.redirect, '_blank');
            
        } else {
            let error = await response.json();
            showToast(error.error, 'error');
        }
    } catch (error) {
        console.error("Ошибка отправки запроса:", error);
        alert("Ошибка соединения. Проверьте подключение к интернету.");
    }
}

// Функция для получения CSRF токена из cookie
function getCSRFToken() {
    let cookies = document.cookie.split("; ");
    for (let cookie of cookies) {
        let [name, value] = cookie.split("=");
        if (name === "csrftoken") {
            return value;
        }
    }
    return "";
}


document.addEventListener('DOMContentLoaded', async () => {
    let currentPage = 1; // Текущая страница

    const loadMoreButton = document.getElementById('loadHistory');
    const tbody = document.querySelector('tbody.divide-y');

    // Функция для загрузки данных
    async function loadPage(page) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/profile/history-pay/${page}`);
            const data = await response.json();

            if (data.ok) {
                // Если запрос успешный, добавляем содержимое в таблицу
                tbody.innerHTML += data.ok.html;
                if (data.ok.next_page) {
                    console.log('true')
                    loadMoreButton.classList.remove('hidden');
                } else {
                    console.log('false')
                    loadMoreButton.classList.add('hidden');
                }
            } else if (data.error) {
                // Если есть ошибка, выводим сообщение
                console.log(`Ошибка: ${data.error}`);
            }
        } catch (error) {
            // Обработка ошибок запроса
            console.error('Ошибка при загрузке данных:', error);
            alert('Не удалось загрузить данные. Попробуйте снова.');
        }
    }

    // Автоматическая загрузка первой страницы при загрузке страницы
    await loadPage(currentPage);

    // Загрузка следующей страницы при нажатии на кнопку
    loadMoreButton.addEventListener('click', async () => {
        currentPage++; // Увеличиваем номер страницы
        await loadPage(currentPage);
    });
});
