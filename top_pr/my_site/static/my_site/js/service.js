// Функция для отправки запроса и обновления опций в "Услуге"
function fetchAndUpdateServices(slug) {
    fetch(`/categories/${slug}/`)
        .then(response => response.json())
        .then(data => {
            const serviceOptions = document.getElementById('serviceOptions');
            serviceOptions.innerHTML = ''; // Очищаем текущие опции

            if (data.length > 0) {
                const firstService = data[0];
                const serviceIcon = document.getElementById('serviceIcon');
                const serviceText = document.getElementById('serviceText');

                serviceIcon.src = `/static/my_site/img/${firstService.icon}`;
                serviceText.innerText = firstService.name;

                const selectServiceElement = document.getElementById('service');
                selectServiceElement.setAttribute('data-selectSocial', firstService.slug);
                // Вызываем fetchTariffs для обновления карточек тарифов
                const selectedSocial = document.getElementById('socialNetwork').getAttribute('data-selectSocial');
                if (selectedSocial && firstService.slug) {
                    fetchTariffs(selectedSocial, firstService.slug);
                }
            }

            data.forEach(service => {
                const serviceOption = document.createElement('div');
                serviceOption.classList.add('flex', 'items-center', 'p-2', 'cursor-pointer', 'hover:bg-gray-100');
                serviceOption.setAttribute('data-value', service.slug);
                serviceOption.setAttribute('data-icon', `img/${service.icon}`);

                const serviceImg = document.createElement('img');
                serviceImg.classList.add('w-5', 'h-5', 'mr-2');
                serviceImg.src = `/static/my_site/img/${service.icon}`;
                serviceImg.alt = service.name;

                const serviceName = document.createElement('span');
                serviceName.innerText = service.name;

                serviceOption.appendChild(serviceImg);
                serviceOption.appendChild(serviceName);
                serviceOptions.appendChild(serviceOption);
            });
        })
        .catch(error => console.error('Error fetching services:', error));
}

// Функция для отправки запроса с выбранной социальной сетью и услугой
function fetchTariffs(social, service) {
    fetch(`/uslugi/${social}/${service}/`)
        .then(response => response.json())
        .then(data => {
            updateTariffCards(data); // Обновляем карточки тарифов
        })
        .catch(error => console.error('Ошибка при получении тарифов:', error));
}

// Функция для создания и добавления карточек тарифов
function updateTariffCards(tariffs) {
    const container = document.getElementById('tariffCardsContainer');
    container.innerHTML = ''; // Очищаем контейнер

    tariffs.forEach(service => {
        // Создаем карточку
        const card = document.createElement('div');
        card.classList.add('bg-white', 'shadow-lg', 'rounded-lg', 'p-6');

        // Внутренние элементы карточки
        card.innerHTML = `
            <div class="flex flex-col items-center flex-grow">
                <img src="/static/my_site/img/${service.category.icon}" alt="${service.category.cat_name}" class="w-10 h-10 mb-4">
                <h3 class="text-lg font-semibold text-gray-800 mb-2">${service.category.cat_name} ${service.category.sub_cat_name}</h3>
                <h3 class="text-lg font-semibold text-gray-800 mb-2">${service.name}</h3>
                <p class="text-gray-500 mb-4">Цена за 1000 шт: ${Math.round(service.price)} ₽</p>
                <p class="text-sm text-center text-gray-600 mb-6">${service.text_pre_info}</p>
            </div>
            <div class="flex flex-col">
                <button onclick="window.open('/create-order/${service.slug}/', '_blank')" class="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-lg transition duration-300">Заказать</button>
                <button onclick="openModal(event)" data-info='${service.text_info}' data-speedDay="${service.speed_day}" class="bg-gray-300 hover:bg-gray-400 text-gray-800 mt-3 py-2 px-4 rounded-lg transition duration-300">Подробнее</button>
            </div>
        `;

        // Добавляем карточку в контейнер
        container.appendChild(card);
    });
}

// Открыть и закрыть список опций
function toggleOptions(element, optionsId, otherOptionsId, iconCheckId) {
    const options = document.getElementById(optionsId);
    const otherOptions = document.getElementById(otherOptionsId);
    const iconCheck = document.getElementById(iconCheckId);

    if (!otherOptions.classList.contains('hidden')) {
        closeOptions(otherOptionsId, iconCheckId);
    }

    options.classList.toggle('hidden');
    iconCheck.classList.toggle('rotate-180');
}

function closeOptions(optionsId, iconCheckId) {
    const options = document.getElementById(optionsId);
    const iconCheck = document.getElementById(iconCheckId);
    options.classList.add('hidden');
    iconCheck.classList.remove('rotate-180');
}

function selectOption(optionElement, iconId, textId, optionsId, dataSelectId, iconCheckId) {
    const iconSrc = optionElement.querySelector('img').src;
    const text = optionElement.querySelector('span').innerText;
    const value = optionElement.getAttribute('data-value');

    const iconElement = document.getElementById(iconId);
    const textElement = document.getElementById(textId);

    iconElement.src = iconSrc;
    textElement.innerText = text;

    const selectSocialElement = document.getElementById(dataSelectId);
    selectSocialElement.setAttribute('data-selectSocial', value);

    closeOptions(optionsId, iconCheckId);
}

document.getElementById('socialNetwork').addEventListener('click', function (event) {
    event.stopPropagation();
    toggleOptions(this, 'socialNetworkOptions', 'serviceOptions', 'socialNetworkIconCheck');
});

document.getElementById('service').addEventListener('click', function (event) {
    event.stopPropagation();
    toggleOptions(this, 'serviceOptions', 'socialNetworkOptions', 'serviceIconCheck');
});

document.getElementById('socialNetworkOptions').addEventListener('click', function (event) {
    event.stopPropagation();
    const option = event.target.closest('[data-value]');
    if (option) {
        selectOption(option, 'socialNetworkIcon', 'socialNetworkId', 'socialNetworkOptions', 'socialNetwork', 'socialNetworkIconCheck');
        const selectedSlug = option.getAttribute('data-value');
        fetchAndUpdateServices(selectedSlug);
    }
});

document.getElementById('serviceOptions').addEventListener('click', function (event) {
    event.stopPropagation();
    const option = event.target.closest('[data-value]');
    if (option) {
        selectOption(option, 'serviceIcon', 'serviceText', 'serviceOptions', 'service', 'serviceIconCheck');

        const selectedSocial = document.getElementById('socialNetwork').getAttribute('data-selectSocial');
        const selectedService = option.getAttribute('data-value');

        if (selectedSocial && selectedService) {
            fetchTariffs(selectedSocial, selectedService);
        }
    }
});

document.addEventListener('click', function () {
    closeOptions('socialNetworkOptions', 'socialNetworkIconCheck');
    closeOptions('serviceOptions', 'serviceIconCheck');
});


// // Открытие модального окна
// function openModal(event) {
//     const modal = document.getElementById('modal');
//     let textInfo = document.getElementById('textInfo');
//     let speedDay = document.getElementById('speedDay');
//     speedDay.innerHTML = `До ${event.target.dataset.speedday} в день.`
//     textInfo.innerHTML = event.target.dataset.info
//     modal.classList.remove('hidden');
//     modal.classList.add('flex');
// }

// // Закрытие модального окна
// function closeModal(event) {
//     const modal = document.getElementById('modal');
//     if (!event || event.target === modal) {
//         modal.classList.add('hidden');
//         modal.classList.remove('flex');
//     }
// }



// Открытие модального окна
function openModal(event) {
    const modal = document.getElementById('modal');
    const textInfo = document.getElementById('textInfo');
    const speedDay = document.getElementById('speedDay');

    speedDay.innerHTML = `До ${event.target.dataset.speedday} в день.`;
    textInfo.innerHTML = event.target.dataset.info;

    modal.classList.remove('hidden', 'opacity-0');
    modal.classList.add('flex', 'opacity-100', 'transition-opacity', 'duration-300');
}

// Закрытие модального окна
function closeModal(event) {
    const modal = document.getElementById('modal');
    if (!event || event.target === modal) {
        modal.classList.remove('opacity-100');
        modal.classList.add('opacity-0');
        setTimeout(() => {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }, 300); // Длительность должна совпадать с `duration-300`
    }
}
