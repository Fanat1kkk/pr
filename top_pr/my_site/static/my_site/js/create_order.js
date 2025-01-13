document.addEventListener('DOMContentLoaded', function () {
    const decreaseBtn = document.getElementById('decrease');
    const increaseBtn = document.getElementById('increase');
    const numberInput = document.getElementById('numberInput');
    const priceDisplay = document.getElementById('priceDisplay'); // Элемент для отображения итоговой цены
    const submitButton = document.getElementById('submitButton');
    const promocodeInput = document.getElementById('promocode');
    const promocodeButton = document.getElementById('promocodeButton');
    const error = document.getElementById('promo-error'); // Ошибка для промокода

    // Получаем min_count и max_count из атрибутов data-* в скрытом элементе
    const serviceData = document.getElementById('serviceData');
    if (!serviceData) {
        console.error('Элемент с id="serviceData" не найден!');
        return;
    }

    const minCount = parseInt(serviceData.getAttribute('data-min-count'));
    const maxCount = parseInt(serviceData.getAttribute('data-max-count'));
    const price = parseFloat(serviceData.getAttribute('data-price').replace(',', '.'));

    if (isNaN(minCount) || isNaN(maxCount) || isNaN(price)) {
        console.error('Ошибка в данных: minCount, maxCount или price имеют некорректные значения.');
        return;
    }

    // Изначальная скидка из атрибута data-promo
    let promo = parseInt(serviceData.getAttribute('data-promo')) || 0;

    function calc() {
        const count = parseInt(numberInput.value);
        console.log('count: ', count);  // Логируем count

        if (!isNaN(count) && count >= minCount && count <= maxCount) {
            console.log('2')
            let totalPrice = count * price;
            console.log('totalPrice: ', totalPrice); // Логируем общую цену до скидки

            // Рассчитываем итоговую цену с учетом скидки
            let discount = totalPrice * (promo / 100);
            console.log('discount: ', discount); // Логируем скидку

            let finalAmount = totalPrice - discount;
            console.log('finalAmount: ', finalAmount); // Логируем финальную сумму

            // Обновление цены в поле priceDisplay
            if (priceDisplay) {
                console.log('3');
                priceDisplay.innerText = finalAmount.toFixed(2) + " ₽"; // Обновляем итоговую цену с учетом скидки
            }
        } else {
            console.log('Invalid count:', count);
            if (priceDisplay) {
                console.log('4')
                priceDisplay.innerText = '0.00 ₽'; // Если количество некорректно, отображаем 0
            }
        }
        console.log('5')
    }

    // Уменьшение количества
    decreaseBtn.addEventListener('click', function () {
        let currentValue = parseInt(numberInput.value);
        if (currentValue > minCount) {
            numberInput.value = currentValue - minCount;
            calc();
        }
    });

    // Увеличение количества
    increaseBtn.addEventListener('click', function () {
        let currentValue = parseInt(numberInput.value);
        if (currentValue < maxCount) {
            numberInput.value = currentValue + minCount;
            calc();
        }
    });

    // Обработчик для изменения промокода
    promocodeButton.addEventListener('click', function () {
        const promoCode = promocodeInput.value.trim();
        if (promoCode === "") {
            error.textContent = "Введите промокод";
            return;
        }

        // Выполняем запрос для проверки промокода
        fetch(`/promocode/${promoCode}/`, { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    error.textContent = data.error;
                } else {
                    // Применяем полученную скидку
                    promo = data.percent; // Применяем процент скидки
                    serviceData.setAttribute('data-promo', promo); // Обновляем атрибут data-promo
                    error.textContent = `Скидка: ${promo}%`; // Отображаем информацию о скидке
                    calc(); // Перерасчет итоговой цены с новой скидкой
                }
            })
            .catch(error => {
                error.textContent = "Ошибка при запросе";
                console.error('Ошибка:', error);
            });
    });

    // Изначальный расчет, если количество задано
    numberInput.addEventListener('input', calc);

    // Обработчик для потери фокуса (клик в другом месте)
    numberInput.addEventListener('blur', function () {
        let currentValue = parseInt(numberInput.value);

        // Если введенное значение меньше минимального, возвращаем минимальное значение
        if (currentValue < minCount) {
            numberInput.value = minCount;
        }
        // Если введенное значение больше максимального, возвращаем максимальное значение
        else if (currentValue > maxCount) {
            numberInput.value = maxCount;
        }

        // Перерасчет итоговой суммы
        calc();
    });

    // Первоначальный расчет после загрузки страницы
    calc();
});


function createOrder() {
    console.log('afsdgsdg')
    let serviceData = document.getElementById('serviceData');
    let count = document.getElementById('numberInput');
    let inputEmail = document.getElementById('inputEmail');
    let link_p = document.getElementById('urlInput');
    let promo = document.getElementById('promocode');
    let data = serviceData.dataset;
    let formData = new FormData();

    formData.append('service', data.serviceid);
    formData.append('count', count.value);
    formData.append('task_url', link_p.value);
    formData.append('promocode', promo.value);
    if (inputEmail) formData.append('email', inputEmail.value);

    let csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    formData.append('csrfmiddlewaretoken', csrfToken);

    fetch('/new-order/', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Произошла ошибка при создании заказа');
            }
        })
        .then(data => {
            // Проверяем ответ от сервера и если всё верно, выполняем редирект
            if (data.success) {
                window.location.href = '/order-confirmation/' + data.order_id;
                console.log('/order-confirmation/' + data.order_id)
            } else {
                // Сначала очищаем все поля ошибок
                document.querySelectorAll('.text-red-700').forEach(span => {
                    span.textContent = '';  // Очистим текст всех span с ошибками
                });

                // Маппинг полей ошибок на id элементов
                const errorMap = {
                    'count': 'count-error',
                    'task_url': 'url-error',
                    'email': 'email-error',
                    'promocode': 'promo-error'
                };

                // Пройдем по объекту ошибок и заполним соответствующие span
                for (let field in data.errors) {
                    if (data.errors.hasOwnProperty(field) && errorMap[field]) {
                        let spanId = errorMap[field];  // Получаем соответствующий ID span
                        let errorText = data.errors[field].join(', ');  // Собираем текст ошибок
                        let errorSpan = document.getElementById(spanId);  // Получаем элемент по ID

                        if (errorSpan) {
                            errorSpan.textContent = errorText;  // Вставляем текст ошибки
                        }
                    }
                }
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
}