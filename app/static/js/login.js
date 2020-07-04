function login(username, password, token, tokenField) {
    let data = {
        username: username.value,
        password: password.value
    };
    if (data.username.length > 0 && data.password.length > 0) {
        // check if 2fa token input field is visible and entered
        if (tokenField.style.display === 'block' && token !== null) {
            if (token.value.length === 6 && token.value.match(/^[0-9]+$/)) {
                data.token = token.value;
            } else {
                token.value = '';
                token.focus();
                token.select();
                setStatusMessage('Invalid 2fa token!', 'danger');
                return;
            }
        }
        // TODO use fetch api
        axios.post('/api/auth', data)
            .then((response) => {
                // clear login fields
                username.value = '';
                password.value = '';
                token.value = '';

                // set tokens as cookie
                setCookie('accessToken', response.data.accessToken, 15);
                setCookie('refreshToken', response.data.refreshToken, 360);

                //window.location = '/';

                // add tokens to flask session (TODO remove after refactor of application is complted)
                axios.post('/login', {
                    accessToken: response.data.accessToken,
                    refreshToken: response.data.refreshToken
                }).then((response) => {
                    if (response.status === 200) {
                        window.location = '/';
                    }
                }).catch((error) => {
                    console.log(error);
                });
            })
            .catch((error) => {
                if (error.response.data.message !== null) {
                    switch (error.response.data.message) {
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

                            token.value = '';

                            // hide 2fa input
                            tokenField.style.display = 'none';
                            break;
                        case 'Missing 2fa token':
                            // show field to enter 2fa token and set username and password field read only
                            username.readOnly = true;
                            password.readOnly = true;
                            tokenField.style.display = 'block';

                            // focus to token input field
                            token.focus();
                            token.select();
                            break;
                    }
                }
            });
    } else {
        setStatusMessage('Fill out all fields!', 'danger');
    }
}
