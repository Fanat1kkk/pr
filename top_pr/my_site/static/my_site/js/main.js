function toggleMenu() {
    const burger = document.querySelector('#burger');
    const links = document.querySelector('.nav-links');
    const header = document.querySelector('#header');

    burger.addEventListener('click', () => {
        burger.classList.toggle('active');
        if (links.classList.contains('hidden')) {
            links.classList.remove('hidden');
            header.classList.toggle('bg-with')
            links.style.top = `${header.getBoundingClientRect().height}px`; // Показываем с отступом
        } else {
            links.style.top = '-100vh'; // Скрываем
            setTimeout(() => links.classList.add('hidden'), 500); // Скрываем класс после анимации
        }
    });
}

function handleScroll() {
    const header = document.getElementById('header');
    const isScrolled = window.scrollY > 50;

    if (isScrolled) {
        header.classList.add('bg-white', 'shadow-md');
    } else {
        header.classList.remove('bg-white', 'shadow-md');
        header.classList.add('bg-gray-100');
    }
};

function accordion() {
    document.querySelectorAll('button[id^="toggle"]').forEach(button => {
        button.addEventListener('click', () => {
            const content = document.getElementById(`content${button.id.slice(-1)}`);
            const icon = document.getElementById(`icon${button.id.slice(-1)}`);

            content.classList.toggle('hidden');
            icon.classList.toggle('rotate-180'); // Поворачиваем на 180 градусов
        });
    });

}

// Инициализация
toggleMenu();
accordion();
window.addEventListener('scroll', handleScroll);