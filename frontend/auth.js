// ─── Login Page ───────────────────────────────────────────────────────────────

const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password })
            });

            const data = await response.json();

            if (data.success) {
                console.log('Password correct, waiting for RFID...');
                // TODO: show RFID prompt on login page
            } else {
                alert('Incorrect password. Try again.');
            }
        } catch (err) {
            console.error('Login error:', err);
            alert('Something went wrong. Please try again.');
        }
    });
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
        nextBtn.disabled = true; // prevent double clicking
        pollRFID();
    });
}

async function pollRFID() {
    try {
        const response = await fetch('/api/auth/rfid-scan');
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
        setTimeout(pollRFID, 2000); // wait a bit longer on error before retrying
    }
}

const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();

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
                body: JSON.stringify({ password, rfid_uid })
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