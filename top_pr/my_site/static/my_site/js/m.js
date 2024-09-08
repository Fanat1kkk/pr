function getURL() {
    var url = window.location.href;
    var arr = url.split("/");
    return arr[0] + "//" + arr[2];
};

function setErrors(errors, form) {
    for (let field of form) {
        if (field.name) {
            if (field.name in errors) {
                field.classList.add('is-invalid');
                document.getElementById(field.name + '_error').textContent = errors[field.name][0];
            } else {
                field.classList.remove('is-invalid');
            };
        };
    }
};

// Вход
let btnLogIn = document.getElementById('btn-log-in');
btnLogIn.addEventListener('click', function (e) {
    e.preventDefault();
    form = document.getElementById('form-log-in');

    let data = new FormData();
    let link = form.getAttribute('action');
    for (let field of form) {
        const { name } = field;
        if (field.name) {
            data.append(name, field.value);
        };
    };
    let xhr = new XMLHttpRequest();
    xhr.open('POST', getURL() + link);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.responseType = 'json';
    xhr.send(data);
    xhr.onload = function () {
        if (xhr.readyState === 4, xhr.status === 200) {
            console.log('xhr.status ', xhr.status);
            console.log('xhr.response ', xhr.response);
            if (xhr.response.errors){
                console.log('errors block')
                let alert = document.getElementById('login-alert');
                alert.classList.remove('d-none');
            }else if(xhr.response.location){
                document.location.href = xhr.response.location;
            };
        };
    };
});

// Регистрация
let btnSignup = document.getElementById('btn-signup');
btnSignup.addEventListener('click', function(e){
    e.preventDefault();
    form = document.getElementById('form-signup');
    let data = new FormData();
    let link = form.getAttribute('action');
    for (let field of form) {
        const { name } = field;
        if (field.name) {
            data.append(name, field.value);
        };
    };
    let xhr = new XMLHttpRequest();
    xhr.open('POST', getURL() + link);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.responseType = 'json';
    xhr.send(data);
    xhr.onload = function () {
        if (xhr.readyState === 4, xhr.status === 200) {
            console.log('response: ', xhr.response);
            if (xhr.response.errors){
                setErrors(xhr.response.errors, form);
            }else if(xhr.response.location){
                document.location.href = xhr.response.location;
            };
        }
    }
});

// Выход
let navLogoutForm = document.getElementById('nav-logout');
if (navLogoutForm){
    navLogoutForm.addEventListener('click', function(e){
        e.preventDefault()
        let data = new FormData();
        let link = navLogoutForm.getAttribute('action');
        for (let field of navLogoutForm) {
            const { name } = field;
            if (field.name) {
                data.append(name, field.value);
            };
        };
        let xhr = new XMLHttpRequest();
        xhr.open('POST', getURL() + link);
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        xhr.responseType = 'json';
        xhr.send(data);
        xhr.onload = function () {
            if (xhr.readyState === 4, xhr.status === 200) {
                if (xhr.response.errors){
                    setErrors(xhr.response.errors, form)
                }else if(xhr.response.location){
                    document.location.href = xhr.response.location;
                };
            }
        }
    })
}


let btnNavLogin = document.getElementById('nav-login')
if (btnNavLogin){
    btnNavLogin.addEventListener('click', function(e){
        e.preventDefault();
        var loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
        loginModal.show();
    });
}

let btnSignupSelect = document.getElementById('btn-s-login');
btnSignupSelect.addEventListener('click', function(e){
    let loginWrap = document.getElementById('login-wrap');
    let signupWrap = document.getElementById('signup-wrap');
    let modalHead = document.getElementById('staticBackdropLabel');
    modalHead.textContent = 'Вход';
    loginWrap.classList.remove('d-none');
    signupWrap.classList.add('d-none');
});

let btnLoginSelect = document.getElementById('btn-s-signup');
btnLoginSelect.addEventListener('click', function(e){
    let loginWrap = document.getElementById('login-wrap');
    let signupWrap = document.getElementById('signup-wrap');
    let modalHead = document.getElementById('staticBackdropLabel');
    modalHead.textContent = 'Регистрация';
    loginWrap.classList.add('d-none');
    signupWrap.classList.remove('d-none');
});