let infoIcon = '<span class="fa fa-info-circle"></span>';

function setCookie(name, value, expired) {
    // expired in minutes
    let d = new Date();
    d.setTime(d.getTime() + (expired*60*1000));
    let expires = "expires="+ d.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function delCookie(name) {
    document.cookie = name+'=; Max-Age=-99999999;';
}

function validateEmail(email) {
    let re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function setStatusMessage(text, category='success') {
    // possible categories: success, warning, danger
    let field = document.getElementById('statusMsg');
    field.style.display = 'block';
    field.className = `alert alert-${category}`;
    field.innerHTML = `${infoIcon} ${text}`;
}

async function refreshToken(callback) {
    fetch('/api/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({
            refreshToken: getCookie('refreshToken')
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        response.json().then(data => {
            if (!response.ok) {
                console.log(response, data);
                return;
            }
            setCookie('accessToken', data.accessToken, '15');
            return callback();
        })
    });
}
