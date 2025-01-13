function toggleMenu() {
    const burger = document.querySelector('#burger');
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('overlay');

    // Функция для открытия/закрытия меню
    burger.addEventListener('click', () => {
        burger.classList.toggle('active');
        menu.classList.toggle('-translate-x-full');
        menu.classList.toggle('translate-x-0');
        overlay.classList.toggle('hidden'); // Показать или скрыть затемнение
    });

    // Закрытие меню при клике на overlay (вне меню)
    overlay.addEventListener('click', () => {
        menu.classList.add('-translate-x-full');
        menu.classList.remove('translate-x-0');
        burger.classList.toggle('active');
        overlay.classList.add('hidden'); // Скрыть затемнение
    });
}


function handleScroll() {
    console.log("Profile")
    const header = document.getElementById('header');
    const isScrolled = window.scrollY > 50;

    if (isScrolled) {
        header.classList.add('bg-white', 'shadow-md');
    } else {
        header.classList.remove('bg-white', 'shadow-md');
        header.classList.add('bg-gray-100');
    }
};

window.addEventListener('scroll', handleScroll);
toggleMenu();