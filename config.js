/**
 * ====================================================================
 * MC SECURITIZADORA - OPEN FINANCE & PIX AUTOMÁTICO
 * Configurações Centrais, Utilitários de Comunicação e Segurança
 * ====================================================================
 */

(function (window) {
    'use strict';

    // 1. Detecção Automática de Ambiente (Local vs Produção)
    const hostname = window.location.hostname;
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '';

    // Se estiver rodando no mesmo servidor Flask, a API é a própria origem.
    // Caso contrário, usa a rota do backend oficial no Render ou local.
    let defaultApiUrl = 'https://motor-openfinance.onrender.com';
    if (isLocalhost) {
        defaultApiUrl = 'http://127.0.0.1:5000';
    }

    // Permite override via variável global se necessário
    const API_BASE_URL = window.API_BASE_URL_OVERRIDE || defaultApiUrl;

    // 2. Gerenciamento de Autenticação Segura do Gestor
    const TOKEN_KEY = 'mc_gestor_auth_token';
    const USER_KEY = 'mc_gestor_user_info';

    function getAuthToken() {
        return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);
    }

    function setAuthToken(token, user, remember = true) {
        const storage = remember ? localStorage : sessionStorage;
        storage.setItem(TOKEN_KEY, token);
        if (user) {
            storage.setItem(USER_KEY, JSON.stringify(user));
        }
    }

    function clearAuthToken() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        sessionStorage.removeItem(TOKEN_KEY);
        sessionStorage.removeItem(USER_KEY);
        // Limpa também chaves legadas
        localStorage.removeItem('chaveAcessoGestor');
    }

    function getAuthUser() {
        try {
            const data = localStorage.getItem(USER_KEY) || sessionStorage.getItem(USER_KEY);
            return data ? JSON.parse(data) : null;
        } catch (e) {
            return null;
        }
    }

    function isAuthenticated() {
        return !!getAuthToken();
    }

    // 3. Wrapper de Requisições Autenticadas (authFetch)
    async function authFetch(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
        
        options.headers = options.headers || {};
        
        const token = getAuthToken();
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }
        
        if (!options.headers['Content-Type'] && !(options.body instanceof FormData)) {
            options.headers['Content-Type'] = 'application/json';
        }

        try {
            const response = await fetch(url, options);

            // Se for 401 (Não autorizado), redireciona para login
            if (response.status === 401) {
                clearAuthToken();
                if (!window.location.pathname.endsWith('gestor-login.html')) {
                    showToast('Sessão expirada. Faça login novamente.', 'warning');
                    setTimeout(() => {
                        window.location.href = 'gestor-login.html';
                    }, 1200);
                }
            }

            return response;
        } catch (error) {
            console.error('[API Fetch Error]:', error);
            throw error;
        }
    }

    // 4. Prevenção de XSS (Sanitização Segura de HTML)
    function escapeHtml(str) {
        if (str === null || str === undefined) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // 5. Sistema de Toasts Modernos e Elegantes (Substitui alerts invasivos)
    function showToast(message, type = 'info', duration = 3500) {
        let container = document.getElementById('mc-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'mc-toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 999999;
                display: flex;
                flex-direction: column;
                gap: 10px;
                pointer-events: none;
                max-width: 90vw;
                width: 380px;
            `;
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.style.cssText = `
            pointer-events: auto;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
            border-radius: 12px;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 13.5px;
            font-weight: 500;
            color: #ffffff;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25), 0 8px 10px -6px rgba(0, 0, 0, 0.2);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            transform: translateX(100%);
            opacity: 0;
            backdrop-filter: blur(8px);
        `;

        let bgColor = '#1e293b';
        let icon = '<i class="fa-solid fa-circle-info text-blue-400"></i>';

        if (type === 'success') {
            bgColor = 'rgba(6, 78, 59, 0.95)';
            icon = '<i class="fa-solid fa-circle-check text-emerald-400 text-base"></i>';
        } else if (type === 'error') {
            bgColor = 'rgba(127, 29, 29, 0.95)';
            icon = '<i class="fa-solid fa-triangle-exclamation text-rose-400 text-base"></i>';
        } else if (type === 'warning') {
            bgColor = 'rgba(120, 53, 15, 0.95)';
            icon = '<i class="fa-solid fa-circle-exclamation text-amber-400 text-base"></i>';
        } else {
            bgColor = 'rgba(15, 23, 42, 0.95)';
            icon = '<i class="fa-solid fa-circle-info text-blue-400 text-base"></i>';
        }

        toast.style.backgroundColor = bgColor;
        toast.innerHTML = `
            <div style="flex-shrink: 0;">${icon}</div>
            <div style="flex: 1; line-height: 1.4;">${escapeHtml(message)}</div>
            <button style="background: none; border: none; color: rgba(255,255,255,0.7); cursor: pointer; padding: 0; font-size: 16px; margin-left: 6px;" onclick="this.parentElement.remove()">&times;</button>
        `;

        container.appendChild(toast);

        // Animação de entrada
        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(0)';
            toast.style.opacity = '1';
        });

        // Remoção após duration
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 350);
        }, duration);
    }

    // 6. Formatadores Utilitários
    function formatMoney(value) {
        if (value === null || value === undefined || isNaN(value)) return 'R$ 0,00';
        return parseFloat(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function formatDate(dateString) {
        if (!dateString) return '---';
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return dateString;
            return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return dateString;
        }
    }

    // Exportação Global
    window.MC_CONFIG = {
        API_BASE_URL,
        isLocalhost,
        getAuthToken,
        setAuthToken,
        clearAuthToken,
        getAuthUser,
        isAuthenticated,
        authFetch,
        escapeHtml,
        showToast,
        formatMoney,
        formatDate
    };

})(window);
