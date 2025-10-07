:root {
    --primary: #2575fc;
    --primary-dark: #1c5bbf;
    --bg-gradient: linear-gradient(135deg, #170661, #092e6e);
    --text-dark: #282c34;
    --text-light: #666;
    --error: #c50d0d;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    font-family: 'Poppins', sans-serif;
    background: var(--bg-gradient);
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    color: var(--text-dark);
}

.login-container {
    background: #ffffff;
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
    width: 100%;
    max-width: 400px;
    text-align: center;
    animation: fadeIn 0.6s ease-out;
}

.login-container h2 {
    margin-bottom: 20px;
    font-size: 28px;
    color: var(--text-dark);
}

.login-container p {
    margin-bottom: 30px;
    font-size: 16px;
    color: var(--text-light);
}

.form-group {
    margin-bottom: 20px;
    text-align: left;
}

.label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
}

.with-icon .input-icon {
    position: relative;
}

.with-icon .input-icon i {
    position: absolute;
    top: 50%;
    left: 12px;
    transform: translateY(-50%);
    color: #aaa;
}

.with-icon .input-icon input {
    width: 100%;
    padding: 12px 12px 12px 40px;
    font-size: 16px;
    border: 1px solid #ddd;
    border-radius: 8px;
    outline: none;
    transition: border-color 0.3s;
}

input:focus {
    border-color: var(--primary);
}

.submit-button {
    width: 100%;
    padding: 12px;
    font-size: 16px;
    font-weight: 500;
    color: #ffffff;
    background-color: var(--primary);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.submit-button:hover {
    background-color: var(--primary-dark);
}

.forgot-password {
    margin-top: 15px;
    font-size: 14px;
    color: var(--primary);
    text-decoration: none;
    display: inline-block;
    transition: color 0.3s;
}

.forgot-password:hover {
    color: var(--primary-dark);
}

.messages {
    margin-top: 20px;
}

.messages .error {
    color: var(--error);
    font-size: 16px;
}

.logo-container {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}

.logo {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--primary);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.contact-info {
    margin-top: 30px;
    padding-top: 15px;
    border-top: 1px solid #eee;
    font-size: 14px;
    color: var(--text-light);
}

.contact-info a {
    color: var(--primary);
    text-decoration: none;
    transition: color 0.3s;
}

.contact-info a:hover {
    color: var(--primary-dark);
}

.contact-info i {
    margin-right: 5px;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 480px) {
    .login-container {
        padding: 30px 20px;
        border-radius: 10px;
    }
}
