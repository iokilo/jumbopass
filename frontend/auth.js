document.getElementById('login-form').addEventListener('submit', async function(e) {
    e.preventDefault(); // stops the page from refreshing

    const password = document.getElementById('password').value;

    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: password })
    });

    const data = await response.json();

    if (data.success) {
        // password accepted, now prompt for RFID
        console.log('Password correct, waiting for RFID...');
    } else {
        console.log('Incorrect password');
    }
});