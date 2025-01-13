function getURL(){
    var url = window.location.href;
    var arr = url.split("/");
    return arr[0] + "//" + arr[2];
  };


let btnPay = document.getElementById('pay_profile_btn');
btnPay.addEventListener('click', function (e) {
    let btn = e.currentTarget;
    let sum = document.getElementById('id_sum').value;
    let pay_provider = document.getElementById('id_pay_provider').value;
    if (btn.dataset.payUrl){
        window.open(btn.dataset.payUrl, '_blank');
        return
    }
    let xhr = new XMLHttpRequest();
    xhr.open('POST', getURL() + '/pay-profile/');
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.responseType = 'json';
    var data = new FormData();
    data.append('pay_provider', pay_provider);
    data.append('sum', sum);
    document.getElementById('pay_profile_btn').setAttribute('disabled', '');
    document.getElementById('btn-spinner-profile').removeAttribute('hidden');
    xhr.send(data);
    xhr.onload = function () {
        if (xhr.readyState === 4, xhr.status === 200) {
            if (xhr.response.redirect){
                window.open(xhr.response.redirect, '_blank');
                btn.dataset.payUrl = xhr.response.redirect;
            }else if(xhr.response.error){
                console.log('error: ', xhr.response.error);
                let error = document.getElementById('pay_error');
                error.textContent = xhr.response.error;
            };
            document.getElementById('pay_profile_btn').removeAttribute('disabled');
            document.getElementById('btn-spinner-profile').setAttribute('hidden', '');
        };
    };
});


let inputSum = document.getElementById('id_sum');
inputSum.addEventListener('change', function(e){
    let btn = document.getElementById('pay_profile_btn')
    if (btn.dataset.payUrl){
        delete btn.dataset.payUrl
    }
})

let selectPay = document.getElementById('id_pay_provider');
selectPay.addEventListener('change', function(e){
    let btn = document.getElementById('pay_profile_btn')
    if (btn.dataset.payUrl){
        delete btn.dataset.payUrl
    }
})