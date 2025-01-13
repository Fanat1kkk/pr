
document.addEventListener('DOMContentLoaded', () => {
    // const tariffInfo = document.getElementById('tariffInfo');
    calc()
    const elements = [
        {
            div: document.getElementById('socialNetwork'),
            text: document.getElementById('socialNetworkText'),
            icon: document.getElementById('socialNetworkIcon'),
            options: document.getElementById('socialNetworkOptions'),
            checkIcon: document.getElementById('socialNetworkIconCheck')
        },
        {
            div: document.getElementById('service'),
            text: document.getElementById('serviceText'),
            icon: document.getElementById('serviceIcon'),
            options: document.getElementById('serviceOptions'),
            checkIcon: document.getElementById('serviceIconCheck')
        },
        {
            div: document.getElementById('tariff'),
            infoText: document.getElementById('infoText'),
            options: document.getElementById('tariffOptions'),
            checkIcon: document.getElementById('tariffIconCheck'),
            numberInput: document.getElementById('numberInput')
        }
    ];

    let openOptionsDiv = null; // Переменная для хранения открытого списка

    function setTariffLoadingState(isLoading) {
        let tariffElement = document.getElementById('tariff');
        let service = document.getElementById('service');
        let socialNetwork = document.getElementById('socialNetwork');

        if (isLoading) {
            tariffElement.classList.add('opacity-50', 'pointer-events-none', 'bg-gray-200'); // Делаем поле неактивным
            service.classList.add('opacity-50', 'pointer-events-none', 'bg-gray-200');
            socialNetwork.classList.add('opacity-50', 'pointer-events-none', 'bg-gray-200');
        } else {
            tariffElement.classList.remove('opacity-50', 'pointer-events-none', 'bg-gray-200'); // Убираем неактивное состояние
            service.classList.remove('opacity-50', 'pointer-events-none', 'bg-gray-200');
            socialNetwork.classList.remove('opacity-50', 'pointer-events-none', 'bg-gray-200');
        }
    }

    // Функция для управления отображением опций
    function toggleOptions(optionsDiv, checkIcon) {
        // Закрываем предыдущий открытый список
        if (openOptionsDiv && openOptionsDiv !== optionsDiv) {
            closeOptions(openOptionsDiv);
        }

        // Переключаем текущий список
        optionsDiv.classList.toggle('hidden');
        if (checkIcon) checkIcon.classList.toggle('rotate-180');

        // Обновляем переменную открытого списка
        openOptionsDiv = optionsDiv.classList.contains('hidden') ? null : optionsDiv;
    }

    // Функция для закрытия опций
    function closeOptions(optionsDiv) {
        optionsDiv.classList.add('hidden');
        const checkIcon = elements.find(e => e.options === optionsDiv)?.checkIcon;
        if (checkIcon) checkIcon.classList.remove('rotate-180');
    }

    // Функция для получения данных с API
    // function fetchServices(socialNetworkSlug) {
    //     fetch(`http://127.0.0.1:8000/cat/${socialNetworkSlug}/`)
    //         .then(response => response.json())
    //         .then(data => {
    //             updateServices(data);
    //             updateServiceSelectOption(data)
    //         })
    //         .catch(error => console.error('Ошибка при получении данных:', error));
    // }

    async function fetchServices(socialNetworkSlug) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/cat/${socialNetworkSlug}/`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка при получении данных:', error);
        }
    }

    async function fetchTariffs(social, service) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/cat/${social}/sub/${service}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка при получении данных:', error);
        }
    }

    // Обновление данных выброной опции сервиса
    function updateServiceSelectOption(data) {
        let text = elements[1].text
        let icon = elements[1].icon

        // // Обновляем данные, если они есть
        text.innerText = data[0].name;
        icon.src = '/static/my_site/img/' + data[0].icon;
        text.setAttribute('data-value', data[0].slug);
    }

    function updateTariffOptions(tariff) {
        let tariffOptions = document.getElementById('tariffOptions');

        let span = document.createElement('span');
        span.innerText = tariff.name + ' (' + tariff.price + ' руб./шт)';

        // Создаем tariffOption и добавляем атрибуты
        let tariffOption = document.createElement('div');
        tariffOption.classList.add('flex', 'items-center', 'p-2', 'cursor-pointer', 'hover:bg-gray-100');
        tariffOption.setAttribute('option', '');
        tariffOption.setAttribute('data-value', tariff.service_id);
        tariffOption.setAttribute('data-price', tariff.price);
        tariffOption.setAttribute('data-mincount', tariff.min_count);
        tariffOption.setAttribute('data-maxcount', tariff.max_count);
        tariffOption.setAttribute('data-desc', tariff.text_info);

        // Добавляем span в tariffOption
        tariffOption.appendChild(span);

        tariffOptions.appendChild(tariffOption);
    }

    function updateSelectTariffOption(data) {
        console.log(data)
        let infoText = elements[2].infoText;
        let discription = document.getElementById('tariffDiscription');
        let infoCount = document.getElementById('infoCount');
        let numberInput = document.getElementById('numberInput');
        let link = document.getElementById('link_p');

        infoText.innerHTML = `${data.name} (${data.price}руб./шт)`;
        link.placeholder = data.link_p;
        infoText.setAttribute('data-value', data.service_id);
        infoText.setAttribute('data-price', data.price);
        infoText.setAttribute('data-mincount', data.min_count);
        infoText.setAttribute('data-maxcount', data.max_count);
        discription.innerHTML = data.text_info;
        infoCount.innerHTML = `Лимиты: от ${data.min_count} до ${data.max_count}`;
        numberInput.value = data.min_count;

        calc()
    }

    // Обновляем услуги и тарифы на основе ответа с сервера
    function updateServices(data) {

        const serviceOptions = document.getElementById('serviceOptions');
        const tariffOptions = document.getElementById('tariffOptions');

        // Очищаем старые данные опций
        serviceOptions.innerHTML = '';
        tariffOptions.innerHTML = '';

        // Обновляем услуги
        data.forEach(serviceCategory => {
            // Создаем img элемент
            let img = document.createElement('img');
            img.classList.add('w-5', 'h-5', 'mr-2');
            img.src = '/static/my_site/img/' + serviceCategory.icon;
            img.alt = serviceCategory.name;

            // Создаем span элемент
            let span = document.createElement('span');
            span.innerText = serviceCategory.name;

            // Создаем serviceOption и добавляем атрибуты
            let serviceOption = document.createElement('div');
            serviceOption.classList.add('flex', 'items-center', 'p-2', 'cursor-pointer', 'hover:bg-gray-100');
            serviceOption.setAttribute('option', '');
            serviceOption.setAttribute('data-value', serviceCategory.slug);
            serviceOption.setAttribute('data-icon', '/static/my_site/img/' + serviceCategory.icon);

            // Добавляем img и span в serviceOption
            serviceOption.appendChild(img);
            serviceOption.appendChild(span);

            serviceOptions.appendChild(serviceOption);
        });

        // Обновляем тарифы (если применимо)
        // Здесь вы можете обновлять тарифы, если API возвращает данные о тарифах.
        if (data[0].services.length > 0) {
            data[0].services.forEach(tariff => {
                updateTariffOptions(tariff)
            });
            updateSelectTariffOption(data[0].services[0])
        }

    }

    // Обработчики кликов на выпадающие списки
    elements.forEach(({ div, options, checkIcon, text, infoText, icon, numberInput }) => {

        div.addEventListener('click', (event) => {
            event.stopPropagation(); // Останавливаем всплытие события
            toggleOptions(options, checkIcon);
        });

        // Делегирование событий: обработчик кликов на опции
        options.addEventListener('click', async (event) => {
            const option = event.target.closest('[option]');
            if (!option) return; // Проверяем, что клик был именно на элемент с атрибутом [option]

            if (text) text.innerText = option.innerText.trim();
            if (icon) icon.src = option.getAttribute('data-icon');

            if (option.parentNode.id === 'socialNetworkOptions') {
                setTariffLoadingState(true);
                let socialNetworkSlug = option.getAttribute('data-value');
                text.setAttribute('data-value', socialNetworkSlug);
                let data = await fetchServices(socialNetworkSlug); // Запрос на сервер при выборе соцсети
                updateServices(data);
                updateServiceSelectOption(data)
            }

            if (option.parentNode.id === 'serviceOptions') {
                setTariffLoadingState(true);
                let serviceNetworkSlug = option.getAttribute('data-value');
                let socialNetworkSlug = elements[0].text.getAttribute('data-value');
                let tariffOptions = document.getElementById('tariffOptions');
                tariffOptions.innerHTML = '';

                text.setAttribute('data-value', serviceNetworkSlug);
                let data = await fetchTariffs(socialNetworkSlug, serviceNetworkSlug);

                if (data.length > 0) {
                    data.forEach(tariff => {
                        updateTariffOptions(tariff);
                    })
                    updateSelectTariffOption(data[0])
                } else {
                    let textTarif = document.getElementById('infoText');
                    let discription = document.getElementById('tariffDiscription');
                    let link = document.getElementById('link_p');
                    discription.innerHTML = '---------';
                    textTarif.innerHTML = '---------';
                    link.placeholder = '---------';
                }
            }

            setTariffLoadingState(false);

            if (option.parentNode.id == 'tariffOptions') {
                // Получаем данные из атрибутов
                const value = option.getAttribute('data-value');
                const price = option.getAttribute('data-price');
                const minCount = option.getAttribute('data-mincount');
                const maxCount = option.getAttribute('data-maxcount');
                const desc = option.getAttribute('data-desc');

                let tarifDesc = document.getElementById('tariffDiscription');
                let infoCount = document.getElementById('infoCount');

                if (desc) tarifDesc.innerHTML = desc;
                infoCount.innerHTML = `Лимиты: от ${minCount} до ${maxCount}`

                if (infoText) infoText.innerHTML = option.innerText.trim();
                if (infoText) infoText.setAttribute('data-value', value);
                if (infoText) infoText.setAttribute('data-price', price);
                if (infoText) infoText.setAttribute('data-mincount', minCount);
                if (infoText) infoText.setAttribute('data-maxcount', maxCount);
                calc()
            }

            // Закрываем список после выбора
            closeOptions(options);
            openOptionsDiv = null; // Сбрасываем переменную открытого списка
            event.stopPropagation(); // Останавливаем всплытие события
        });
    });

    // Закрытие открытых опций при клике вне списка
    document.addEventListener('click', () => {
        if (openOptionsDiv) {
            closeOptions(openOptionsDiv);
            openOptionsDiv = null; // Сбрасываем переменную
        }
    });
});

// Функция для расчёта стоимости
function calc() {
    // Рассчёт стоимости
    const finalPrice = document.getElementById('finalPrice');

    // Используем parseFloat для получения значения цены с дробной частью
    const price = parseFloat(document.getElementById('infoText').getAttribute('data-price').replace(',', '.')); // Извлекаем цену из атрибута data-price

    // Получаем количество
    const count = parseInt(document.getElementById('numberInput').value); // Количество остаётся целым числом

    let promo = parseFloat(document.getElementById('infoText').getAttribute('data-promo'));

    // Обновляем итоговую цену, если цена и количество корректны
    if (!isNaN(price) && !isNaN(count)) {
        let totalPrice = count * price;
        if (promo) {
            let discount = totalPrice * (promo / 100); // Рассчитываем сумму скидки
            finalPrice.innerText = (totalPrice - discount).toFixed(2); // Вычитаем скидку и форматируем до 2 знаков после запятой
        } else {
            finalPrice.innerText = totalPrice.toFixed(2); // Форматируем до 4 знаков после запятой для точных цен
        }

    } else {
        console.log('Ошибка: некорректное значение цены или количества.');
    }
};

document.addEventListener('DOMContentLoaded', function () {
    let btn = document.getElementById('btn-promo');
    let error = document.getElementById('promo-error');

    btn.addEventListener('click', function () {
        let promo = document.getElementById('promocode').value.trim();
        if (promo === "") {
            error.textContent = "Введите промокод";
            return;
        }

        fetch(`/promocode/${promo}/`, { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    error.textContent = data.error;
                } else {
                    document.getElementById('infoText').setAttribute('data-promo', data.percent)
                    calc()
                    error.textContent = `Скидка: ${data.percent}%`;
                }
            })
            .catch(error => {
                error.textContent = "Ошибка при запросе";
                console.error('Ошибка:', error);
            });
    })

});

document.addEventListener('DOMContentLoaded', function () {
    const servicInfo = document.getElementById('infoText');
    const numberInput = document.getElementById('numberInput');
    const increaseButton = document.getElementById('increase');
    const decreaseButton = document.getElementById('decrease');


    // Получаем min и max значения динамически
    function getMinMax() {
        const minCount = parseInt(servicInfo.getAttribute('data-mincount'));
        const maxCount = parseInt(servicInfo.getAttribute('data-maxcount'));
        return { minCount, maxCount };
    }

    // Функция увеличения числа
    increaseButton.addEventListener('click', () => {
        if (!increaseButton.classList.contains('text-gray-200')) {
            decreaseButton.classList.remove('bg-gray-200')
            increaseButton.classList.add('bg-gray-200')
        }
        const { minCount, maxCount } = getMinMax()
        let currentValue = parseInt(numberInput.value) || minCount;
        if (currentValue < maxCount) {
            numberInput.value = currentValue + minCount; // Увеличиваем на шаг
            calc(); // Пересчёт
        }
    });

    // Функция уменьшения числа
    decreaseButton.addEventListener('click', () => {
        if (!decreaseButton.classList.contains('text-gray-200')) {
            increaseButton.classList.remove('bg-gray-200')
            decreaseButton.classList.add('bg-gray-200')
        }
        const { minCount, maxCount } = getMinMax()
        let currentValue = parseInt(numberInput.value) || minCount;
        if (currentValue > minCount) {
            numberInput.value = currentValue - minCount; // Уменьшаем на шаг
            calc(); // Пересчёт
        }
    });

    // Ограничение ввода только цифрами и проверка на допустимый диапазон
    numberInput.addEventListener('input', () => {
        // Ограничиваем ввод только числами
        numberInput.value = numberInput.value.replace(/[^0-9]/g, '');

        calc(); // Пересчёт
    });

    // Проверка при потере фокуса
    numberInput.addEventListener('blur', () => {
        let currentValue = parseInt(numberInput.value) || minCount;
        const { minCount, maxCount } = getMinMax()
        // Если значение выходит за пределы диапазона, сбрасываем его на допустимое значение
        if (currentValue < minCount) {
            numberInput.value = minCount;
        } else if (currentValue > maxCount) {
            numberInput.value = maxCount;
        }

        calc(); // Пересчёт
    });
});

function createOrder() {
    let infoText = document.getElementById('infoText');
    let count = document.getElementById('numberInput');
    let inputEmail = document.getElementById('inputEmail');
    let link_p = document.getElementById('link_p');
    let promo = document.getElementById('promocode');
    let data = infoText.dataset;
    let formData = new FormData();

    formData.append('service', data.value);
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
                window.location.href = '/profile/order/' + data.order_id;
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