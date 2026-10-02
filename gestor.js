/**
 * GESTOR.JS - Lógica de Controle Frontend
 * MC Securitizadora Open Finance
 */

let todosOsClientes = []; 
        let todosOsPix = [];
        let kpisPix = {};
        let filtroStatusPixAtivo = 'todos';
        let tipoLinkAtivo = 'extrato';
        let listaTodosBancos = [];

        function toggleSidebar(abrir) {
            const sidebar = document.getElementById('sidebar-menu');
            const backdrop = document.getElementById('sidebar-backdrop');
            if (!sidebar) return;
            
            const estaOculto = sidebar.classList.contains('-translate-x-full');
            const novoEstado = (abrir !== undefined) ? abrir : estaOculto;

            if (novoEstado) {
                sidebar.classList.remove('-translate-x-full');
                if (backdrop) backdrop.classList.remove('hidden');
            } else {
                sidebar.classList.add('-translate-x-full');
                if (backdrop) backdrop.classList.add('hidden');
            }
        }

        function alternarCascata(menuId) {
            const submenu = document.getElementById(`submenu-${menuId}`);
            const chevron = document.getElementById(`chevron-${menuId}`);
            if (!submenu) return;

            const estaOculto = submenu.classList.contains('hidden');
            if (estaOculto) {
                submenu.classList.remove('hidden');
                if (chevron) chevron.style.transform = 'rotate(180deg)';
            } else {
                submenu.classList.add('hidden');
                if (chevron) chevron.style.transform = 'rotate(0deg)';
            }
        }

        function navegarPara(secao, subopcao) {
            if (window.innerWidth < 768) {
                toggleSidebar(false);
            }
            
            if (secao === 'openfinance') {
                mudarAbaLista('extrato');
                if (subopcao === 'gerar') {
                    mudarAbaGerador('extrato');
                    const inp = document.getElementById('identificadorCliente');
                    if (inp) {
                        inp.focus();
                        inp.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                } else {
                    document.getElementById('painel-clientes-principal')?.scrollIntoView({ behavior: 'smooth' });
                }
            } else if (secao === 'pix') {
                mudarAbaLista('pix');
                if (subopcao === 'pagamentos') {
                    mudarSubVisaoPix('pagamentos');
                } else if (subopcao === 'gerar') {
                    mudarAbaGerador('pix');
                    const inp = document.getElementById('identificadorCliente');
                    if (inp) {
                        inp.focus();
                        inp.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                } else {
                    mudarSubVisaoPix('solicitacoes');
                }
                document.getElementById('painel-clientes-principal')?.scrollIntoView({ behavior: 'smooth' });
            } else if (secao === 'sync') {
                carregarClientes(true);
                MC_CONFIG.showToast('Sincronização com a Pluggy solicitada!', 'info');
            }
        }

        function fazerLogout() {
            if (confirm("Deseja realmente sair do Portal do Gestor?")) {
                MC_CONFIG.clearAuthToken();
                window.location.href = "gestor-login.html";
            }
        }

        function mudarAbaGerador(tipo) {
            tipoLinkAtivo = tipo;
            const btnExtrato = document.getElementById("aba-gen-extrato");
            const btnPix = document.getElementById("aba-gen-pix");
            const camposPix = document.getElementById("campos-pix");

            if (tipo === 'extrato') {
                if (btnExtrato) btnExtrato.className = "flex-1 py-2.5 rounded-lg text-xs font-bold transition bg-[#010157] text-white shadow-sm cursor-pointer";
                if (btnPix) btnPix.className = "flex-1 py-2.5 rounded-lg text-xs font-bold transition text-slate-600 hover:text-[#010157] cursor-pointer";
                if (camposPix) camposPix.classList.add("hidden");
            } else {
                if (btnPix) btnPix.className = "flex-1 py-2.5 rounded-lg text-xs font-bold transition bg-[#010157] text-white shadow-sm cursor-pointer";
                if (btnExtrato) btnExtrato.className = "flex-1 py-2.5 rounded-lg text-xs font-bold transition text-slate-600 hover:text-[#010157] cursor-pointer";
                if (camposPix) camposPix.classList.remove("hidden");
            }
            document.getElementById("box-resultado")?.classList.add("hidden");
        }
        window.alternarTipoOperacao = mudarAbaGerador;

        function mascaraMoeda(input) {
            let valor = input.value.replace(/\D/g, "");
            if (!valor) { input.value = ""; return; }
            valor = (parseFloat(valor) / 100).toFixed(2);
            input.value = parseFloat(valor).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
        }

        let tipoPessoaPix = 'pf';
        function alternarDocPix(tipo) {
            tipoPessoaPix = tipo;
            const btnPf = document.getElementById("btn-doc-pf");
            const btnPj = document.getElementById("btn-doc-pj");
            const boxPf = document.getElementById("box-doc-pf");
            const boxPj = document.getElementById("box-doc-pj");

            if (tipo === 'pf') {
                if (btnPf) btnPf.className = "py-2 rounded-lg text-xs font-bold transition bg-[#010157] text-white shadow-sm cursor-pointer flex items-center justify-center gap-1.5";
                if (btnPj) btnPj.className = "py-2 rounded-lg text-xs font-bold transition text-slate-600 hover:text-[#010157] cursor-pointer flex items-center justify-center gap-1.5";
                if (boxPf) boxPf.classList.remove("hidden");
                if (boxPj) boxPj.classList.add("hidden");
            } else {
                if (btnPj) btnPj.className = "py-2 rounded-lg text-xs font-bold transition bg-[#010157] text-white shadow-sm cursor-pointer flex items-center justify-center gap-1.5";
                if (btnPf) btnPf.className = "py-2 rounded-lg text-xs font-bold transition text-slate-600 hover:text-[#010157] cursor-pointer flex items-center justify-center gap-1.5";
                if (boxPf) boxPf.classList.add("hidden");
                if (boxPj) boxPj.classList.remove("hidden");
            }
        }

        function mascaraCpf(input) {
            input.value = MC_CONFIG.formatCpf(input.value);
        }

        function mascaraCnpj(input) {
            input.value = MC_CONFIG.formatCnpj(input.value);
        }

        function mascaraMoedaPix(input) {
            let v = input.value.replace(/\D/g, "");
            if (!v) {
                input.value = "";
                return;
            }
            const centavos = parseInt(v, 10);
            const floatVal = centavos / 100;
            input.value = floatVal.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        function gerarLink() {
            const identificador = document.getElementById("identificadorCliente").value.trim();
            if (!identificador) {
                MC_CONFIG.showToast("Informe o identificador ou nome do cliente.", "warning");
                return;
            }

            const parametros = new URLSearchParams();
            parametros.append("cliente", identificador);

            if (tipoLinkAtivo === "pix") {
                const valorCampo = (document.getElementById("valorPix")?.value || "").trim();
                const apenasDigitos = valorCampo.replace(/\D/g, "");
                let valorFloat = 0;
                if (apenasDigitos) {
                    valorFloat = parseInt(apenasDigitos, 10) / 100;
                } else {
                    valorFloat = parseFloat(valorCampo.replace(",", "."));
                }

                const inicio = document.getElementById("dataInicio")?.value;
                const fim = document.getElementById("dataFim")?.value;

                if (!valorFloat || isNaN(valorFloat) || valorFloat <= 0) {
                    MC_CONFIG.showToast("Informe o valor da parcela mensal do Pix.", "warning");
                    return;
                }

                if (valorFloat > 10000) {
                    const fmtValor = valorFloat.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
                    if (!confirm(`Atenção: Você está prestes a gerar uma solicitação de Pix Automático no valor de ${fmtValor} mensais.\n\nConfirma que este valor está correto?`)) {
                        return;
                    }
                }

                if (!inicio) {
                    MC_CONFIG.showToast("Informe a data de início da primeira cobrança.", "warning");
                    return;
                }

                parametros.append("valor", valorFloat.toFixed(2));
                parametros.append("inicio", inicio);
                if (fim) {
                    parametros.append("fim", fim);
                }

                if (tipoPessoaPix === 'pf') {
                    const cpf = MC_CONFIG.cleanCpf(document.getElementById("cpfCliente")?.value);
                    if (!cpf || !MC_CONFIG.validarCpf(cpf)) {
                        MC_CONFIG.showToast("Informe um CPF válido com 11 dígitos para a Pessoa Física.", "warning");
                        return;
                    }
                    parametros.append("tipoDoc", "pf");
                    parametros.append("cpf", cpf);
                } else {
                    const cnpj = MC_CONFIG.cleanCnpj(document.getElementById("cnpjEmpresa")?.value);
                    const cpfRep = MC_CONFIG.cleanCpf(document.getElementById("cpfRepresentante")?.value);

                    if (!cnpj || !MC_CONFIG.validarCnpj(cnpj)) {
                        MC_CONFIG.showToast("Informe um CNPJ válido com 14 dígitos para a Empresa.", "warning");
                        return;
                    }
                    if (!cpfRep || !MC_CONFIG.validarCpf(cpfRep)) {
                        MC_CONFIG.showToast("Informe o CPF do representante legal/operador que autorizará no banco.", "warning");
                        return;
                    }
                    parametros.append("tipoDoc", "pj");
                    parametros.append("cnpj", cnpj);
                    parametros.append("cpf", cpfRep);
                }
            }

            let urlBase = window.location.origin;
            if (!urlBase || urlBase === 'null' || urlBase.startsWith('file:') || urlBase.includes('localhost') || urlBase.includes('127.0.0.1')) {
                urlBase = 'https://vitrine-openfinance.onrender.com';
            }
            const urlFinal = `${urlBase}/cliente.html?${parametros.toString()}`;
            
            document.getElementById("linkGerado").textContent = urlFinal;
            document.getElementById("box-resultado").classList.remove("hidden");
            MC_CONFIG.showToast("Link seguro gerado com sucesso!", "success");
        }

        function copiarLink() {
            const texto = document.getElementById("linkGerado").textContent;
            navigator.clipboard.writeText(texto).then(() => {
                const btn = document.getElementById("btn-copiar");
                btn.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> Copiado!`;
                MC_CONFIG.showToast("Link copiado para a area de transferencia!", "success");
                setTimeout(() => {
                    btn.innerHTML = `<i class="fa-regular fa-copy"></i> Copiar Link`;
                }, 2000);
            }).catch(() => {
                MC_CONFIG.showToast("Erro ao copiar link.", "error");
            });
        }

        function compartilharWhatsApp() {
            const texto = document.getElementById("linkGerado").textContent;
            const cliente = document.getElementById("identificadorCliente").value.trim();
            const mensagem = `Ola ${cliente}, segue o link seguro da MC Minha Conta para autorizacao bancaria: ${texto}`;
            const urlWhats = `https://api.whatsapp.com/send?text=${encodeURIComponent(mensagem)}`;
            window.open(urlWhats, '_blank');
        }

        // ============================================================
        // CARREGAMENTO CENTRALIZADO (OPEN FINANCE + PAINEL PLUGGY PIX)
        // ============================================================

        async function carregarClientes(forcar = false) {
            const divLista = document.getElementById('lista-clientes');
            const btnRecarregar = document.getElementById('btn-recarregar');
            
            btnRecarregar.innerHTML = `<i class="fa-solid fa-rotate fa-spin"></i>`;
            
            const btnPix = document.getElementById('aba-lista-pix');
            const abaAtual = (btnPix && btnPix.classList.contains('bg-[#010157]')) ? 'pix' : 'extrato';

            divLista.innerHTML = `
                <div class="flex flex-col items-center justify-center py-16 text-slate-400">
                    <i class="fa-solid fa-circle-notch fa-spin text-[#0985ff] text-3xl mb-3"></i>
                    <p class="text-xs">Sincronizando com a API da Pluggy...</p>
                </div>
            `;
            
            try {
                // 1. Carrega Open Finance do Supabase
                const resOf = await MC_CONFIG.authFetch('/listar-conexoes');
                if (resOf.ok) {
                    todosOsClientes = await resOf.json();
                }

                // 2. Carrega Pix Automatico diretamente da Pluggy com KPIs
                try {
                    const resPix = await MC_CONFIG.authFetch(`/api/pix-intents${forcar ? '?force=true' : ''}`);
                    if (resPix.ok) {
                        const dataPix = await resPix.json();
                        todosOsPix = dataPix.results || [];
                        kpisPix = dataPix.kpis || {};
                        atualizarRibbonKpisPix(kpisPix);
                        atualizarPeriodosDinamicos(todosOsPix);
                    }
                } catch (ePix) {
                    console.warn('[PIX INTENTS FETCH WARNING]:', ePix);
                }

                // Fallback automático para Pix caso a API de intents retorne vazia temporariamente
                if (todosOsPix.length === 0 && todosOsClientes.length > 0) {
                    const pixDb = todosOsClientes.filter(c => c.payment_intent_id || c.tipo === 'pix_automatico');
                    if (pixDb.length > 0) {
                        todosOsPix = pixDb.map(c => ({
                            id: c.payment_intent_id || c.item_id,
                            cliente: c.cliente,
                            status: 'PAYMENT_COMPLETED',
                            status_label: 'Contrato Ativo',
                            status_classe: 'ativo',
                            status_badge: 'bg-emerald-100 text-emerald-800 border-emerald-300',
                            banco_nome: 'Instituição Bancária',
                            valor_parcela: 0,
                            data_criacao: c.data_conexao
                        }));
                    }
                }
                
                renderizarLista(abaAtual);
            } catch (erro) {
                divLista.innerHTML = `
                    <div class="text-center py-12 text-rose-500 text-xs">
                        <i class="fa-solid fa-triangle-exclamation text-2xl mb-2"></i>
                        <p>Falha ao carregar informacoes: ${MC_CONFIG.escapeHtml(erro.message)}</p>
                    </div>
                `;
            } finally {
                btnRecarregar.innerHTML = `<i class="fa-solid fa-rotate"></i>`;
            }
        }

        let modoExibicaoPix = 'tabela';
        let subVisaoPix = 'solicitacoes';
        let paginaAtualPluggy = 1;
        let linhasPorPaginaPluggy = 100;
        let filtroStatusPluggy = 'todos';

        function focarCriarSolicitacao() {
            mudarAbaGerador('pix');
            const inputCli = document.getElementById('identificadorCliente');
            if (inputCli) {
                inputCli.focus();
                inputCli.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            MC_CONFIG.showToast("Informe os dados do cliente e valor para criar a solicitação Pix.", "info");
        }

        function mudarSubVisaoPix(sub) {
            subVisaoPix = sub;
            const btnSol = document.getElementById('subbtn-solicitacoes');
            const btnPag = document.getElementById('subbtn-pagamentos');
            const cSol = document.getElementById('container-painel-solicitacoes');
            const cPag = document.getElementById('container-painel-pagamentos');

            const inativo = "px-3 py-1.5 rounded-lg text-slate-600 hover:text-[#010157] transition cursor-pointer flex items-center gap-1.5";
            const ativo = "px-3 py-1.5 rounded-lg bg-[#010157] text-white shadow-xs transition cursor-pointer flex items-center gap-1.5";

            if (btnSol) btnSol.className = (sub === 'solicitacoes') ? ativo : inativo;
            if (btnPag) btnPag.className = (sub === 'pagamentos') ? ativo : inativo;

            if (sub === 'solicitacoes') {
                if (cSol) cSol.classList.remove('hidden');
                if (cPag) cPag.classList.add('hidden');
            } else {
                if (cSol) cSol.classList.add('hidden');
                if (cPag) cPag.classList.remove('hidden');
            }
        }

        function alternarModoExibicao(modo) {
            modoExibicaoPix = modo;
            const btnTab = document.getElementById('btn-modo-tabela');
            const btnCard = document.getElementById('btn-modo-cards');
            const wrapperTab = document.getElementById('wrapper-tabela-pluggy');
            const listaCli = document.getElementById('lista-clientes');

            if (modo === 'tabela') {
                if (btnTab) btnTab.className = "px-2.5 py-1 rounded-lg bg-white text-[#010157] font-bold shadow-xs cursor-pointer";
                if (btnCard) btnCard.className = "px-2.5 py-1 rounded-lg text-slate-500 hover:text-[#010157] font-medium cursor-pointer";
                if (wrapperTab) wrapperTab.classList.remove('hidden');
                if (listaCli) listaCli.classList.add('hidden');
            } else {
                if (btnCard) btnCard.className = "px-2.5 py-1 rounded-lg bg-white text-[#010157] font-bold shadow-xs cursor-pointer";
                if (btnTab) btnTab.className = "px-2.5 py-1 rounded-lg text-slate-500 hover:text-[#010157] font-medium cursor-pointer";
                if (wrapperTab) wrapperTab.classList.add('hidden');
                if (listaCli) listaCli.classList.remove('hidden');
            }
            renderizarLista('pix');
        }

        function mudarPagina(delta) {
            paginaAtualPluggy += delta;
            renderizarLista('pix');
        }

        function mudarLinhasPorPagina(val) {
            linhasPorPaginaPluggy = parseInt(val) || 100;
            paginaAtualPluggy = 1;
            renderizarLista('pix');
        }

        function aplicarFiltrosPluggy() {
            debounceFiltrarClientes();
        }

        function formatarDataSimplesPluggy(isoDate) {
            if (!isoDate) return '---';
            try {
                const s = String(isoDate).trim();
                const partes = s.slice(0, 10).split('-');
                if (partes.length === 3) {
                    const meses = ['', 'jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.'];
                    const mIdx = parseInt(partes[1], 10);
                    const mesNome = (mIdx >= 1 && mIdx <= 12) ? meses[mIdx] : partes[1];
                    return `${parseInt(partes[2], 10)} de ${mesNome} de ${partes[0]}`;
                }
            } catch {}
            return String(isoDate);
        }

        function formatarDataPluggy(isoString) {
            if (!isoString) return '---';
            try {
                const s = String(isoString).trim();
                if (s.length === 10 && s.indexOf('-') === 4) {
                    return formatarDataSimplesPluggy(s);
                }
                const d = new Date(isoString);
                if (isNaN(d.getTime())) return isoString;
                const meses = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.'];
                const dia = String(d.getDate()).padStart(2, '0');
                const mes = meses[d.getMonth()];
                const ano = d.getFullYear();
                const hora = String(d.getHours()).padStart(2, '0');
                const min = String(d.getMinutes()).padStart(2, '0');
                const seg = String(d.getSeconds()).padStart(2, '0');
                return `${dia} de ${mes} de ${ano}, ${hora}:${min}:${seg}`;
            } catch {
                return isoString;
            }
        }

        function atualizarPeriodosDinamicos(listaPix) {
            if (!listaPix || listaPix.length === 0) return;
            const datasValidas = listaPix
                .map(p => p.data_criacao ? new Date(p.data_criacao) : null)
                .filter(d => d && !isNaN(d.getTime()));

            if (datasValidas.length > 0) {
                const minData = new Date(Math.min(...datasValidas));
                const maxData = new Date(Math.max(...datasValidas));
                const meses = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.'];
                
                let rangeTexto = '';
                if (minData.getFullYear() === maxData.getFullYear()) {
                    if (minData.getMonth() === maxData.getMonth()) {
                        rangeTexto = `${minData.getDate()} – ${maxData.getDate()} de ${meses[maxData.getMonth()]} de ${maxData.getFullYear()}`;
                    } else {
                        rangeTexto = `${minData.getDate()} de ${meses[minData.getMonth()]} – ${maxData.getDate()} de ${meses[maxData.getMonth()]} de ${maxData.getFullYear()}`;
                    }
                } else {
                    rangeTexto = `${minData.getDate()} de ${meses[minData.getMonth()]} de ${minData.getFullYear()} – ${maxData.getDate()} de ${meses[maxData.getMonth()]} de ${maxData.getFullYear()}`;
                }

                const elPeriodoSol = document.getElementById('filtro-pluggy-periodo');
                if (elPeriodoSol) elPeriodoSol.textContent = rangeTexto;

                const elPeriodoPag = document.getElementById('periodo-pagamentos-texto');
                if (elPeriodoPag) elPeriodoPag.textContent = rangeTexto;
            }
        }

        function renderizarDonutInstituicoes(instituicoes, totalQtd) {
            const containerSvg = document.getElementById('container-donut-svg');
            const containerLegenda = document.getElementById('container-legenda-bancos');
            if (!containerSvg || !containerLegenda) return;

            if (!instituicoes || instituicoes.length === 0) {
                containerSvg.innerHTML = `
                    <div class="w-32 h-32 rounded-full border-4 border-dashed border-slate-200 flex flex-col items-center justify-center text-slate-400 text-xs text-center p-2">
                        <i class="fa-solid fa-chart-pie text-xl mb-1 text-slate-300"></i>
                        <span>Sem dados</span>
                    </div>
                `;
                containerLegenda.innerHTML = `<p class="text-xs text-slate-400 italic">Nenhum pagamento concluído no período.</p>`;
                return;
            }

            const r = 40;
            const c = 2 * Math.PI * r;
            let offsetAcumulado = 0;
            let svgCircles = '';

            instituicoes.forEach(inst => {
                const pct = inst.percentual || 0;
                const dash = (pct / 100) * c;
                const gap = c - dash;
                const cor = inst.cor || '#0985ff';

                svgCircles += `
                    <circle 
                        cx="60" cy="60" r="${r}" 
                        fill="transparent" 
                        stroke="${cor}" 
                        stroke-width="18" 
                        stroke-dasharray="${dash.toFixed(2)} ${gap.toFixed(2)}" 
                        stroke-dashoffset="${(-offsetAcumulado).toFixed(2)}"
                        class="transition-all duration-300 hover:opacity-85 cursor-pointer"
                    >
                        <title>${inst.nome}: ${pct}% (${inst.qtd})</title>
                    </circle>
                `;
                offsetAcumulado += dash;
            });

            containerSvg.innerHTML = `
                <svg width="150" height="150" viewBox="0 0 120 120" class="transform -rotate-90">
                    <circle cx="60" cy="60" r="${r}" fill="transparent" stroke="#f1f5f9" stroke-width="18" />
                    ${svgCircles}
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span class="text-2xl font-black text-[#010157] font-mono leading-none">${totalQtd}</span>
                    <span class="text-[9px] uppercase font-bold text-slate-400 mt-1 tracking-wider">Total</span>
                </div>
            `;

            let htmlLegenda = '';
            instituicoes.forEach(inst => {
                const cor = inst.cor || '#0985ff';
                const nomeSeguro = MC_CONFIG.escapeHtml(inst.nome);
                htmlLegenda += `
                    <div class="flex items-center justify-between text-xs py-1 px-2.5 rounded-lg hover:bg-slate-50 transition border border-transparent hover:border-slate-100">
                        <div class="flex items-center gap-2.5">
                            <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" style="background-color: ${cor}"></span>
                            <span class="text-slate-700 font-medium">${nomeSeguro}</span>
                        </div>
                        <span class="font-bold text-slate-800 font-mono">${inst.percentual}% (${inst.qtd})</span>
                    </div>
                `;
            });
            containerLegenda.innerHTML = htmlLegenda;
        }

        function atualizarRibbonKpisPix(kpis) {
            kpis = kpis || {};
            const elQtd = document.getElementById('kpi-qtd-concluidos-grande');
            if (elQtd) elQtd.textContent = kpis.total_concluidos_qtd ?? 0;

            const elValor = document.getElementById('kpi-valor-concluidos-grande');
            if (elValor) elValor.textContent = MC_CONFIG.formatMoney(kpis.total_concluidos_valor ?? 0);

            renderizarDonutInstituicoes(kpis.instituicoes || [], kpis.total_concluidos_qtd || 0);
        }

        let debounceTimerBusca = null;
        function debounceFiltrarClientes() {
            clearTimeout(debounceTimerBusca);
            debounceTimerBusca = setTimeout(() => {
                paginaAtualPluggy = 1;
                filtrarClientes();
            }, 180);
        }

        function mudarAbaLista(abaSelecionada) {
            const btnExtrato = document.getElementById('aba-lista-extrato');
            const btnPix = document.getElementById('aba-lista-pix');
            const subNavPix = document.getElementById('subnavegacao-pix');
            const cPag = document.getElementById('container-painel-pagamentos');
            const cSol = document.getElementById('container-painel-solicitacoes');
            const divLista = document.getElementById('lista-clientes');
            
            btnExtrato.className = "px-5 py-2 rounded-xl text-xs font-bold transition text-slate-600 hover:text-[#010157] flex items-center gap-2 cursor-pointer";
            btnPix.className = "px-5 py-2 rounded-xl text-xs font-bold transition text-slate-600 hover:text-[#010157] flex items-center gap-2 cursor-pointer";
            
            if (abaSelecionada === 'extrato') {
                btnExtrato.className = "px-5 py-2 rounded-xl text-xs font-bold transition bg-[#010157] text-white shadow-sm flex items-center gap-2 cursor-pointer";
                if (subNavPix) subNavPix.classList.add("hidden");
                if (cPag) cPag.classList.add("hidden");
                if (cSol) cSol.classList.add("hidden");
                if (divLista) divLista.classList.remove("hidden");
                renderizarLista('extrato');
            } else {
                btnPix.className = "px-5 py-2 rounded-xl text-xs font-bold transition bg-[#010157] text-white shadow-sm flex items-center gap-2 cursor-pointer";
                if (subNavPix) subNavPix.classList.remove("hidden");
                mudarSubVisaoPix(subVisaoPix);
                alternarModoExibicao(modoExibicaoPix);
            }
        }

        function filtrarClientes() {
            const btnPix = document.getElementById('aba-lista-pix');
            const abaAtiva = (btnPix && btnPix.classList.contains('bg-[#010157]')) ? 'pix' : 'extrato';
            renderizarLista(abaAtiva);
        }

        // ============================================================
        // RENDERIZADOR PRINCIPAL DE ALTA PERFORMANCE (ZERO LAG)
        // ============================================================

        function renderizarLista(filtroAba) {
            const divLista = document.getElementById('lista-clientes');
            const badgeTotal = document.getElementById('badge-contador-total');
            const termoBusca = (
                (document.getElementById('filtro-pluggy-busca')?.value || '') ||
                (document.getElementById('inputBusca')?.value || '')
            ).toLowerCase().trim();

            if (filtroAba === 'pix') {
                const buscaTexto = termoBusca;
                const statusFiltro = (document.getElementById('filtro-pluggy-status')?.value || 'todos');
                const periodoFiltro = (document.getElementById('filtro-pluggy-periodo-select')?.value || 'todos');
                const agoraMs = Date.now();
                const limitesDias = {
                    '7d': 7 * 86400000,
                    '30d': 30 * 86400000,
                    '90d': 90 * 86400000
                };

                const pixFiltrados = todosOsPix.filter(p => {
                    const matchTexto = (
                        (p.cliente || '').toLowerCase().includes(buscaTexto) ||
                        (p.cpf || '').includes(buscaTexto) ||
                        (p.cnpj || '').includes(buscaTexto) ||
                        (p.id_externo || '').toLowerCase().includes(buscaTexto) ||
                        (p.id || '').toLowerCase().includes(buscaTexto) ||
                        (p.descricao || '').toLowerCase().includes(buscaTexto) ||
                        (p.recebedor || '').toLowerCase().includes(buscaTexto) ||
                        (p.banco_nome || '').toLowerCase().includes(buscaTexto)
                    );
                    let matchStatus = true;
                    if (statusFiltro !== 'todos') {
                        if (statusFiltro === 'Erro') {
                            matchStatus = (p.status_label === 'Erro' || p.status_label === 'Falha no Banco' || p.status_classe === 'erro');
                        } else {
                            matchStatus = (p.status_label === statusFiltro || p.status === statusFiltro);
                        }
                    }
                    let matchPeriodo = true;
                    if (periodoFiltro !== 'todos' && limitesDias[periodoFiltro]) {
                        if (p.data_criacao) {
                            const t = new Date(p.data_criacao).getTime();
                            matchPeriodo = !isNaN(t) && ((agoraMs - t) <= limitesDias[periodoFiltro]);
                        } else {
                            matchPeriodo = false;
                        }
                    }
                    return matchTexto && matchStatus && matchPeriodo;
                });

                atualizarPeriodosDinamicos(pixFiltrados.length > 0 ? pixFiltrados : todosOsPix);

                badgeTotal.innerHTML = `Exibindo <strong class="text-[#010157] font-bold">${pixFiltrados.length}</strong> de <strong class="text-[#0985ff] font-bold">${todosOsPix.length}</strong> solicitações Pix`;

                // Cálculo da paginação
                const totalItens = pixFiltrados.length;
                const totalPaginas = Math.max(1, Math.ceil(totalItens / linhasPorPaginaPluggy));
                if (paginaAtualPluggy > totalPaginas) paginaAtualPluggy = totalPaginas;
                if (paginaAtualPluggy < 1) paginaAtualPluggy = 1;

                const inicioIdx = (paginaAtualPluggy - 1) * linhasPorPaginaPluggy;
                const fimIdx = Math.min(inicioIdx + linhasPorPaginaPluggy, totalItens);
                const itensPaginados = pixFiltrados.slice(inicioIdx, fimIdx);

                // Atualiza controles de paginação
                const elResumo = document.getElementById('pluggy-resumo-paginacao');
                if (elResumo) {
                    elResumo.textContent = `Mostrando ${totalItens ? inicioIdx + 1 : 0}-${fimIdx} de ${totalItens}`;
                }
                const elIndicador = document.getElementById('pluggy-indicador-pag');
                if (elIndicador) {
                    elIndicador.textContent = `${paginaAtualPluggy}/${totalPaginas}`;
                }
                const btnAnt = document.getElementById('btn-pag-ant');
                if (btnAnt) btnAnt.disabled = (paginaAtualPluggy <= 1);
                const btnProx = document.getElementById('btn-pag-prox');
                if (btnProx) btnProx.disabled = (paginaAtualPluggy >= totalPaginas);

                // 1. RENDERIZA TABELA (ALTA PERFORMANCE - STRING ACUMULADA)
                const tbody = document.getElementById('tbody-solicitacoes-pluggy');
                if (tbody) {
                    if (itensPaginados.length === 0) {
                        tbody.innerHTML = `
                            <tr>
                                <td colspan="9" class="py-12 text-center text-slate-400">
                                    <i class="fa-solid fa-inbox text-3xl mb-2 text-slate-300 block"></i>
                                    Nenhuma solicitação encontrada para o filtro selecionado.
                                </td>
                            </tr>
                        `;
                    } else {
                        let htmlRows = '';
                        itensPaginados.forEach(p => {
                            const idCurto = p.id ? (p.id.slice(0, 18) + '..') : '---';
                            const recDisplay = MC_CONFIG.escapeHtml(p.recebedor || 'MC Minhaconta Securitizadora C SA');
                            const valorDisplay = MC_CONFIG.formatMoney(p.valor || p.valor_parcela || 0);
                            const dataFmt = p.criado_em || formatarDataPluggy(p.data_criacao);
                            const dataInicioFmt = p.data_inicio_formatada || (p.data_inicio ? formatarDataSimplesPluggy(p.data_inicio) : null);
                            const badgeInicio = (dataInicioFmt && dataInicioFmt !== '---')
                                ? `<div class="mt-1 flex items-center gap-1 text-[10px] text-slate-500 font-medium"><i class="fa-regular fa-calendar-check text-[#0985ff]"></i> 1º débito: <strong class="text-slate-700">${dataInicioFmt}</strong></div>`
                                : '';
                            const nomeSeguro = MC_CONFIG.escapeHtml(p.cliente || 'Cliente');

                            const docDisplay = p.documento 
                                ? `<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 text-slate-700 border border-slate-200">${p.tipo_documento || 'DOC'}: ${p.documento}</span>`
                                : `<span class="text-slate-400 text-[11px] italic">Não informado</span>`;

                            const logoBanco = p.banco_imagem 
                                ? `<img src="${p.banco_imagem}" alt="Logo" class="w-5 h-5 object-contain rounded-md inline-block mr-1.5" onerror="this.style.display='none'">` 
                                : `<i class="fa-solid fa-building-columns text-slate-400 mr-1.5"></i>`;

                            let badgeStatus = 'bg-slate-100 text-slate-600 border-slate-200';
                            let iconeStatus = '<i class="fa-regular fa-clock text-[9px] mr-1"></i>';
                            if (p.status_label === 'Autorizado') {
                                badgeStatus = 'bg-purple-50 text-purple-700 border-purple-200';
                                iconeStatus = '<i class="fa-solid fa-bolt text-[9px] mr-1 text-purple-600"></i>';
                            } else if (p.status_label === 'Concluído') {
                                badgeStatus = 'bg-emerald-50 text-emerald-700 border-emerald-200';
                                iconeStatus = '<i class="fa-solid fa-check text-[9px] mr-1 text-emerald-600"></i>';
                            } else if (p.status_label === 'Erro' || p.status_classe === 'erro' || p.status_label === 'Falha no Banco') {
                                badgeStatus = 'bg-rose-50 text-rose-700 border-rose-200';
                                iconeStatus = '<i class="fa-solid fa-triangle-exclamation text-[9px] mr-1 text-rose-600"></i>';
                            } else if (p.status_label === 'Rejeitado') {
                                badgeStatus = 'bg-rose-50 text-rose-700 border-rose-200';
                                iconeStatus = '<i class="fa-solid fa-ban text-[9px] mr-1 text-rose-600"></i>';
                            } else if (p.status_label === 'Expirado') {
                                badgeStatus = 'bg-slate-100 text-slate-700 border-slate-300';
                                iconeStatus = '<i class="fa-regular fa-clock text-[9px] mr-1 text-slate-500"></i>';
                            } else if (p.status_label === 'Agendado') {
                                badgeStatus = 'bg-sky-50 text-sky-700 border-sky-200';
                                iconeStatus = '<i class="fa-regular fa-calendar-check text-[9px] mr-1 text-sky-600"></i>';
                            } else if (p.status_label === 'Cancelado') {
                                badgeStatus = 'bg-slate-100 text-slate-600 border-slate-200';
                                iconeStatus = '<i class="fa-solid fa-xmark text-[9px] mr-1 text-slate-500"></i>';
                            } else {
                                badgeStatus = 'bg-amber-50 text-amber-800 border-amber-200';
                                iconeStatus = '<i class="fa-solid fa-hourglass-half text-[9px] mr-1 text-amber-600"></i>';
                            }

                            let tagErroHtml = '';
                            if (p.erro && (p.erro.titulo || p.erro.codigo) && p.status_label !== 'Aguardando') {
                                const titErro = MC_CONFIG.escapeHtml(p.erro.titulo || p.erro.codigo);
                                const detErro = MC_CONFIG.escapeHtml(p.erro.detalhe || p.erro.codigo || '');
                                tagErroHtml = `
                                    <div class="mt-1" title="${detErro}">
                                        <span class="inline-flex items-center gap-1 text-[10px] font-medium text-rose-700 bg-rose-50 border border-rose-200/90 px-1.5 py-0.5 rounded cursor-help">
                                            <i class="fa-solid fa-circle-exclamation text-[9px]"></i>
                                            <span class="truncate max-w-[125px]">${titErro}</span>
                                        </span>
                                    </div>
                                `;
                            }

                            let btnLink = '';
                            if (p.payment_url || p.consent_url) {
                                const urlAuth = p.payment_url || p.consent_url;
                                btnLink = `
                                    <button onclick="copiarLinkPagamento('${MC_CONFIG.escapeHtml(urlAuth)}')" class="p-1.5 rounded-lg text-emerald-600 hover:bg-emerald-50 border border-emerald-200 text-xs font-semibold cursor-pointer" title="Copiar link WhatsApp">
                                        <i class="fa-brands fa-whatsapp text-sm"></i>
                                    </button>
                                `;
                            }

                            htmlRows += `
                                <tr class="hover:bg-slate-50/80 transition duration-150">
                                    <td class="py-3 px-3.5">
                                        <div class="flex flex-col gap-0.5">
                                            <span class="font-bold text-[#010157] text-xs leading-snug">${nomeSeguro}</span>
                                            <div>${docDisplay}</div>
                                        </div>
                                    </td>
                                    <td class="py-3 px-3 text-slate-700 text-xs font-medium">
                                        <div class="flex items-center">
                                            ${logoBanco}
                                            <span class="truncate max-w-[130px]" title="${MC_CONFIG.escapeHtml(p.banco_nome || 'Banco')}">${MC_CONFIG.escapeHtml(p.banco_nome || 'Banco')}</span>
                                        </div>
                                    </td>
                                    <td class="py-3 px-3 font-mono text-[11px] text-slate-600" title="${p.id}">
                                        <div class="flex items-center gap-1">
                                            <span>${idCurto}</span>
                                            <button onclick="navigator.clipboard.writeText('${p.id}'); MC_CONFIG.showToast('ID copiado!', 'success')" class="text-slate-400 hover:text-[#0985ff] p-0.5 cursor-pointer" title="Copiar ID">
                                                <i class="fa-regular fa-copy text-[10px]"></i>
                                            </button>
                                        </div>
                                    </td>
                                    <td class="py-3 px-3 text-slate-600 text-xs max-w-[140px] truncate" title="${recDisplay}">${recDisplay}</td>
                                    <td class="py-3 px-3 text-right">
                                        <div class="font-black text-slate-900 font-mono text-xs">${valorDisplay}</div>
                                        <span class="text-[10px] text-slate-400 font-semibold block">Mensal</span>
                                    </td>
                                    <td class="py-3 px-3 text-center">
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${badgeStatus}">
                                            ${iconeStatus} ${p.status_label || 'Pendente'}
                                        </span>
                                        ${tagErroHtml}
                                    </td>
                                    <td class="py-3 px-3 text-slate-600 text-[11px] whitespace-nowrap">
                                        <div class="font-medium text-slate-800">${dataFmt}</div>
                                        ${badgeInicio}
                                    </td>
                                    <td class="py-3 px-3 text-center">
                                        <div class="flex items-center justify-center gap-1.5">
                                            ${btnLink}
                                            <button onclick="consultarPix('${p.id}', null, '${nomeSeguro}')" class="px-2.5 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-[#0985ff] border border-blue-200 text-xs font-bold transition flex items-center gap-1 cursor-pointer" title="Ver Detalhes Oficiais da Pluggy">
                                                <i class="fa-solid fa-eye"></i> Detalhes
                                            </button>
                                            <button onclick="abrirModalJson('${p.id}')" class="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 border border-slate-200 text-xs cursor-pointer" title="Ver JSON da Pluggy">
                                                <i class="fa-solid fa-code"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            `;
                        });
                        tbody.innerHTML = htmlRows;
                    }
                }

                // 2. RENDERIZA VISÃO EM CARDS (ALTA PERFORMANCE)
                if (modoExibicaoPix === 'cards') {
                    if (itensPaginados.length === 0) {
                        divLista.innerHTML = `
                            <div class="text-center py-16 text-slate-400">
                                <i class="fa-solid fa-inbox text-3xl mb-2 text-slate-300"></i>
                                <p class="text-xs">Nenhum contrato encontrado para o filtro selecionado.</p>
                            </div>
                        `;
                        return;
                    }

                    let htmlCards = '';
                    itensPaginados.forEach(pix => {
                        const dataCriacaoFormatada = pix.criado_em || formatarDataPluggy(pix.data_criacao);
                        const dataInicioCard = pix.data_inicio_formatada || (pix.data_inicio ? formatarDataSimplesPluggy(pix.data_inicio) : null);
                        const badgeInicioCard = (dataInicioCard && dataInicioCard !== '---')
                            ? `<span class="text-slate-500 font-medium ml-1.5"><i class="fa-regular fa-calendar-check text-[#0985ff]"></i> 1º débito: <strong class="text-slate-700">${dataInicioCard}</strong></span>`
                            : '';
                        const valorParcelaForm = MC_CONFIG.formatMoney(pix.valor || pix.valor_parcela || 0);
                        const nomeSeguro = MC_CONFIG.escapeHtml(pix.cliente);
                        const docDisplay = pix.documento 
                            ? `<span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[10px] font-mono font-bold">${pix.tipo_documento}: ${pix.documento}</span>` 
                            : (pix.cpf ? `<span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[10px] font-mono font-bold">${pix.cpf}</span>` : '');

                        const logoBanco = pix.banco_imagem 
                            ? `<img src="${pix.banco_imagem}" alt="Logo" class="w-6 h-6 object-contain rounded-md" onerror="this.style.display='none'">` 
                            : `<i class="fa-solid fa-building-columns text-slate-400"></i>`;

                        let btnLinkWhats = '';
                        if (pix.payment_url || pix.consent_url) {
                            const linkAutorizacao = pix.payment_url || pix.consent_url;
                            btnLinkWhats = `
                                <button onclick="copiarLinkPagamento('${MC_CONFIG.escapeHtml(linkAutorizacao)}')" class="bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 px-3 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer" title="Copiar link para WhatsApp">
                                    <i class="fa-brands fa-whatsapp text-emerald-600 text-sm"></i> Copiar Link
                                </button>
                            `;
                        }

                        let cardAvisoErro = '';
                        if (pix.erro && pix.erro.titulo) {
                            cardAvisoErro = `
                                <div class="mt-3 p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2">
                                    <i class="fa-solid fa-triangle-exclamation text-rose-600 mt-0.5 flex-shrink-0"></i>
                                    <div>
                                        <span class="font-bold">${MC_CONFIG.escapeHtml(pix.erro.titulo)}</span>:
                                        <span class="text-rose-700">${MC_CONFIG.escapeHtml(pix.erro.detalhe || '')}</span>
                                    </div>
                                </div>
                            `;
                        }

                        htmlCards += `
                            <div class="bg-white border border-slate-200/90 rounded-2xl p-5 hover:border-[#0985ff]/50 transition duration-200 shadow-sm">
                                <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                                    <div class="flex items-start gap-3.5">
                                        <div class="w-10 h-10 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
                                            ${logoBanco}
                                        </div>
                                        <div>
                                            <div class="flex items-center gap-2 flex-wrap">
                                                <h3 class="font-bold text-[#010157] text-sm">${nomeSeguro}</h3>
                                                ${docDisplay}
                                                <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-md border ${pix.status_badge || 'bg-slate-100 text-slate-600 border-slate-200'}">
                                                    ${pix.status_label || 'Pendente'}
                                                </span>
                                            </div>
                                            <div class="flex items-center gap-3 text-xs text-slate-500 mt-1 flex-wrap">
                                                <span><i class="fa-solid fa-building-columns text-slate-400"></i> ${MC_CONFIG.escapeHtml(pix.banco_nome || 'Banco')}</span>
                                                <span class="text-slate-300">•</span>
                                                <span><i class="fa-regular fa-clock text-slate-400"></i> ${dataCriacaoFormatada}</span>
                                                ${badgeInicioCard}
                                            </div>
                                        </div>
                                    </div>

                                    <div class="flex items-center justify-between lg:justify-end gap-3 w-full lg:w-auto pt-3 lg:pt-0 border-t lg:border-t-0 border-slate-100">
                                        <div class="text-left lg:text-right mr-2">
                                            <span class="text-[10px] text-slate-400 font-bold uppercase block">Valor</span>
                                            <span class="text-base font-black text-[#010157] font-mono">${valorParcelaForm}</span>
                                        </div>

                                        <div class="flex items-center gap-2">
                                            ${btnLinkWhats}
                                            <button onclick="consultarPix('${pix.id}', 'detalhe-pix-${pix.id}', '${nomeSeguro}')" class="bg-white hover:bg-slate-50 text-[#010157] border border-slate-300 px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-sm cursor-pointer">
                                                <i class="fa-solid fa-file-invoice-dollar text-[#0985ff]"></i> Detalhes
                                            </button>
                                            <button onclick="abrirModalJson('${pix.id}')" class="bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200 px-2.5 py-2 rounded-xl text-xs transition cursor-pointer" title="Ver JSON da Pluggy">
                                                <i class="fa-solid fa-code"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                ${cardAvisoErro}
                                <div id="detalhe-pix-${pix.id}" class="hidden bg-slate-50 border border-slate-200 rounded-xl p-5 mt-4"></div>
                            </div>
                        `;
                    });
                    divLista.innerHTML = htmlCards;
                }

            } else {
                // RENDERIZACAO DE OPEN FINANCE (ALTA PERFORMANCE)
                const ofFiltrados = todosOsClientes.filter(cliente => {
                    const matchTexto = (cliente.cliente || '').toLowerCase().includes(termoBusca);
                    const matchTipo = (cliente.tipo === 'open_finance') || (cliente.tipo === 'securitizadora') || (!cliente.payment_intent_id && Boolean(cliente.item_id));
                    return matchTexto && matchTipo;
                });

                badgeTotal.innerHTML = `Exibindo <strong class="text-[#010157] font-bold">${ofFiltrados.length}</strong> conexões Open Finance`;

                if (ofFiltrados.length === 0) {
                    divLista.innerHTML = `
                        <div class="text-center py-16 text-slate-400">
                            <i class="fa-solid fa-inbox text-3xl mb-2 text-slate-300"></i>
                            <p class="text-xs">Nenhum registro de <strong>Open Finance</strong> encontrado.</p>
                        </div>
                    `;
                    return;
                }

                let htmlOf = '';
                ofFiltrados.forEach(cliente => {
                    const dataFormatada = MC_CONFIG.formatDate(cliente.data_conexao);
                    const nomeSeguro = MC_CONFIG.escapeHtml(cliente.cliente);
                    const clienteId = cliente.id || Math.random().toString(36).substring(7);
                    const isSecuritizadora = cliente.tipo === 'securitizadora' || (cliente.cliente && cliente.cliente.toUpperCase().includes('SECURITIZADORA'));

                    const badgeOf = isSecuritizadora
                        ? `<span class="px-2.5 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] uppercase font-bold rounded-md border border-emerald-200 flex items-center gap-1"><i class="fa-solid fa-building-shield"></i> Conta Securitizadora MC</span>`
                        : `<span class="px-2.5 py-0.5 bg-blue-50 text-[#0985ff] text-[10px] uppercase font-bold rounded-md border border-blue-200">Open Finance</span>`;

                    const botoesAcao = isSecuritizadora
                        ? `
                            <a href="securitizadora.html" class="btn-brand-primary text-white px-4 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 flex-1 md:flex-none cursor-pointer shadow-sm">
                                <i class="fa-solid fa-landmark"></i> Abrir Ambiente Securitizadora
                            </a>
                            <button onclick="buscarExtratos('${MC_CONFIG.escapeHtml(cliente.item_id)}', 'detalhe-of-${clienteId}', '${nomeSeguro}')" class="bg-white hover:bg-slate-50 text-[#010157] border border-slate-200 px-3 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-sm">
                                <i class="fa-solid fa-magnifying-glass-chart text-[#0985ff]"></i> Prévia Rápida
                            </button>
                        `
                        : `
                            <a href="extratos.html?item=${encodeURIComponent(cliente.item_id)}&cliente=${encodeURIComponent(cliente.cliente)}" target="_blank" class="btn-brand-primary text-white px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer shadow-sm" title="Abrir Dossiê Cadastral e Extrato Completo (Entradas, Saídas, Contas e Identidade)">
                                <i class="fa-solid fa-address-card"></i> Dossiê & Extrato
                            </a>
                            <button onclick="buscarExtratos('${MC_CONFIG.escapeHtml(cliente.item_id)}', 'detalhe-of-${clienteId}', '${nomeSeguro}')" class="bg-white hover:bg-slate-50 text-[#010157] border border-slate-200 px-3 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-sm" title="Abrir prévia rápida inline">
                                <i class="fa-solid fa-magnifying-glass-chart text-[#0985ff]"></i> Prévia
                            </button>
                        `;

                    const cardBg = isSecuritizadora ? 'bg-gradient-to-r from-emerald-50/30 via-white to-white border-emerald-300/80 shadow-md ring-1 ring-emerald-200/50' : 'bg-white border-slate-200/90 shadow-sm';

                    htmlOf += `
                        <div class="${cardBg} border rounded-2xl p-5 hover:border-[#0985ff]/50 transition duration-200">
                            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                                <div>
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <h3 class="font-bold text-[#010157] text-sm">${nomeSeguro}</h3>
                                        ${badgeOf}
                                    </div>
                                    <p class="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                                        <i class="fa-regular fa-clock"></i> Conectado em: ${dataFormatada}
                                    </p>
                                </div>
                                <div class="flex items-center gap-2 w-full md:w-auto flex-wrap">
                                    ${botoesAcao}
                                </div>
                            </div>
                            <div id="detalhe-of-${clienteId}" class="hidden bg-slate-50 border border-slate-200 rounded-xl p-5 mt-4"></div>
                        </div>
                    `;
                });
                divLista.innerHTML = htmlOf;
            }
        }

        function copiarLinkPagamento(url) {
            navigator.clipboard.writeText(url).then(() => {
                MC_CONFIG.showToast("Link de autorizacao copiado para a area de transferencia!", "success");
            }).catch(() => {
                MC_CONFIG.showToast("Erro ao copiar link.", "error");
            });
        }

        let jsonAtualInspecao = "";
        function abrirModalJson(intentId) {
            const item = todosOsPix.find(p => p.id === intentId);
            if (!item) return;
            jsonAtualInspecao = JSON.stringify(item.raw, null, 2);
            document.getElementById('conteudo-json-pluggy').textContent = jsonAtualInspecao;
            document.getElementById('modal-json-pluggy').classList.remove('hidden');
        }

        function fecharModalJson() {
            document.getElementById('modal-json-pluggy').classList.add('hidden');
        }

        function copiarJsonBruto() {
            if (!jsonAtualInspecao) return;
            navigator.clipboard.writeText(jsonAtualInspecao).then(() => {
                MC_CONFIG.showToast("JSON copiado para a area de transferencia!", "success");
            });
        }

        // ============================================================
        // EXTRATOS OPEN FINANCE (CONTAS & TRANSACOES COM SYNC ATIVO)
        // ============================================================

        async function forcarSincronizacaoExtrato(itemId, divId, nomeCliente) {
            const btnSync = document.getElementById(`btn-sync-${divId}`);
            if (btnSync) {
                btnSync.disabled = true;
                btnSync.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin mr-1"></i> Solicitando ao banco...`;
            }
            try {
                const res = await MC_CONFIG.authFetch(`/sincronizar-item/${itemId}`, { method: 'POST' });
                const data = await res.json();
                if (data.sucesso) {
                    MC_CONFIG.showToast(data.mensagem || "Sincronização iniciada com o banco!", "success");
                    // Recarrega extrato em 3 segundos para acompanhar o download da Pluggy
                    setTimeout(() => buscarExtratos(itemId, divId, nomeCliente, true), 3000);
                } else {
                    MC_CONFIG.showToast(data.erro || "Não foi possível sincronizar agora.", "warning");
                    if (btnSync) {
                        btnSync.disabled = false;
                        btnSync.innerHTML = `<i class="fa-solid fa-rotate mr-1"></i> Sincronizar com Banco`;
                    }
                }
            } catch (e) {
                MC_CONFIG.showToast("Erro ao contatar servidor de sincronização.", "error");
                if (btnSync) {
                    btnSync.disabled = false;
                    btnSync.innerHTML = `<i class="fa-solid fa-rotate mr-1"></i> Sincronizar com Banco`;
                }
            }
        }

        async function buscarExtratos(itemId, divId, nomeCliente, forcarAbertura = false) {
            const areaDetalhe = document.getElementById(divId);
            if (!forcarAbertura && !areaDetalhe.classList.contains('hidden')) {
                areaDetalhe.classList.add('hidden');
                return;
            }

            areaDetalhe.classList.remove('hidden');
            areaDetalhe.innerHTML = `
                <div class="flex items-center justify-center py-8 text-[#0985ff] text-xs gap-2">
                    <i class="fa-solid fa-circle-notch fa-spin text-lg"></i>
                    Buscando contas bancárias e extrato atualizado na Pluggy...
                </div>
            `;

            try {
                const resposta = await MC_CONFIG.authFetch(`/consultar-dados/${itemId}`);
                if (!resposta.ok) throw new Error('Falha ao comunicar com a Pluggy');
                
                const dados = await resposta.json();
                const item = dados.item || {};
                const contas = dados.results || [];
                const bancoNome = MC_CONFIG.escapeHtml(item.connector?.name || 'Instituição Bancária');
                const ultimaAtualizacao = item.lastUpdatedAt ? MC_CONFIG.formatDate(item.lastUpdatedAt) : 'Hoje';

                if (item.status === 'LOGIN_ERROR' || (contas.length === 0 && item.error)) {
                    const motivo = item.error?.providerMessage || item.error?.message || 'A autorização expirou ou foi revogada no aplicativo do banco.';
                    areaDetalhe.innerHTML = `
                        <div class="bg-amber-50/90 border border-amber-200 rounded-2xl p-5 text-amber-900">
                            <div class="flex items-start gap-3">
                                <div class="w-10 h-10 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center text-lg flex-shrink-0">
                                    <i class="fa-solid fa-triangle-exclamation"></i>
                                </div>
                                <div class="flex-1">
                                    <h4 class="font-bold text-sm text-[#010157]">Autorização Expirada ou Revogada no Banco</h4>
                                    <p class="text-xs text-slate-600 mt-1">Banco: <strong>${bancoNome}</strong>. Motivo: ${MC_CONFIG.escapeHtml(motivo)}</p>
                                    <p class="text-[11px] text-slate-500 mt-2">O cliente precisa realizar uma nova autorização para sincronizar.</p>
                                </div>
                                <button onclick="document.getElementById('${divId}').classList.add('hidden')" class="text-slate-400 hover:text-slate-600 p-1 text-xs">
                                    <i class="fa-solid fa-xmark"></i>
                                </button>
                            </div>
                        </div>
                    `;
                    return;
                }

                // Banner se a conexão ainda estiver sincronizando no banco
                let bannerSincronizando = '';
                if (item.status === 'UPDATING') {
                    bannerSincronizando = `
                        <div class="bg-blue-50 border border-blue-200 rounded-2xl p-3.5 text-blue-900 mb-4 flex items-center justify-between flex-wrap gap-2">
                            <div class="flex items-center gap-2.5">
                                <i class="fa-solid fa-circle-notch fa-spin text-base text-[#0985ff]"></i>
                                <div>
                                    <strong class="text-xs block text-[#010157]">Sincronização em andamento com o banco ${bancoNome}...</strong>
                                    <span class="text-[11px] text-slate-500">As movimentações recentes estão sendo coletadas. A tela atualizará automaticamente.</span>
                                </div>
                            </div>
                            <button onclick="buscarExtratos('${MC_CONFIG.escapeHtml(itemId)}', '${divId}', '${MC_CONFIG.escapeHtml(nomeCliente)}', true)" class="px-3 py-1 bg-white border border-blue-200 rounded-lg text-xs font-bold text-[#0985ff] hover:bg-blue-50 transition cursor-pointer shadow-2xs">
                                Checar Agora
                            </button>
                        </div>
                    `;
                    // Auto-refresh em 4 segundos
                    setTimeout(() => {
                        const area = document.getElementById(divId);
                        if (area && !area.classList.contains('hidden')) {
                            buscarExtratos(itemId, divId, nomeCliente, true);
                        }
                    }, 4000);
                }

                if (contas.length === 0) {
                    areaDetalhe.innerHTML = `
                        ${bannerSincronizando}
                        <div class="text-center py-6 text-slate-500 text-xs">
                            <i class="fa-solid fa-building-columns text-2xl text-slate-300 mb-2 block"></i>
                            <p>Nenhuma conta ativa encontrada para este cliente no banco <strong>${bancoNome}</strong>.</p>
                            <div class="mt-3 flex items-center justify-center gap-2">
                                <button onclick="forcarSincronizacaoExtrato('${MC_CONFIG.escapeHtml(itemId)}', '${divId}', '${MC_CONFIG.escapeHtml(nomeCliente)}')" class="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-lg hover:bg-emerald-100 cursor-pointer">
                                    <i class="fa-solid fa-rotate mr-1"></i> Tentar Sincronizar Novamente
                                </button>
                                <button onclick="document.getElementById('${divId}').classList.add('hidden')" class="text-[11px] text-slate-400 hover:underline">Fechar</button>
                            </div>
                        </div>
                    `;
                    return;
                }

                let htmlContas = `
                    ${bannerSincronizando}
                    <div class="flex items-center justify-between pb-3 mb-4 border-b border-slate-200 flex-wrap gap-2">
                        <div class="flex items-center gap-2">
                            <i class="fa-solid fa-building-columns text-[#0985ff]"></i>
                            <div>
                                <h4 class="font-bold text-[#010157] text-sm">${bancoNome}</h4>
                                <span class="text-[10px] text-slate-400">Última atualização: ${ultimaAtualizacao}</span>
                            </div>
                        </div>
                        <div class="flex items-center gap-2 flex-wrap">
                            <button onclick="forcarSincronizacaoExtrato('${MC_CONFIG.escapeHtml(itemId)}', '${divId}', '${MC_CONFIG.escapeHtml(nomeCliente)}')" id="btn-sync-${divId}" class="text-xs font-bold text-emerald-700 hover:text-emerald-800 flex items-center gap-1.5 bg-emerald-50 hover:bg-emerald-100 px-3 py-1.5 rounded-xl border border-emerald-200 shadow-2xs cursor-pointer transition" title="Dispara sincronização direta do extrato atual no banco">
                                <i class="fa-solid fa-rotate"></i> Sincronizar com Banco
                            </button>
                            <a href="extratos.html?item=${encodeURIComponent(itemId)}&cliente=${encodeURIComponent(nomeCliente)}" target="_blank" class="text-xs font-bold text-[#0985ff] hover:text-[#0772dc] flex items-center gap-1 bg-blue-50 px-3 py-1.5 rounded-xl border border-blue-200 shadow-2xs">
                                <i class="fa-solid fa-file-invoice-dollar"></i> Tela Cheia
                            </a>
                            <span class="text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full flex items-center gap-1">
                                <i class="fa-solid fa-circle text-[6px]"></i> Conexão Ativa
                            </span>
                            <button onclick="document.getElementById('${divId}').classList.add('hidden')" class="text-slate-400 hover:text-slate-600 p-1 text-xs cursor-pointer">
                                <i class="fa-solid fa-xmark"></i>
                            </button>
                        </div>
                    </div>
                `;

                contas.forEach(conta => {
                    const saldoFormatado = MC_CONFIG.formatMoney(conta.balance);
                    const nomeConta = MC_CONFIG.escapeHtml(conta.name || 'Conta Bancária');
                    const subtipo = MC_CONFIG.escapeHtml(conta.subtype || 'Corrente');
                    const agencia = MC_CONFIG.escapeHtml(conta.agency || (conta.bankData?.transferNumber ? conta.bankData.transferNumber.split('/')[1] : null) || '---');
                    const numero = MC_CONFIG.escapeHtml(conta.number || '---');
                    const titular = MC_CONFIG.escapeHtml(conta.owner || 'Não informado');
                    const cpfTitular = conta.taxNumber ? ` | CPF: ${MC_CONFIG.escapeHtml(conta.taxNumber)}` : '';

                    htmlContas += `
                        <div class="border-b border-slate-200 pb-5 mb-5 last:border-0 last:pb-0 last:mb-0">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-bold text-[#010157] text-sm">${nomeConta}</h4>
                                    <div class="text-[11px] text-slate-700 font-medium mt-0.5">Titular: <strong>${titular}</strong>${cpfTitular}</div>
                                    <div class="text-[11px] text-slate-500 mt-0.5">Agência: ${agencia} | Conta: ${numero} | ${subtipo}</div>
                                </div>
                                <div class="text-right">
                                    <span class="text-[10px] text-slate-400 uppercase font-bold block mb-0.5">Saldo Disponível</span>
                                    <span class="text-[#0985ff] font-extrabold text-base font-mono">${saldoFormatado}</span>
                                </div>
                            </div>
                            <div id="transacoes-${conta.id}" class="bg-white p-4 rounded-xl border border-slate-200 mt-3 shadow-sm">
                                <div class="flex items-center justify-center py-4 text-xs text-slate-400 gap-2">
                                    <i class="fa-solid fa-circle-notch fa-spin text-[#0985ff]"></i>
                                    Carregando histórico de transações...
                                </div>
                            </div>
                        </div>
                    `;
                });

                areaDetalhe.innerHTML = htmlContas;
                contas.forEach(conta => buscarMovimentacoes(conta.id));
            } catch (erro) {
                areaDetalhe.innerHTML = `
                    <div class="text-center py-4 text-rose-500 text-xs">
                        <i class="fa-solid fa-triangle-exclamation mr-1"></i> Erro ao carregar extrato: ${MC_CONFIG.escapeHtml(erro.message)}
                        <button onclick="document.getElementById('${divId}').classList.add('hidden')" class="ml-2 text-slate-400 hover:underline">Fechar</button>
                    </div>
                `;
            }
        }

        async function buscarMovimentacoes(accountId) {
            const areaTransacoes = document.getElementById(`transacoes-${accountId}`);
            try {
                const resposta = await MC_CONFIG.authFetch(`/consultar-transacoes/${accountId}`);
                const payload = await resposta.json();
                if (!resposta.ok) throw new Error(payload.erro || 'Falha ao buscar movimentações');
                
                const transacoesData = payload.results || payload.data || []; 
                if (transacoesData.length === 0) {
                    areaTransacoes.innerHTML = '<p class="text-xs text-slate-400 text-center py-2">Sem movimentações recentes no período.</p>';
                    return;
                }

                let htmlTx = `
                    <div class="flex justify-between items-center mb-3">
                        <strong class="text-[11px] font-bold text-[#010157] uppercase tracking-wider">Histórico Recente</strong>
                        <span class="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-bold">${transacoesData.length} registros</span>
                    </div>
                    <div class="space-y-1.5 max-h-56 overflow-y-auto pr-1 custom-scrollbar">
                `;
                
                transacoesData.forEach(tx => {
                    if (tx.amount == null) return; 
                    const valorForm = MC_CONFIG.formatMoney(Math.abs(tx.amount));
                    const isNegativo = tx.amount < 0;
                    const cor = isNegativo ? 'text-slate-800' : 'text-[#0985ff] font-semibold';
                    const sinal = isNegativo ? '-' : '+';
                    const dataBR = tx.date ? new Date(tx.date).toLocaleDateString('pt-BR') : '---';
                    const descSegura = MC_CONFIG.escapeHtml(tx.description || 'Transação');

                    htmlTx += `
                        <div class="flex justify-between items-center text-xs py-2 px-2.5 hover:bg-slate-50 transition rounded-lg border-b border-slate-100 last:border-0">
                            <span class="text-slate-700 truncate max-w-[220px] md:max-w-md">
                                <span class="text-slate-400 font-mono text-[11px] mr-2">${dataBR}</span> 
                                ${descSegura}
                            </span>
                            <span class="${cor} font-mono text-xs whitespace-nowrap ml-2">${sinal} ${valorForm}</span>
                        </div>
                    `;
                });
                
                htmlTx += '</div>';
                areaTransacoes.innerHTML = htmlTx;
            } catch (erro) {
                areaTransacoes.innerHTML = `<p class="text-xs text-rose-500 text-center py-2">Falha nas transações: ${MC_CONFIG.escapeHtml(erro.message)}</p>`;
            }
        }

        // ============================================================
        // EXTRATO ANALITICO DO PIX AUTOMATICO
        // ============================================================

        function fecharModalDetalhesPluggy() {
            const modal = document.getElementById('modal-detalhe-operacao-pluggy');
            if (modal) modal.classList.add('hidden');
        }

        async function consultarPix(intentId, divId, nomeCliente) {
            const modal = document.getElementById('modal-detalhe-operacao-pluggy');
            const corpoModal = document.getElementById('corpo-detalhe-pluggy');
            const areaDetalheInline = divId ? document.getElementById(divId) : null;

            if (areaDetalheInline && !areaDetalheInline.classList.contains('hidden')) {
                areaDetalheInline.classList.add('hidden');
                return;
            }

            if (modal) {
                modal.classList.remove('hidden');
                document.getElementById('det-topo-criado-em').textContent = 'Carregando...';
                document.getElementById('det-topo-autorizado-em').textContent = 'Carregando...';
                document.getElementById('det-topo-atualizado-em').textContent = 'Carregando...';
                const elBadgeTopo = document.getElementById('det-topo-status-badge');
                if (elBadgeTopo) elBadgeTopo.innerHTML = '<span class="text-xs text-slate-400"><i class="fa-solid fa-circle-notch fa-spin"></i></span>';
                corpoModal.innerHTML = `
                    <div class="flex flex-col items-center justify-center py-20 text-slate-400 gap-3">
                        <i class="fa-solid fa-circle-notch fa-spin text-[#0985ff] text-3xl"></i>
                        <span class="text-xs font-semibold text-slate-600">Buscando dados oficiais do Pix Automático na Pluggy...</span>
                    </div>
                `;
            }

            if (areaDetalheInline) {
                areaDetalheInline.classList.remove('hidden');
                areaDetalheInline.innerHTML = `
                    <div class="flex items-center justify-center py-6 text-slate-500 text-xs gap-2">
                        <i class="fa-solid fa-circle-notch fa-spin text-lg text-[#0985ff]"></i>
                        Carregando detalhes da operação...
                    </div>
                `;
            }

            try {
                const resposta = await MC_CONFIG.authFetch(`/consultar-pix/${intentId}`);
                if (!resposta.ok) throw new Error('Falha ao consultar operação de Pix na Pluggy');
                
                const pix = await resposta.json();
                const cfg = pix.configuracao_pix || {};
                const cli = pix.cliente || {};
                const rec = pix.recebedor || {};
                const pag = pix.pagamentos || {};

                document.getElementById('det-topo-criado-em').textContent = pix.criado_em || '---';
                document.getElementById('det-topo-autorizado-em').textContent = pix.autorizado_em || '---';
                document.getElementById('det-topo-atualizado-em').textContent = pix.atualizado_em || '---';

                // 1. Badge de Status no Cabeçalho Superior
                const elBadgeTopo = document.getElementById('det-topo-status-badge');
                if (elBadgeTopo) {
                    let classeBadge = 'bg-slate-100 text-slate-700 border-slate-300';
                    let iconeBadge = '<i class="fa-regular fa-clock"></i>';
                    if (pix.status_label === 'Autorizado') {
                        classeBadge = 'bg-purple-100 text-purple-800 border-purple-200';
                        iconeBadge = '<i class="fa-solid fa-bolt text-purple-600"></i>';
                    } else if (pix.status_label === 'Concluído') {
                        classeBadge = 'bg-emerald-100 text-emerald-800 border-emerald-200';
                        iconeBadge = '<i class="fa-solid fa-check text-emerald-600"></i>';
                    } else if (pix.status_label === 'Erro') {
                        classeBadge = 'bg-rose-100 text-rose-800 border-rose-200';
                        iconeBadge = '<i class="fa-solid fa-triangle-exclamation text-rose-600"></i>';
                    } else if (pix.status_label === 'Rejeitado') {
                        classeBadge = 'bg-rose-100 text-rose-800 border-rose-200';
                        iconeBadge = '<i class="fa-solid fa-ban text-rose-600"></i>';
                    } else if (pix.status_label === 'Expirado') {
                        classeBadge = 'bg-slate-100 text-slate-700 border-slate-300';
                        iconeBadge = '<i class="fa-regular fa-clock text-slate-500"></i>';
                    } else if (pix.status_label === 'Agendado') {
                        classeBadge = 'bg-sky-100 text-sky-800 border-sky-200';
                        iconeBadge = '<i class="fa-regular fa-calendar-check text-sky-600"></i>';
                    } else if (pix.status_label === 'Cancelado') {
                        classeBadge = 'bg-slate-100 text-slate-600 border-slate-200';
                        iconeBadge = '<i class="fa-solid fa-xmark text-slate-500"></i>';
                    } else {
                        classeBadge = 'bg-amber-100 text-amber-800 border-amber-200';
                        iconeBadge = '<i class="fa-solid fa-hourglass-half text-amber-600"></i>';
                    }

                    elBadgeTopo.innerHTML = `
                        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${classeBadge}">
                            ${iconeBadge} ${pix.status_label || 'Pendente'}
                        </span>
                    `;
                }

                // 2. Banner de Diagnóstico Oficial Pluggy (Erro ou Sucesso)
                let bannerDiagnostico = '';
                if (pix.erro && pix.erro.tem_erro) {
                    const err = pix.erro;
                    const titSeguro = MC_CONFIG.escapeHtml(err.titulo || 'Falha na Autorização');
                    const detSeguro = MC_CONFIG.escapeHtml(err.detalhe || 'Ocorreu um erro no processamento junto à instituição financeira.');
                    const codSeguro = MC_CONFIG.escapeHtml(err.codigo || 'ERRO');
                    const acaoSegura = MC_CONFIG.escapeHtml(err.acao || 'Reenviar link de autorização ao cliente');
                    const bancoSeguro = MC_CONFIG.escapeHtml(err.banco_nome || cli.instituicao || 'Instituição Bancária');
                    const linkReenvio = pix.consent_url || pix.payment_url || '';

                    let btnAcaoReenvio = '';
                    if (linkReenvio) {
                        btnAcaoReenvio = `
                            <button onclick="copiarLinkPagamento('${MC_CONFIG.escapeHtml(linkReenvio)}')" class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-xs transition cursor-pointer">
                                <i class="fa-brands fa-whatsapp"></i> Copiar Link WhatsApp
                            </button>
                        `;
                    }

                    bannerDiagnostico = `
                        <!-- CARD DE DIAGNÓSTICO DE RECUSA / ERRO OFICIAL PLUGGY -->
                        <div class="bg-gradient-to-r from-rose-50/95 via-rose-50/70 to-white border-2 border-rose-300/80 rounded-2xl p-5 shadow-xs animate-in fade-in duration-150">
                            <div class="flex items-start gap-3.5">
                                <div class="w-10 h-10 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center text-lg flex-shrink-0 shadow-2xs">
                                    <i class="fa-solid fa-triangle-exclamation"></i>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <div class="flex flex-wrap items-center justify-between gap-2">
                                        <div class="flex items-center gap-2 flex-wrap">
                                            <h4 class="font-extrabold text-sm text-rose-950">${titSeguro}</h4>
                                            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-100 text-rose-800 border border-rose-200">${codSeguro}</span>
                                        </div>
                                        <span class="text-xs text-rose-700 font-semibold flex items-center gap-1.5 bg-white/90 px-2.5 py-0.5 rounded-md border border-rose-200">
                                            <i class="fa-solid fa-building-columns text-rose-500"></i> ${bancoSeguro}
                                        </span>
                                    </div>
                                    <p class="text-xs text-rose-800 mt-2 leading-relaxed font-normal">${detSeguro}</p>
                                    <div class="mt-4 pt-3 border-t border-rose-200 flex flex-wrap items-center justify-between gap-3">
                                        <div class="flex items-center gap-1.5 text-xs text-rose-900 font-medium">
                                            <i class="fa-solid fa-circle-info text-rose-500"></i>
                                            <span>Ação recomendada: <strong>${acaoSegura}</strong></span>
                                        </div>
                                        ${btnAcaoReenvio}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                } else if (pix.status_label === 'Autorizado') {
                    bannerDiagnostico = `
                        <!-- CARD DE CONTRATO AUTORIZADO (MANDATO ATIVO) -->
                        <div class="bg-gradient-to-r from-purple-50/90 via-purple-50/50 to-white border border-purple-200 rounded-2xl p-4 flex items-center justify-between flex-wrap gap-3 shadow-2xs">
                            <div class="flex items-center gap-3">
                                <div class="w-9 h-9 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center text-base flex-shrink-0">
                                    <i class="fa-solid fa-circle-check"></i>
                                </div>
                                <div>
                                    <h4 class="font-bold text-xs text-[#010157]">Contrato de Pix Automático Autorizado e Ativo</h4>
                                    <p class="text-[11px] text-slate-500">Consentimento aprovado pelo titular no Open Finance. Cobranças automáticas programadas conforme o contrato.</p>
                                </div>
                            </div>
                            <span class="px-3 py-1 rounded-full text-xs font-bold bg-purple-100 text-purple-800 border border-purple-200 flex items-center gap-1.5">
                                <i class="fa-solid fa-bolt text-purple-600"></i> Mandato Ativo
                            </span>
                        </div>
                    `;
                }

                const logoBancoCli = cli.instituicao_logo 
                    ? `<img src="${cli.instituicao_logo}" alt="Logo" class="w-5 h-5 object-contain rounded-md" onerror="this.style.display='none'">` 
                    : `<i class="fa-solid fa-building-columns text-slate-400"></i>`;

                let htmlLinhasPagamentos = '';
                (pag.itens || []).forEach(item => {
                    let badgeItem = 'bg-slate-100 text-slate-700 border-slate-200';
                    let iconeItem = '<i class="fa-regular fa-clock"></i>';
                    if (item.status === 'CONCLUIDO') {
                        badgeItem = 'bg-emerald-50 text-emerald-700 border-emerald-200';
                        iconeItem = '<i class="fa-solid fa-check text-emerald-600"></i>';
                    } else if (item.status === 'AGENDADO' || item.status === 'EM_PROCESSAMENTO') {
                        badgeItem = 'bg-sky-50 text-sky-700 border-sky-200';
                        iconeItem = '<i class="fa-regular fa-calendar-check text-sky-600"></i>';
                    } else if (item.status === 'REJEITADO' || item.status === 'ERRO') {
                        badgeItem = 'bg-rose-50 text-rose-700 border-rose-200';
                        iconeItem = '<i class="fa-solid fa-triangle-exclamation text-rose-600"></i>';
                    } else if (item.status === 'CANCELADO' || item.status === 'EXPIRADO') {
                        badgeItem = 'bg-slate-100 text-slate-600 border-slate-200';
                        iconeItem = '<i class="fa-solid fa-ban text-slate-400"></i>';
                    } else if (item.status === 'PENDENTE') {
                        badgeItem = 'bg-amber-50 text-amber-700 border-amber-200';
                        iconeItem = '<i class="fa-solid fa-hourglass-half text-amber-600"></i>';
                    }

                    htmlLinhasPagamentos += `
                        <tr class="border-b border-slate-100 hover:bg-slate-50/80 transition text-xs">
                            <td class="py-3 px-4 font-semibold text-[#010157]">
                                <div class="flex items-center gap-2">
                                    <span class="w-6 h-6 rounded-full bg-slate-100 text-slate-600 font-bold flex items-center justify-center text-[11px]">${item.numero}</span>
                                    <span>${MC_CONFIG.escapeHtml(item.titulo)}</span>
                                </div>
                            </td>
                            <td class="py-3 px-4 text-slate-600 font-mono text-[11px]">${item.data}</td>
                            <td class="py-3 px-4 font-black text-slate-900 font-mono">${item.valor_formatado}</td>
                            <td class="py-3 px-4 text-slate-500 max-w-[200px] truncate" title="${MC_CONFIG.escapeHtml(item.descricao)}">${MC_CONFIG.escapeHtml(item.descricao)}</td>
                            <td class="py-3 px-4 text-center">
                                <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${badgeItem}">
                                    ${iconeItem} ${MC_CONFIG.escapeHtml(item.status_label)}
                                </span>
                            </td>
                        </tr>
                    `;
                });

                const htmlDetalhesPluggy = `
                    ${bannerDiagnostico}

                    <!-- 1. BLOCO CONFIGURAÇÃO PIX AUTOMÁTICO -->
                    <div class="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm">
                        <div class="flex justify-between items-center mb-5 pb-3 border-b border-slate-100">
                            <h4 class="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
                                <i class="fa-solid fa-sliders text-[#0985ff]"></i>
                                CONFIGURAÇÃO PIX AUTOMÁTICO
                            </h4>
                            <span class="text-slate-400 text-xs"><i class="fa-solid fa-chevron-up"></i></span>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 text-xs">
                            <!-- Coluna 1 -->
                            <div class="space-y-4">
                                <div>
                                    <span class="text-[11px] text-slate-400 block font-medium">Intervalo</span>
                                    <span class="text-sm font-bold text-[#010157]">${cfg.intervalo || 'Mensal'}</span>
                                </div>
                                <div>
                                    <span class="text-[11px] text-slate-400 block font-medium">Data de Início</span>
                                    <span class="text-xs font-semibold text-slate-800">${cfg.data_inicio || '---'}</span>
                                </div>
                                <div>
                                    <span class="text-[11px] text-slate-400 block font-medium">Expira em</span>
                                    <span class="text-xs font-semibold text-slate-800">${cfg.expira_em || '---'}</span>
                                </div>
                            </div>
                            <!-- Coluna 2 -->
                            <div class="space-y-4">
                                <div>
                                    <span class="text-[11px] text-slate-400 block font-medium">Valor Fixo</span>
                                    <span class="text-base font-black text-[#010157] font-mono">${cfg.valor_fixo_formatado || 'R$ 0,00'}</span>
                                </div>
                            </div>
                            <!-- Coluna 3 -->
                            <div class="space-y-4">
                                <div>
                                    <span class="text-[11px] text-slate-400 block font-medium">Aceita Retentativa</span>
                                    <span class="text-xs font-semibold text-slate-800">${cfg.aceita_retentativa || 'Sim'}</span>
                                </div>
                                <div>
                                    <span class="text-[11px] text-slate-400 block font-medium">Dias de Retentativa Automática</span>
                                    <span class="text-xs font-semibold text-slate-800 font-mono">${cfg.dias_retentativa || '1, 2, 3'}</span>
                                </div>
                                <div>
                                    <span class="text-[11px] text-slate-400 block font-medium">Agendador</span>
                                    <span class="text-xs font-semibold text-slate-800">${cfg.agendador || 'Sim'}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 2. DOIS CARDS LADO A LADO: CLIENTE E RECEBEDOR -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <!-- CARD DO CLIENTE -->
                        <div class="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between">
                            <div>
                                <div class="flex justify-between items-center mb-5 pb-3 border-b border-slate-100">
                                    <h4 class="text-xs font-bold text-[#010157] flex items-center gap-2">
                                        <i class="fa-regular fa-user text-slate-400"></i>
                                        <span>Cliente <span class="text-slate-300 font-normal">•</span> <strong class="text-[#0985ff]">${cli.nome}</strong></span>
                                    </h4>
                                    <span class="text-slate-400 text-xs"><i class="fa-solid fa-chevron-up"></i></span>
                                </div>
                                <div class="space-y-3.5 text-xs">
                                    <div>
                                        <span class="text-[11px] text-slate-400 block font-medium">ID</span>
                                        <div class="flex items-center gap-1.5 mt-0.5">
                                            <span class="font-mono text-slate-600 text-[11px] select-all">${cli.id}</span>
                                            <button onclick="navigator.clipboard.writeText('${cli.id}'); MC_CONFIG.showToast('ID do cliente copiado!', 'success')" class="text-slate-400 hover:text-[#0985ff] p-0.5 cursor-pointer" title="Copiar ID">
                                                <i class="fa-regular fa-copy text-[11px]"></i>
                                            </button>
                                        </div>
                                    </div>
                                    <div>
                                        <span class="text-[11px] text-slate-400 block font-medium">Nome</span>
                                        <span class="text-sm font-bold text-[#010157] uppercase">${cli.nome}</span>
                                    </div>
                                    <div>
                                        <span class="text-[11px] text-slate-400 block font-medium">CPF/CNPJ</span>
                                        <span class="font-mono text-slate-800 font-bold">${cli.cpf_cnpj}</span>
                                    </div>
                                    <div>
                                        <span class="text-[11px] text-slate-400 block font-medium">Instituição</span>
                                        <div class="flex items-center gap-2 mt-1">
                                            ${logoBancoCli}
                                            <span class="font-semibold text-slate-800">${cli.instituicao}</span>
                                        </div>
                                    </div>
                                    <div class="grid grid-cols-2 gap-4 pt-1">
                                        <div>
                                            <span class="text-[11px] text-slate-400 block font-medium">Agência</span>
                                            <span class="font-mono text-slate-700">${cli.agencia || '-'}</span>
                                        </div>
                                        <div>
                                            <span class="text-[11px] text-slate-400 block font-medium">Conta</span>
                                            <span class="font-mono text-slate-700">${cli.conta || '-'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- CARD DO RECEBEDOR -->
                        <div class="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between">
                            <div>
                                <div class="flex justify-between items-center mb-5 pb-3 border-b border-slate-100">
                                    <h4 class="text-xs font-bold text-[#010157] flex items-center gap-2">
                                        <i class="fa-solid fa-handshake text-slate-400"></i>
                                        <span>Recebedor <span class="text-slate-300 font-normal">•</span> <strong class="text-slate-700">${rec.nome}</strong></span>
                                    </h4>
                                    <span class="text-slate-400 text-xs"><i class="fa-solid fa-chevron-up"></i></span>
                                </div>
                                <div class="space-y-3.5 text-xs">
                                    <div>
                                        <span class="text-[11px] text-slate-400 block font-medium">Razão Social / Nome</span>
                                        <span class="text-sm font-bold text-[#010157]">${rec.nome}</span>
                                    </div>
                                    <div>
                                        <span class="text-[11px] text-slate-400 block font-medium">CNPJ</span>
                                        <span class="font-mono text-slate-800 font-bold">${rec.cnpj}</span>
                                    </div>
                                    <div>
                                        <span class="text-[11px] text-slate-400 block font-medium">Instituição Financeira</span>
                                        <span class="font-semibold text-slate-800">${rec.instituicao}</span>
                                    </div>
                                    <div class="grid grid-cols-2 gap-4 pt-1">
                                        <div>
                                            <span class="text-[11px] text-slate-400 block font-medium">Agência</span>
                                            <span class="font-mono text-slate-700">${rec.agencia || '-'}</span>
                                        </div>
                                        <div>
                                            <span class="text-[11px] text-slate-400 block font-medium">Conta Corrente</span>
                                            <span class="font-mono text-slate-700">${rec.conta || '-'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 3. BLOCO PAGAMENTOS (LISTAGEM OFICIAL) -->
                    <div class="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
                        <div class="px-6 py-4 border-b border-slate-100 flex flex-wrap justify-between items-center gap-3 bg-white">
                            <h4 class="text-xs font-bold text-[#010157] uppercase tracking-wider flex items-center gap-2">
                                <i class="fa-solid fa-money-bill-transfer text-emerald-600"></i>
                                PAGAMENTOS (${pag.total || 0})
                            </h4>
                            <div class="flex items-center gap-3">
                                <span class="text-xs text-slate-500 font-medium">${pag.indicador || ''}</span>
                                <button onclick="consultarPix('${intentId}', '${divId || ''}', '${MC_CONFIG.escapeHtml(nomeCliente)}')" class="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition cursor-pointer" title="Atualizar">
                                    <i class="fa-solid fa-rotate-right text-xs"></i>
                                </button>
                                <button onclick="MC_CONFIG.showToast('Módulo de agendamento acoplado ao contrato da Pluggy', 'info')" class="btn-brand-primary text-white text-xs font-bold px-3.5 py-1.5 rounded-xl flex items-center gap-1.5 shadow-sm cursor-pointer">
                                    <i class="fa-regular fa-calendar-plus"></i> Agendar Pagamento
                                </button>
                            </div>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left border-collapse text-xs">
                                <thead>
                                    <tr class="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase border-b border-slate-100">
                                        <th class="py-3 px-4">Item / Cobrança</th>
                                        <th class="py-3 px-4">Data Vencimento</th>
                                        <th class="py-3 px-4">Valor</th>
                                        <th class="py-3 px-4">Descrição</th>
                                        <th class="py-3 px-4 text-center">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${htmlLinhasPagamentos}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;

                if (corpoModal) corpoModal.innerHTML = htmlDetalhesPluggy;
                if (areaDetalheInline) areaDetalheInline.innerHTML = htmlDetalhesPluggy;

            } catch (erro) {
                const erroHtml = `
                    <div class="text-center py-10 text-rose-500 text-xs">
                        <i class="fa-solid fa-triangle-exclamation text-2xl mb-2 text-rose-400 block"></i>
                        Erro ao carregar detalhes da operação: ${MC_CONFIG.escapeHtml(erro.message)}
                        <div class="mt-4">
                            <button onclick="fecharModalDetalhesPluggy()" class="btn-brand-primary text-white text-xs font-bold px-4 py-2 rounded-xl">Fechar</button>
                        </div>
                    </div>
                `;
                if (corpoModal) corpoModal.innerHTML = erroHtml;
                if (areaDetalheInline) areaDetalheInline.innerHTML = erroHtml;
            }
        }

        function inicializarDatasFormularioPix() {
            const elInicio = document.getElementById("dataInicio");
            const elFim = document.getElementById("dataFim");
            if (elInicio && !elInicio.value) {
                const d = new Date();
                d.setDate(d.getDate() + 1);
                elInicio.value = d.toISOString().split('T')[0];
            }
            if (elFim && !elFim.value) {
                const dFim = new Date();
                dFim.setFullYear(dFim.getFullYear() + 1);
                elFim.value = dFim.toISOString().split('T')[0];
            }
        }

        // Inicializacao com verificacao de autenticacao
        document.addEventListener('DOMContentLoaded', () => {
            if (!MC_CONFIG.isAuthenticated()) {
                window.location.href = 'gestor-login.html';
                return;
            }

            const usuario = MC_CONFIG.getAuthUser();
            if (usuario) {
                const elNome = document.getElementById('nome-usuario-gestor');
                if (elNome) elNome.textContent = usuario.nome || usuario.username || 'Gestor';
            }

            inicializarDatasFormularioPix();
            carregarClientes();
        });
