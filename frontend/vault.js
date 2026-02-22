async function loadVault() {
    try {
        const response = await fetch('/api/vault');
        const data = await response.json();

        if (data.success) {
            renderCredentials(data.credentials);
        }
    } catch (err) {
        console.error('Vault error:', err);
        alert('Something went wrong. Please try again.');
    }
}

function renderCredentials(credentials) {
    const vault = document.getElementById('vault-section');

    if (credentials.length === 0) {
        vault.innerHTML += '<p>No credentials stored yet.</p>';
        return;
    }

    const grid = document.createElement('div');
    grid.className = 'grid-container';

    credentials.forEach(cred => {
        const card = document.createElement('div');
        card.className = 'credential-card';
        card.innerHTML = `
            <div class="card-header">
                <h3>${cred.name}</h3>
                <span class="arrow">▼</span>
            </div>
            <div class="card-body" style="display:none;">
                <p><span class="label">Username:</span> ${cred.username}</p>
                <p><span class="label">Password:</span> 
                    <span class="password-text" style="filter:blur(4px);">${cred.password}</span>
                    <button class="reveal-btn" onclick="togglePassword(this)">Show</button>
                </p>
                ${cred.url ? `<p><span class="label">URL:</span> <a href="${cred.url}" target="_blank">${cred.url}</a></p>` : ''}
                ${cred.notes ? `<p><span class="label">Notes:</span> ${cred.notes}</p>` : ''}
            </div>
        `;

        card.querySelector('.card-header').addEventListener('click', function() {
            const body = card.querySelector('.card-body');
            const arrow = card.querySelector('.arrow');
            const isOpen = body.style.display === 'block';
            body.style.display = isOpen ? 'none' : 'block';
            arrow.textContent = isOpen ? '▼' : '▲';
        });

        grid.appendChild(card);
    });

    vault.appendChild(grid);
}

function togglePassword(btn) {
    const passwordText = btn.previousElementSibling;
    const isBlurred = passwordText.style.filter === 'blur(4px)';
    passwordText.style.filter = isBlurred ? 'none' : 'blur(4px)';
    btn.textContent = isBlurred ? 'Hide' : 'Show';
}

const vault = document.getElementById('vault-section');
if (vault) {
    loadVault();
}