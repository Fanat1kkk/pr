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


// Функция обновления информации в таблице
function updateInfo(orderId) {
    // Находим элементы таблицы по id
    let statusElement = document.getElementById(`status-${orderId}`);
    let btnElement = document.getElementById(`btn-${orderId}`);

    // Обновляем содержимое статуса
    if (statusElement) {
        statusElement.innerHTML = `
            <span class="px-3 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-200 text-black">
                Отменяется
            </span>
        `;
    }

    // Обновляем содержимое кнопки/действия
    if (btnElement) {
        btnElement.innerHTML = `
            <p>Нет действий</p>
        `;
    }
}


function cancelOrder(button) {
    // Получаем значение атрибута data-orderid
    const orderId = button.dataset.orderid;
    // Можно добавить дополнительные действия, например, запрос к серверу
    fetch(`/profile/cancel-order/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(), // Функция для получения CSRF токена
        },
        body: JSON.stringify({ order_id: orderId }),
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error("Ошибка при отмене заказа");
        }
    })
    .then(data => {
        if (data.status === 'WCL'){
            updateInfo(orderId);
            showToast('Заказ успешно отменён!', 'success');
        }else{
            console.log("Ответ сервера:", data);
        }
    })
    .catch(error => {
        console.error("Ошибка:", error);
        alert("Не удалось отменить заказ.");
    });
}