
let orderFormaCreate = document.getElementById('order')

var orderModal = document.getElementById('orderModal');
orderModal.addEventListener('show.bs.modal', function (event) {
    orderFormaCreate.count.value = '';
    orderFormaCreate.task_url.value = '';
    document.getElementById('price').textContent = '0 руб'
    orderFormaCreate.classList.remove('d-none');
    let orderFormConfirm = document.getElementById('pay');
    if (orderFormConfirm){
      orderFormConfirm.remove();
    }
    // Кнопка, запускающая модальное окно
    var button = event.relatedTarget;
    // Извлечь информацию из атрибутов data-bs- *
    var recipient = button.getAttribute('data-bs-whatever');

    var iconSrc = button.parentNode.parentNode.previousSibling.previousSibling.getElementsByTagName('img')[0].getAttribute('src');
    var select_elemt = document.getElementsByClassName('form-select select-elements')[0];
    var cat_id = button.getAttribute('data-cat-id');
    var sub_id = button.getAttribute('data-sub-id');

        // удаление всех элементов
    while (select_elemt.firstChild) {
      select_elemt.removeChild(select_elemt.firstChild);
    }
    // При необходимости вы можете инициировать запрос AJAX здесь
    // а затем выполните обновление в обратном вызове.
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/cat_id/' + cat_id + '/sub_id/' + sub_id);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.responseType = 'json';
    xhr.send();
    xhr.onload = function(){
      if (xhr.readyState === 4, xhr.status === 200){
        r_data = xhr.response.data_s;
        if (Object.keys( r_data ).length > 0){
          for (key in r_data){
            const element = r_data[key];  
            var newOption = document.createElement("option");
            newOption.innerText = `${element.name}: ${element.price} р.шт`;
            newOption.setAttribute('value', key);
            select_elemt.appendChild(newOption);
          };
          setServiceInfo(xhr.response.service_info)
        }else{
          console.log('False');
        };
      };
    };

    // Обновите содержимое модального окна.
    var modalTitle = orderModal.querySelector('.modal-title');
    var modalTitleImg = orderModal.querySelector('.modalTitleImg');
    var modalBodyInput = orderModal.querySelector('.modal-body input');
  
    modalTitleImg.setAttribute('src', iconSrc);
    modalTitle.textContent = recipient;
  });

orderModal.addEventListener('hidden.bs.modal', function (event) {
  document.getElementById('order-confirm-form').innerHTML = '';
});

function setStars(count, element){
  for (let i=0; i<count; i++){
    var newStarSpan = document.createElement("span");
    newStarSpan.setAttribute('class', 'mx-2');

    var newStarImg = document.createElement("img");
    newStarImg.setAttribute('src', '/static/my_site/img/star.svg');
    newStarImg.setAttribute('class', 'star');
    newStarSpan.innerHTML = newStarImg;
    element.innerHTML += '<span><img class="star" src="/static/my_site/img/star.svg" alt="star"></span>';
  }
}

function setServiceInfo(data){
  console.log(data)
  let speed = document.getElementById('id-speed');
  let quality = document.getElementById('id-quality');
  let textElement = document.getElementById('service-info-text');
  speed.innerHTML = '';
  quality.innerHTML = '';
  speed.textContent = 'Скорость:';
  quality.textContent = 'Качество:';

  setStars(data.speed, speed);
  setStars(data.quality, quality);

  if (data.is_cancellation){
    console.log('Есть отмена')
    textElement.innerHTML = '✅ Есть отмена<br><br>' +  data.text
  }else{
    console.log('Нет отмены')
    textElement.textContent = data.text
  }
}

function getURL(){
  var url = window.location.href;
  var arr = url.split("/");
  return arr[0] + "//" + arr[2];
};

function setErrors(errors, form){
  for (let field of form){
    if (field.name) {
      
      if (field.name in errors){
        field.classList.add('is-invalid');
        document.getElementById(field.name+'_error').textContent = errors[field.name][0];
      }else{
        field.classList.remove('is-invalid');
      };
    };
  }
}

class FormEvents {

  handleEvent(event) {
    if (event.type === 'change'){
      this.change(event)
    }else if(event.type === 'click' && event.target.id === 'btn-create-order'){
      this.submiteCreateOrder(event)
    }else if(event.type === 'click' && event.target.id === 'pay' && event.target.dataset.type === 'pay'){
      this.submitPay(event)
    }else if(event.type === 'click' && event.target.id === 'pay' && event.target.dataset.type === 'checked'){
      this.checkedPay(event)
    }

  }

  change(event){
    let inputCount = document.getElementById('id_count');
    let inputPromoCode = document.getElementById('id_promocode');
    let selectService = document.getElementById('id_service');

    if (event.target != inputCount && event.target != inputPromoCode && event.target != selectService){
      return;
    }
    let form = document.getElementById('order');
    let link = '/calculate/';
    let data = new FormData();
    for (let field of form){
      const {name} = field;
      if (field.name) {
        data.append(name, field.value);
      };
    };
    let xhr = new XMLHttpRequest();
    xhr.open('POST', getURL()+link);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.responseType = 'json';
    xhr.send(data);
    xhr.onload = function(){
      if (xhr.readyState === 4, xhr.status === 200 ){
        setServiceInfo(xhr.response.service_info)
        
        document.getElementById('price').textContent = xhr.response.price + ' руб'
        if (xhr.response.errors){
          setErrors(xhr.response.errors, form)
        }
      } else{
        window.location.href = getURL();
      };
    };

  };

  submiteCreateOrder(event){
    event.preventDefault();
    let form = document.getElementById('order');
    let link = form.getAttribute('action');
    let data = new FormData();
    for (let field of form){
      const {name} = field;
      if (field.name) {
        data.append(name, field.value);
      };
    };
    let xhr = new XMLHttpRequest();
    xhr.open('POST', getURL()+link);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.responseType = 'json';
    document.getElementById('btn-create-order').setAttribute('disabled', '');
    document.getElementById('btn-spinner').removeAttribute('hidden');
    xhr.send(data);
    xhr.onload = function(){
      if (xhr.readyState === 4, xhr.status === 200 ){
        if (xhr.response.errors){
          let errors = xhr.response.errors;
          setErrors(errors, form);
        }else{
          form.classList.add('d-none');
          var orderFormParent = document.getElementById('order-confirm-form');
          var newForm = xhr.response.ok.form;
          orderFormParent.innerHTML += newForm;
          
          let btnPayOrder = document.getElementById('pay')
          btnPayOrder.addEventListener('click', formEvents)
        };
      } else{
        window.location.href = getURL();
      };
      document.getElementById('btn-create-order').removeAttribute('disabled');
      document.getElementById('btn-spinner').setAttribute('hidden', '');
    };
  };
  submitPay(event){
    let xhr = new XMLHttpRequest();
    xhr.open('POST', getURL()+'/pay/');
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.responseType = 'json';
    var data = new FormData();
    data.append('order_id', event.target.dataset.orderId);
    xhr.send(data);
    xhr.onload = function(){
      if (xhr.readyState === 4, xhr.status === 200 ){
        if (xhr.response.error){
          let btn = document.getElementById('checked-error');
          btn.innerHTML = xhr.response.error;

        }else if(xhr.response.redirect && xhr.response.pay === 'PRF'){
          document.location = xhr.response.redirect;

        }else if(xhr.response.redirect && xhr.response.pay != 'PRF'){
          window.open(xhr.response.redirect, '_blank');
          let btnPay = document.getElementById('pay');
          btnPay.textContent = 'Проверить оплату';
          btnPay.setAttribute('data-type', 'checked');
        };
      };
    };
  };
  checkedPay(event){
    let btn = document.getElementById('checked-error');
    btn.innerHTML = '';
    btn.classList.add('loading');
    let xhr = new XMLHttpRequest();
    xhr.open('POST', getURL()+'/checkedpay/');
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.responseType = 'json';
    var data = new FormData();
    data.append('order_id', event.target.dataset.orderId)
    xhr.send(data);
    xhr.onload = function(){
      if (xhr.readyState === 4, xhr.status === 200 ){
        if (xhr.response.error){
          btn.classList.remove('loading');
          btn.innerHTML = xhr.response.error;
        }else if (xhr.response.redirect){
          document.location = xhr.response.redirect;
        };
      };
    };
  };
};
let formEvents = new FormEvents();
// Оформление заказа
let orderForm = document.getElementById('order')
orderForm.addEventListener('change', formEvents)
let btnCreateOrder = document.getElementById('btn-create-order')
btnCreateOrder.addEventListener('click', formEvents)
