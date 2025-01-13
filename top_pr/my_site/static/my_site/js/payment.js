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

// "flex items-center justify-between mt-3 mb-3 border border-gray-300 rounded p-2 ring-2 ring-blue-600"
// "flex items-center justify-between mt-3 mb-3 border border-gray-300 rounded p-2 hover:ring-2 hover:offset-blue-500"
}