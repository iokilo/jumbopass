// ─── Login Page ───────────────────────────────────────────────────────────────

const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            // step 1: verify password
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success) {
                // password correct, show RFID prompt and start polling
                document.getElementById('rfid-prompt').style.display = 'block';
                loginForm.querySelector('button[type="submit"]').disabled = true;
                pollLoginRFID(data.user_id);
            } else {
                alert('Incorrect username or password. Try again.');
            }
        } catch (err) {
            console.error('Login error:', err);
            alert('Something went wrong. Please try again.');
        }
    });
}

async function pollLoginRFID(user_id) {
    try {
        // step 2: wait for RFID tap
        // SWAP TO RFID_SCAN WHEN READY
        const response = await fetch('/api/auth/rfid-test');
        const data = await response.json();

        if (data.uid) {
            // step 3: verify RFID matches the user
            const verifyResponse = await fetch('/api/auth/rfid-verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id, rfid_uid: data.uid })
            });

            const verifyData = await verifyResponse.json();

            if (verifyData.success) {
                window.location.href = 'dashboard.html';
            } else {
                alert('RFID does not match. Access denied.');
                loginForm.querySelector('button[type="submit"]').disabled = false;
                document.getElementById('rfid-prompt').style.display = 'none';
            }
        } else {
            setTimeout(() => pollLoginRFID(user_id), 1000);
        }
    } catch (err) {
        console.error('RFID polling error:', err);
        setTimeout(() => pollLoginRFID(user_id), 2000);
    }
}

// ─── Register Page ────────────────────────────────────────────────────────────

const nextBtn = document.getElementById('next');
if (nextBtn) {
    nextBtn.addEventListener('click', function() {
        const password = document.getElementById('register-password').value;
        const confirm = document.getElementById('confirm-password').value;

        if (password.length === 0) {
            alert('Password cannot be empty.');
            return;
        }

        if (password !== confirm) {
            alert('Passwords do not match.');
            return;
        }

        document.getElementById('rfid-section').style.display = 'block';
        nextBtn.disabled = true;
        pollRFID();
    });
}

async function pollRFID() {
    try {
        const response = await fetch('/api/auth/rfid-test');
        const data = await response.json();

        if (data.uid) {
            document.getElementById('rfid-uid').value = data.uid;
            document.querySelector('#rfid-section p').textContent = 'Card registered! Click Create Account to finish.';
            document.getElementById('submit-btn').style.display = 'block';
        } else {
            setTimeout(pollRFID, 1000);
        }
    } catch (err) {
        console.error('RFID polling error:', err);
        setTimeout(pollRFID, 2000);
    }
}

const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;
        const rfid_uid = document.getElementById('rfid-uid').value;

        if (!rfid_uid) {
            alert('Please tap your card before submitting.');
            return;
        }

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password, rfid_uid })
            });

            const data = await response.json();

            if (data.success) {
                window.location.href = 'index.html';
            } else {
                alert('Registration failed: ' + data.message);
            }
        } catch (err) {
            console.error('Registration error:', err);
            alert('Something went wrong. Please try again.');
        }
    });
}