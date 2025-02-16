function select_payment(clickedElemet) {
    if (clickedElemet.classList.contains('selected')) {
        return;
    }
    let payments = document.getElementsByClassName('payments');
    for (let e of payments) {
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
    let sum = document.getElementById('btn_pay').dataset.price;
    let orderId = document.getElementById('btn_pay').dataset.orderid;
    let btnPay = document.getElementById('btn_pay');
    let errorMethod = document.getElementById('method-error');
    errorMethod.innerHTML = '';
    btnPay.disabled = true;

    // Проверяем наличие выбранного метода оплаты
    let elementPayMethod = document.querySelector('.selected');
    if (!elementPayMethod) {
        errorMethod.innerHTML = "Выберите способ оплаты";
        btnPay.disabled = false;
        return;
    }

    // Получаем метод оплаты
    let payProvider = elementPayMethod.getAttribute('data-method');

    // Проверяем сумму и метод оплаты
    if (!sum || isNaN(sum) || parseFloat(sum) <= 0) {
        showToast('Некорректная сумма!', 'error');
        btnPay.disabled = false;
        return;
    }
    if (!payProvider) {
        showToast('Не указан способ оплаты!', 'error');
        btnPay.disabled = false;
        return;
    }

    // Формируем данные для отправки
    let postData = {
        sum: sum,
        pay_provider: payProvider,
        order_id: orderId,
    };

    try {
        // Отправляем POST-запрос
        let response = await fetch("/order-pay/", {
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

            // Проверяем наличие redirect
            if (result.redirect && payProvider === 'PRF') {
                showToast('Оплата успешно завершена!', 'success');
                setTimeout(() => {
                    window.location.href = result.redirect; // Перенаправление после задержки
                }, 3000);
            } else if (result.redirect && payProvider !== 'PRF') {
                showToast('Вы будите перенаправлены на сайт оплаты', 'success');
                setTimeout(() => {
                    window.location.href = result.redirect; // Перенаправление после задержки
                }, 3000);
            } else {
                showToast('Оплата успешна, но URL для перенаправления отсутствует.', 'success');
                btnPay.disabled = false;
            }
        } else {
            // Обработка ошибок сервера
            let error = await response.json();
            errorMethod.innerHTML = error.error || 'Неизвестная ошибка.';
            showToast(error.error || 'Произошла ошибка при оплате.', 'error');
            btnPay.disabled = false;
        }
    } catch (error) {
        console.error("Ошибка отправки запроса:", error);
        showToast("Ошибка соединения. Проверьте подключение к интернету.", 'error');
        btnPay.disabled = false;
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
