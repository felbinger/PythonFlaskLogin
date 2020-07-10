async function enable2fa(token) {
    await refreshToken(async () => {
        if (token.length === 6 && token.match(/^[0-9]+$/)) {
            const response = await fetch('/api/users/2fa', {
                method: 'POST',
                body: JSON.stringify({
                    token: token
                }),
                headers: {
                    'Authorization': `Bearer ${getCookie('accessToken')}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json()

            if (!response.ok) {
                setStatusMessage('Token is invalid!', 'danger');
                console.log(response, data)
            }
            setStatusMessage('2FA has been enabled!');
            window.location = '/';
        } else {
            setStatusMessage("Token is invalid!", 'danger');
        }
    });
}

async function abort2faSetup() {
    await refreshToken(async () => {
        const response = await fetch('/api/users/2fa', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getCookie('accessToken')}`
            }
        });

        const data = await response.json()

        if (response.ok && data.data === '2fa secret has been disabled') {
            window.location = '/';
        } else {
            if (data.message) {
                setStatusMessage(data.message, 'danger');
            } else {
                console.log(response, data);
            }
        }
    });
}