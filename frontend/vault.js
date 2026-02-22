async function loadVault() {
    try {
        const response = await fetch('/api/vault');
        const data = await response.json();

        if (data.success) {
            const existing = document.querySelector('.grid-container');
            if (existing) existing.remove();
            renderCredentials(data.credentials);
        }
    } catch (err) {
        console.error('Vault error:', err);
        alert('Something went wrong. Please try again.');
    }
}

function renderCredentials(credentials) {
    const vault = document.getElementById('vault-section');

    const grid = document.createElement('div');
    grid.className = 'grid-container';

    if (credentials.length === 0) {
        // no entries but still show the add card
    }

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
                <button class="delete-btn" data-id="${cred.id}">delete entry</button>
            </div>
        `;
    
        card.querySelector('.card-header').addEventListener('click', function() {
            const body = card.querySelector('.card-body');
            const arrow = card.querySelector('.arrow');
            const isOpen = body.style.display === 'block';
            body.style.display = isOpen ? 'none' : 'block';
            arrow.textContent = isOpen ? '▼' : '▲';
        });
    
        card.querySelector('.delete-btn').addEventListener('click', function(e) {
            e.stopPropagation(); // prevent card from collapsing when clicking delete
            const id = this.dataset.id;
            deleteCredential(id);
        });
    
        grid.appendChild(card);
    });

    // add entry card
    const addCard = document.createElement('div');
    addCard.className = 'credential-card';
    addCard.innerHTML = `
        <div class="card-header" id="add-card-header">
            <h3>NEW ENTRY</h3>
            <span class="add-icon">+</span>
        </div>
        <div class="card-body" id="add-card-body" style="display:none;">
            <input type="text" id="cred-name" placeholder="site name" required>
            <input type="text" id="cred-username" placeholder="username">
            <input type="password" id="cred-password" placeholder="password" required>
            <input type="text" id="cred-url" placeholder="url">
            <input type="text" id="cred-notes" placeholder="notes">
            <button class="reveal-btn" style="margin-top: 10px; width: 100%; margin-left: 0;" onclick="submitCredential()">add entry</button>
        </div>
    `;

    addCard.querySelector('.card-header').addEventListener('click', function() {
        const body = addCard.querySelector('.card-body');
        const arrow = addCard.querySelector('.arrow');
        const isOpen = body.style.display === 'block';
        body.style.display = isOpen ? 'none' : 'block';
    });

    grid.appendChild(addCard);
    vault.appendChild(grid);
}

function togglePassword(btn) {
    const passwordText = btn.previousElementSibling;
    const isBlurred = passwordText.style.filter === 'blur(4px)';
    passwordText.style.filter = isBlurred ? 'none' : 'blur(4px)';
    btn.textContent = isBlurred ? 'Hide' : 'Show';
}

// ─── Add Credential ───────────────────────────────────────────────────────────

function submitCredential() {
    const name = document.getElementById('cred-name').value;
    const username = document.getElementById('cred-username').value;
    const password = document.getElementById('cred-password').value;
    const url = document.getElementById('cred-url').value;
    const notes = document.getElementById('cred-notes').value;

    if (!name || !password) {
        alert('Name and password are required.');
        return;
    }

    addCredential(name, username, password, url, notes);
}

async function addCredential(name, username, password, url, notes) {
    try {
        const response = await fetch('/api/vault', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, username, password, url, notes })
        });

        const data = await response.json();

        if (data.success) {
            // clear form fields
            document.getElementById('cred-name').value = '';
            document.getElementById('cred-username').value = '';
            document.getElementById('cred-password').value = '';
            document.getElementById('cred-url').value = '';
            document.getElementById('cred-notes').value = '';
            loadVault();
        } else {
            alert('Failed to add credential: ' + data.message);
        }
    } catch (err) {
        console.error('Add credential error:', err);
        alert('Something went wrong. Please try again.');
    }
}

async function deleteCredential(id) {
    if (!confirm('Delete this entry?')) return;

    try {
        const response = await fetch(`/api/vault/${id}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            loadVault();
        } else {
            alert('Failed to delete entry.');
        }
    } catch (err) {
        console.error('Delete error:', err);
        alert('Something went wrong. Please try again.');
    }
}

// ─── Init ─────────────────────────────────────────────────────────────────────

const vault = document.getElementById('vault-section');
if (vault) {
    loadVault();
}