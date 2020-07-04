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

let config = () => {
    return {
        headers: {
            'Authorization': `Bearer ${getCookie('accessToken')}`,
            'Content-Type': 'application/json'
        }
    };
};

function logout() {
    axios.delete(`/api/auth/refresh/${getCookie('refreshToken')}`)
        .then((response) => {
            if (response.status === 200) {
                delCookie('accessToken');
                delCookie('refreshToken');
                // remove token from flask session cookie
                axios.post(`/logout`);
                window.location = '/login';
            } else {
                console.log(response.data)
            }
        })
        .catch((error) => {
            console.log(error.response.data)
        });
}

function enable2fa(token) {
    refreshToken(() => {
        if (token.length === 6 && token.match(/^[0-9]+$/)) {
            axios.post('/api/users/2fa', {
                token: token
            }, config()).then((response) => {
                if (response.status === 200) {
                    window.location = '/';
                    setStatusMessage('2FA has been enabled!');
                } else {
                    setStatusMessage('Token is invalid!', 'danger');
                }
            }).catch((error) => {
                if (error && error.response && error.response.data && error.response.data.message) {
                    setStatusMessage('Token is invalid!', 'danger');
                } else {
                    console.log(error);
                }
            });
        } else {
            setStatusMessage("Token is invalid!", 'danger');
        }
    });
}

function abort2faSetup() {
    refreshToken(() => {
        axios.delete('/api/users/2fa', {
            headers: {
                'Authorization': `Bearer ${getCookie('accessToken')}`
            }
        }).then(response => {
            if (response.status === 200 && response.data.data === '2fa secret has been disabled') {
                window.location = '/'
            }
        }).catch(error => {
            if (error && error.response && error.response.data && error.response.data.message) {
                setStatusMessage(error.response.data.message, 'danger');
            } else {
                console.log(error)
            }
        });
    });
}

function modifyProfile(displayName, email, totp, totpToken=null) {
    refreshToken(() => {
        // check if the entered email address is valid
        if (!validateEmail(email)) {
            setStatusMessage('Invalid E-Mail address!', 'danger');
        } else {
            axios.put('/api/users/me', {
                displayName: displayName,
                email: email,
                totp_enabled: totp,
                totp_token: totpToken
            }, config()).then((response) => {
                if (response.status === 200) {
                    setStatusMessage('Profile has been saved!');
                    // if 2fa has been disabled, hide input field for the token
                    if (!totp && document.getElementById("disable2fa")) {
                        document.getElementById("disable2fa").style.display = 'none';
                    }
                    if (response.data.data.hasOwnProperty('2fa_secret')) {
                        // @Security possible security vulnerability - todo find another way to setup 2fa
                        setCookie('2faSecret', response.data.data['2fa_secret'], 10);
                        window.location = '/2fa';
                    }
                } else {
                    console.log(response);
                }
            }).catch((error) => {
                if (error && error.response && error.response.data && error.response.data.message) {
                    setStatusMessage(error.response.data.message, 'danger');
                } else {
                    console.log(error)
                }
            });
        }
    });
}

function changePassword(password, password2) {
    refreshToken(() => {
        // check if the passwords are equal
        if (password !== password2) {
            setStatusMessage('The entered passwords are not the same!', 'danger');
        } else {
            // check if the password fits the requirements (min. 8 characters)
            if (password.length < 8) {
                setStatusMessage('Password is too short!', 'danger');
            } else {
                axios.put('/api/users/me', {
                    password: password
                }, config()).then((response) => {
                    if (response.status === 200) {
                        setStatusMessage('Password has been updated!');
                    } else {
                        console.log(response.data);
                    }
                }).catch((error) => {
                    if (error && error.response && error.response.data && error.response.data.message) {
                        setStatusMessage(error.response.data.message, 'danger');
                    } else {
                        console.log(error)
                    }
                });
            }
        }
    });
}

function refreshToken(callback) {
    axios.post('/api/auth/refresh', {
        refreshToken: getCookie('refreshToken')
    }).then((response) => {
        if (response.status === 200) {
            setCookie('accessToken', response.data.accessToken, '15');
            return callback();
        } else {
            console.log(response.data)
        }
    }).catch((error) => {
        if (error && error.response && error.response.data && error.response.data.message) {
            if (error.response.data.message === 'Invalid refresh token') {
                // refresh token is invalid if not already jumped out
                delCookie('refreshToken');
                delCookie('accessToken');
                window.location = '/login'
            } else {
                console.log(error.response.data.message)
            }
        } else {
            console.log(error);
        }
    });
}
