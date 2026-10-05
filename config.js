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
    const isLocalhost = (hostname === 'localhost' || hostname === '127.0.0.1');

    // Se estiver rodando localmente com o Flask, conecta local na porta ativa.
    // Em qualquer outro ambiente (incluindo file:/// ou Render), usa o backend na nuvem.
    let defaultApiUrl = 'https://motor-openfinance.onrender.com';
    if (isLocalhost) {
        const port = window.location.port ? `:${window.location.port}` : ':5000';
        defaultApiUrl = `${window.location.protocol}//${hostname}${port}`;
    }

    // Permite override via variável global se necessário
    const API_BASE_URL = window.API_BASE_URL_OVERRIDE || defaultApiUrl;

    // 2. Identidade Visual e Logomarca Oficial (Configurável via URL ou caminho relativo)
    const LOGO_URL = window.LOGO_URL_OVERRIDE || 'logo-mc-minhaconta.png';

    // 3. Gerenciamento de Autenticação Segura do Gestor com Validação de Integridade
    const TOKEN_KEY = 'mc_gestor_auth_token';
    const USER_KEY = 'mc_gestor_user_info';

    function isTokenValid(token) {
        if (!token || typeof token !== 'string') return false;
        try {
            let b64 = token.replace(/-/g, '+').replace(/_/g, '/');
            while (b64.length % 4) b64 += '=';
            const decoded = atob(b64);
            const partes = decoded.split(':');
            if (partes.length !== 3) return false;
            const ts = parseInt(partes[1], 10);
            if (isNaN(ts)) return false;
            const agora = Math.floor(Date.now() / 1000);
            if (agora - ts > 86400 || ts > agora + 60) return false;
            return true;
        } catch (e) {
            return false;
        }
    }

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
            if (data) return JSON.parse(data);
        } catch (e) {}

        // Fallback: decodifica o usuário diretamente do payload do token de sessão
        const token = getAuthToken();
        if (token && isTokenValid(token)) {
            try {
                let b64 = token.replace(/-/g, '+').replace(/_/g, '/');
                while (b64.length % 4) b64 += '=';
                const decoded = atob(b64);
                const u = decoded.split(':')[0];
                if (u) {
                    const nome = (u === 'admin') ? 'Administrador' : (u === 'julianemc' ? 'Juliane MC' : u.charAt(0).toUpperCase() + u.slice(1));
                    return { username: u, nome };
                }
            } catch (e) {}
        }
        return null;
    }

    function isAuthenticated() {
        const token = getAuthToken();
        if (!token) return false;
        if (!isTokenValid(token)) {
            clearAuthToken();
            return false;
        }
        return true;
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

    // 6. Formatadores e Utilitários de Dados
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

    function cleanCpf(cpf) {
        return String(cpf || '').replace(/\D/g, '');
    }

    function formatCpf(cpf) {
        const digitos = cleanCpf(cpf).slice(0, 11);
        if (!digitos) return '';
        if (digitos.length <= 3) return digitos;
        if (digitos.length <= 6) return `${digitos.slice(0, 3)}.${digitos.slice(3)}`;
        if (digitos.length <= 9) return `${digitos.slice(0, 3)}.${digitos.slice(3, 6)}.${digitos.slice(6)}`;
        return `${digitos.slice(0, 3)}.${digitos.slice(3, 6)}.${digitos.slice(6, 9)}-${digitos.slice(9, 11)}`;
    }

    function validarCpf(cpf) {
        const digitos = cleanCpf(cpf);
        if (digitos.length !== 11) return false;
        if (/^(\d)\1{10}$/.test(digitos)) return false;

        let soma = 0;
        for (let i = 0; i < 9; i++) soma += parseInt(digitos.charAt(i)) * (10 - i);
        let resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) resto = 0;
        if (resto !== parseInt(digitos.charAt(9))) return false;

        soma = 0;
        for (let i = 0; i < 10; i++) soma += parseInt(digitos.charAt(i)) * (11 - i);
        resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) resto = 0;
        return resto === parseInt(digitos.charAt(10));
    }

    function cleanCnpj(cnpj) {
        return String(cnpj || '').replace(/\D/g, '');
    }

    function formatCnpj(cnpj) {
        const digitos = cleanCnpj(cnpj).slice(0, 14);
        if (!digitos) return '';
        if (digitos.length <= 2) return digitos;
        if (digitos.length <= 5) return `${digitos.slice(0, 2)}.${digitos.slice(2)}`;
        if (digitos.length <= 8) return `${digitos.slice(0, 2)}.${digitos.slice(2, 5)}.${digitos.slice(5)}`;
        if (digitos.length <= 12) return `${digitos.slice(0, 2)}.${digitos.slice(2, 5)}.${digitos.slice(5, 8)}/${digitos.slice(8)}`;
        return `${digitos.slice(0, 2)}.${digitos.slice(2, 5)}.${digitos.slice(5, 8)}/${digitos.slice(8, 12)}-${digitos.slice(12, 14)}`;
    }

    function validarCnpj(cnpj) {
        const digitos = cleanCnpj(cnpj);
        if (digitos.length !== 14) return false;
        if (/^(\d)\1{13}$/.test(digitos)) return false;

        const pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
        let soma1 = 0;
        for (let i = 0; i < 12; i++) soma1 += parseInt(digitos.charAt(i)) * pesos1[i];
        let resto1 = soma1 % 11;
        let d1 = resto1 < 2 ? 0 : 11 - resto1;
        if (parseInt(digitos.charAt(12)) !== d1) return false;

        const pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
        let soma2 = 0;
        for (let i = 0; i < 13; i++) soma2 += parseInt(digitos.charAt(i)) * pesos2[i];
        let resto2 = soma2 % 11;
        let d2 = resto2 < 2 ? 0 : 11 - resto2;
        return parseInt(digitos.charAt(13)) === d2;
    }

    function formatDoc(doc) {
        const limpo = String(doc || '').replace(/\D/g, '');
        if (limpo.length > 11) return formatCnpj(limpo);
        return formatCpf(limpo);
    }

    function validarDoc(doc) {
        const limpo = String(doc || '').replace(/\D/g, '');
        if (limpo.length === 14) return validarCnpj(limpo);
        if (limpo.length === 11) return validarCpf(limpo);
        return false;
    }

    function limparMemoriaCliente() {
        const chaves = ['memoriaCliente', 'memoriaCpf', 'memoriaCnpj', 'memoriaTipoDoc', 'memoriaValor', 'memoriaInicio', 'memoriaFim', 'memoriaBanco'];
        chaves.forEach(chave => localStorage.removeItem(chave));
    }

    // Exportação Global
    window.MC_CONFIG = {
        API_BASE_URL,
        LOGO_URL,
        isLocalhost,
        getAuthToken,
        setAuthToken,
        clearAuthToken,
        getAuthUser,
        isTokenValid,
        isAuthenticated,
        authFetch,
        escapeHtml,
        showToast,
        formatMoney,
        formatDate,
        cleanCpf,
        formatCpf,
        validarCpf,
        cleanCnpj,
        formatCnpj,
        validarCnpj,
        formatDoc,
        validarDoc,
        limparMemoriaCliente
    };

})(window);
