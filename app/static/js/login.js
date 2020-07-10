async function login(username, password, token, tokenField) {
    let body = {
        username: username.value,
        password: password.value
    };
    if (!body.username.length > 0 && !body.password.length > 0) {
        setStatusMessage('Fill out all fields!', 'danger');
    }
    // check if 2fa token input field is visible and entered
    if (tokenField.style.display === 'block' && token !== null) {
        if (token.value.length === 6 && token.value.match(/^[0-9]+$/)) {
            body.token = token.value;
        } else {
            token.value = '';
            token.focus();
            token.select();
            setStatusMessage('Invalid 2fa token!', 'danger');
            return;
        }
    }

    const response = await fetch('/api/auth', {
        method: 'POST',
        body: JSON.stringify(body),
        headers: {
            'Content-Type': 'application/json'
        }
    });

    const data = await response.json()

    if (!response.ok) {
        switch (data.message) {
            case 'Invalid credentials':
                setStatusMessage('Invalid Credentials!', 'danger');

                // clear login fields
                username.value = '';
                username.readOnly = false;

                // focus to username input field
                username.focus();
                username.select();

                password.value = '';
                password.readOnly = false;

                if (token) {
                    token.value = '';
                }

                // hide 2fa input
                tokenField.style.display = 'none';
                break;
            case 'Missing 2fa token':
                // show field to enter 2fa token and set username and password field read only
                username.readOnly = true;
                password.readOnly = true;
                tokenField.style.display = 'block';

                if (token) {
                    // focus to token input field
                    token.focus();
                    token.select();
                }
                break;
        }

        console.log(response, data);
        return;
    }

    // clear login fields
    username.value = '';
    password.value = '';
    if (token) {
        token.value = '';
    }

    // set tokens as cookie
    setCookie('accessToken', data.accessToken, 15);
    setCookie('refreshToken', data.refreshToken, 360);

    window.location = '/';
}

async function logout() {
    const response = await fetch(`/api/auth/refresh/${getCookie('refreshToken')}`, {
        method: 'DELETE',
    });

    const data = await response.json()

    if (!response.ok) {
        console.log(response, data)
    }
    delCookie('accessToken');
    delCookie('refreshToken');

    window.location = '/login';
}
