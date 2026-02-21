const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const password = document.getElementById('password').value;

        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: password })
        });

        const data = await response.json();

        if (data.success) {
            console.log('Password correct, waiting for RFID...');
        } else {
            console.log('Incorrect password');
        }
    });
}

const nextBtn = document.getElementById('next');
if (nextBtn) {
    nextBtn.addEventListener('click', function() {
        const password = document.getElementById('register-password').value;
        const confirm = document.getElementById('confirm-password').value;

        if (password !== confirm || password.length === 0) {
            alert('Passwords do not match');
            return;
        }

        document.getElementById('rfid-section').style.display = 'block';
    });
}