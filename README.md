# jumbopass

# blackbox 🔒

A cybersecurity-themed password vault with hardware 2FA using RFID. Built for a hackathon.

---

## What it does

blackbox lets users securely store and retrieve passwords through a noir-styled web interface. Authentication requires both a master password and a physical RFID card tap, providing two-factor authentication at login. All stored passwords are encrypted with a per-user vault key that never touches the database in plaintext.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | Python, Flask |
| Database | SQLite |
| Encryption | AES-GCM via `cryptography` library |
| Password Hashing | bcrypt |
| Key Derivation | Scrypt (KDF) |
| Hardware | RFID reader (RC522 or similar) |

---

## Security Model

- Master passwords are hashed with **bcrypt** and never stored in plaintext
- On registration, a random **256-bit vault key** is generated per user
- The vault key is encrypted using a **Scrypt-derived key** from the user's master password, and stored alongside its nonce
- At login, the vault key is decrypted in memory and stored in the **server-side session** — it never touches the database again
- Individual credential passwords are encrypted with **AES-GCM** using the vault key, with a unique nonce per entry
- Login requires both password verification **and** a physical RFID card tap (2FA)

---


---

## Setup

### Prerequisites

- Python 3.10+
- An RFID reader (RC522 or compatible)

### Installation

```bash
# clone the repo
git clone https://github.com/yourname/blackbox.git
cd blackbox/backend

# create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install flask flask-bcrypt cryptography

# initialize the database
python db/db_init.py

# run the app
python app.py
```

Then open your browser and go to:
```
http://localhost:5001
```



---

## Authentication Flow

```
1. User enters username + master password
        ↓
2. Server verifies bcrypt hash
        ↓
3. Server derives vault key from password + KDF, stores in session
        ↓
4. Frontend prompts user to tap RFID card
        ↓
5. Server verifies RFID UID matches user record
        ↓
6. Access granted → redirect to dashboard
```

## Team

Built at a hackathon by Edwin, Alex, Jake, and Ram.