async function modifyProfile(displayName, email, totp, totpToken=null) {
    await refreshToken(async () => {
        // check if the entered email address is valid
        if (!validateEmail(email)) {
            setStatusMessage('Invalid E-Mail address!', 'danger');
        } else {
            const response = await fetch('/api/users/me', {
                method: 'PUT',
                body: JSON.stringify({
                    displayName: displayName,
                    email: email,
                    totp_enabled: totp,
                    totp_token: totpToken
                }),
                headers: {
                    'Authorization': `Bearer ${getCookie('accessToken')}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json()

            if (!response.ok) {
                console.log(response, data);
                return;
            }
            setStatusMessage('Profile has been saved!');

            // if 2fa has been disabled, hide input field for the token
            if (!totp && document.getElementById("disable2fa")) {
                document.getElementById("disable2fa").style.display = 'none';
            }

            if (data.data.hasOwnProperty('2fa_secret')) {
                // @Security possible security vulnerability
                setCookie('2faSecret', data.data['2fa_secret'], 10);
                window.location = '/2fa';
            }
        }
    });
}

async function changePassword(password, password2) {
    await refreshToken(async () => {
        // check if the passwords are equal
        if (password !== password2) {
            setStatusMessage('The entered passwords are not the same!', 'danger');
        } else {
            // check if the password fits the requirements (min. 8 characters)
            if (password.length < 8) {
                setStatusMessage('Password is too short!', 'danger');
                return;
            }
            const response = await fetch('/api/users/me', {
                method: 'PUT',
                body: JSON.stringify({
                    password: password
                }),
                headers: {
                    'Authorization': `Bearer ${getCookie('accessToken')}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();


            if (!response.ok) {
                console.log(response, data);
                return;
            }
            setStatusMessage('Password has been updated!');

            // if 2fa has been disabled, hide input field for the token
            if (!totp && document.getElementById("disable2fa")) {
                document.getElementById("disable2fa").style.display = 'none';
            }

            if (data.data.hasOwnProperty('2fa_secret')) {
                // @Security possible security vulnerability
                setCookie('2faSecret', data.data['2fa_secret'], 10);
                window.location = '/2fa';
            }
        }
    });
}