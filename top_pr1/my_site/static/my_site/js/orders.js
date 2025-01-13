function getURL(){
    var url = window.location.href;
    var arr = url.split("/");
    return arr[0] + "//" + arr[2];
};


let select = document.getElementById('sort_orders');
select.addEventListener('change', function (e){
    let url = getURL() + '/orders/sorting?email=' + select.dataset.email + '&status=' + select.value;
    document.location = url;
}
);


let table = document.getElementById('table')

table.addEventListener('click', function(e){
    let orderId = e.target.dataset.orderId;
    if (e.target.id.includes('btn_cancel_'+orderId)){
        if (e.target.dataset.auth === 'False'){
            alert('Для отмены заказа вам необходимо авторизоваться');
            return;
        };
        let csrf = e.target.dataset.csrf;
        let xhr = new XMLHttpRequest();
        xhr.open('POST', getURL() + '/order-cancel/');
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        xhr.setRequestHeader("X-CSRFToken", csrf);
        xhr.responseType = 'json';
        var data = new FormData();
        data.append('order_id', orderId);
        // data.append('csrf', csrf);
        document.getElementById('btn_cancel_'+orderId).setAttribute('disabled', '');
        document.getElementById('spin-' + orderId).removeAttribute('hidden');
        xhr.send(data);
        xhr.onload = function () {
            if (xhr.readyState === 4, xhr.status === 200) {
                console.log(xhr.response)
                if (xhr.response.status === 'WCL'){
                    document.getElementById('td_btn_'+orderId).innerHTML = '<p>Нет действий</p>';
                    document.getElementById('td_status_'+orderId).textContent = 'Отменяется';
                }
                // document.getElementById('btn_cancel').removeAttribute('disabled');
                // document.getElementById('spin-' + orderId).setAttribute('hidden', '');
            };
        };
    }else if(e.target.id.includes('btn_rate_' + orderId)){
        if (e.target.dataset.auth === 'False'){
            alert('Для оценки заказа вам необходимо авторизоваться');
            return;
        };
        window.open(getURL()+'/comment/'+orderId, '_blank')
    };
});

