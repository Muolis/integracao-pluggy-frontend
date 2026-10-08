/**
 * SECURITIZADORA.JS - Lógica de Controle Frontend
 * MC Securitizadora Open Finance
 */

let contasSecuritizadora = [];
        let contaSelecionadaId = null;
        let transacoesCache = [];
        let debounceTimer = null;

        async function carregarResumoSecuritizadora() {
            try {
                const res = await MC_CONFIG.authFetch('/api/securitizadora/resumo');
                if (!res.ok) throw new Error('Falha ao obter dados da Securitizadora');
                
                const dados = await res.json();
                const kpis = dados.kpis || {};
                contasSecuritizadora = dados.contas || [];
                const bloqueio = dados.bloqueio_banco;

                // Atualiza KPIs
                document.getElementById('kpi-saldo').textContent = kpis.saldo_consolidado_formatado || 'R$ 0,00';
                document.getElementById('kpi-entradas').textContent = kpis.total_entradas_formatado || 'R$ 0,00';
                document.getElementById('kpi-saidas').textContent = kpis.total_saidas_formatado || 'R$ 0,00';
                document.getElementById('kpi-contas').textContent = `${contasSecuritizadora.length} ${contasSecuritizadora.length === 1 ? 'Conta Vinculada' : 'Contas Vinculadas'}`;
                document.getElementById('kpi-total-tx').textContent = `${kpis.total_transacoes || 0} movimentações registradas`;

                // Diagnóstico de Bloqueio do Banco (Bradesco Empresas)
                const bannerAlerta = document.getElementById('banner-alerta-banco');
                const badgeStatus = document.getElementById('badge-status-conexao');
                const kpiSaldoSub = document.getElementById('kpi-saldo-sub');

                if (bloqueio && bloqueio.bloqueado) {
                    if (bannerAlerta) {
                        bannerAlerta.classList.remove('hidden');
                        bannerAlerta.innerHTML = `
                            <div class="bg-amber-50 border border-amber-200/90 rounded-2xl p-4 md:p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xs">
                                <div class="flex items-start gap-3.5">
                                    <div class="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center shrink-0 text-lg">
                                        <i class="fa-solid fa-triangle-exclamation"></i>
                                    </div>
                                    <div>
                                        <div class="flex items-center gap-2 flex-wrap">
                                            <h4 class="text-sm font-bold text-amber-900">${MC_CONFIG.escapeHtml(bloqueio.titulo || 'Acesso Bloqueado pelo Banco')}</h4>
                                            <span class="text-[10px] font-bold bg-amber-200 text-amber-900 px-2 py-0.5 rounded-full">Ação Necessária</span>
                                        </div>
                                        <p class="text-xs text-amber-800 mt-1 leading-relaxed">
                                            O Bradesco retornou: <em>"${MC_CONFIG.escapeHtml(bloqueio.mensagem)}"</em>. 
                                            O saldo exibido abaixo refere-se à última sincronização com sucesso em <strong>${bloqueio.data_ultimo_sucesso}</strong>.
                                        </p>
                                    </div>
                                </div>
                                <div class="flex items-center gap-2 shrink-0 w-full md:w-auto">
                                    <button type="button" onclick="reconectarContaSecuritizadora('${bloqueio.item_id}')" class="w-full md:w-auto px-4 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs transition shadow-sm flex items-center justify-center gap-2 cursor-pointer">
                                        <i class="fa-solid fa-key"></i> Reconectar / Atualizar Senha
                                    </button>
                                </div>
                            </div>
                        `;
                    }
                    if (badgeStatus) {
                        badgeStatus.className = "inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-800 border border-amber-200";
                        badgeStatus.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ACESSO BLOQUEADO NO BRADESCO`;
                    }
                    if (kpiSaldoSub) {
                        kpiSaldoSub.className = "mt-2 flex items-center gap-1.5 text-[11px] text-amber-700 font-semibold";
                        kpiSaldoSub.innerHTML = `<i class="fa-solid fa-clock-rotate-left text-xs"></i> Último saldo capturado em ${bloqueio.data_ultimo_sucesso}`;
                    }
                } else {
                    if (bannerAlerta) bannerAlerta.classList.add('hidden');
                    if (badgeStatus) {
                        badgeStatus.className = "inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200";
                        badgeStatus.innerHTML = `<i class="fa-solid fa-circle-check"></i> CONEXÃO ATIVA OPEN FINANCE`;
                    }
                    if (kpiSaldoSub) {
                        kpiSaldoSub.className = "mt-2 flex items-center gap-1.5 text-[11px] text-emerald-600 font-semibold";
                        kpiSaldoSub.innerHTML = `<i class="fa-solid fa-shield-halved text-xs"></i> Saldo atualizado via Open Finance`;
                    }
                }

                // Renderiza Grid de Contas
                renderizarContasSecuritizadora();

                // Seleciona a primeira conta e busca o extrato
                if (contasSecuritizadora.length > 0) {
                    contaSelecionadaId = contasSecuritizadora[0].id;
                    const c = contasSecuritizadora[0];
                    document.getElementById('subtitulo-extrato').innerHTML = `
                        Exibindo movimentações de: <strong class="text-slate-800">${MC_CONFIG.escapeHtml(c.banco)} (Agência ${c.agencia} | Conta ${c.numero})</strong>
                    `;
                    buscarExtratoSecuritizadora();
                } else {
                    document.getElementById('tabela-extrato-corpo').innerHTML = `
                        <tr>
                            <td colspan="5" class="py-12 text-center text-slate-400 text-xs">
                                Nenhuma conta corporativa encontrada vinculada à Securitizadora.
                            </td>
                        </tr>
                    `;
                }

            } catch (err) {
                console.error(err);
                MC_CONFIG.showToast('Erro ao carregar ambiente da Securitizadora: ' + err.message, 'error');
            }
        }

        function renderizarContasSecuritizadora() {
            const grid = document.getElementById('grid-contas-securitizadora');
            if (!contasSecuritizadora.length) {
                grid.innerHTML = `
                    <div class="col-span-full py-8 text-center text-slate-400 text-xs">
                        Nenhuma conta bancária cadastrada. Clique em "Vincular Novo Banco" para adicionar.
                    </div>
                `;
                return;
            }

            grid.innerHTML = contasSecuritizadora.map(c => {
                const isSelected = c.id === contaSelecionadaId;
                const bordaClass = isSelected ? 'border-[#0985ff] ring-2 ring-[#0985ff]/20 bg-blue-50/20' : 'border-slate-200/90 hover:border-slate-300 bg-white';
                
                const badgeConta = c.tem_bloqueio
                    ? `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200" title="Acesso bloqueado na agência do Bradesco">
                           <i class="fa-solid fa-triangle-exclamation text-[9px]"></i> Bloqueada no Banco
                       </span>`
                    : `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                           <i class="fa-solid fa-check text-[9px]"></i> Ativa
                       </span>`;

                return `
                    <div class="rounded-2xl p-5 border ${bordaClass} transition shadow-xs flex flex-col justify-between cursor-pointer" onclick="selecionarContaSecuritizadora('${c.id}')">
                        <div>
                            <div class="flex items-center justify-between mb-4">
                                <div class="flex items-center gap-2.5">
                                    <img src="${c.banco_logo}" alt="${c.banco}" class="w-8 h-8 object-contain rounded-lg border border-slate-100 p-0.5 bg-white shadow-2xs" onerror="this.src='https://cdn.pluggy.ai/assets/connectors/bradesco.svg'">
                                    <div>
                                        <h3 class="text-xs font-bold text-[#010157] leading-tight">${MC_CONFIG.escapeHtml(c.banco)}</h3>
                                        <span class="text-[10px] text-slate-400 uppercase font-semibold">${MC_CONFIG.escapeHtml(c.tipo)}</span>
                                    </div>
                                </div>
                                ${badgeConta}
                            </div>

                            <div class="space-y-1.5 text-xs text-slate-600 mb-4 bg-slate-50 p-3 rounded-xl border border-slate-100">
                                <div class="flex justify-between">
                                    <span class="text-slate-400 text-[11px]">Agência:</span>
                                    <span class="font-mono font-bold text-slate-700">${c.agencia}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-slate-400 text-[11px]">Conta Corrente:</span>
                                    <span class="font-mono font-bold text-slate-700">${c.numero}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-slate-400 text-[11px]">Titular:</span>
                                    <span class="font-bold text-slate-700 text-[11px] truncate max-w-[170px]" title="${c.titular}">${c.titular}</span>
                                </div>
                            </div>
                        </div>

                        <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
                            <div>
                                <span class="text-[10px] text-slate-400 uppercase font-bold block">${c.tem_bloqueio ? 'Último Saldo Coletado' : 'Saldo Disponível'}</span>
                                <strong class="text-base font-black text-[#010157]">${c.saldo_formatado}</strong>
                            </div>
                            <button class="text-xs font-bold ${isSelected ? 'text-[#0985ff]' : 'text-slate-500'} flex items-center gap-1 hover:underline">
                                <span>${isSelected ? 'Selecionada' : 'Ver Extrato'}</span>
                                <i class="fa-solid fa-chevron-right text-[10px]"></i>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function selecionarContaSecuritizadora(accId) {
            contaSelecionadaId = accId;
            renderizarContasSecuritizadora();
            const c = contasSecuritizadora.find(x => x.id === accId);
            if (c) {
                document.getElementById('subtitulo-extrato').innerHTML = `
                    Exibindo movimentações de: <strong class="text-slate-800">${MC_CONFIG.escapeHtml(c.banco)} (Agência ${c.agencia} | Conta ${c.numero})</strong>
                `;
            }
            buscarExtratoSecuritizadora();
        }

        async function buscarExtratoSecuritizadora(mostrarToast = false) {
            const corpo = document.getElementById('tabela-extrato-corpo');
            corpo.innerHTML = `
                <tr>
                    <td colspan="5" class="py-12 text-center text-slate-400 text-xs">
                        <i class="fa-solid fa-circle-notch fa-spin text-xl text-[#0985ff] mb-2 block"></i>
                        Atualizando movimentações do extrato...
                    </td>
                </tr>
            `;

            const tipoFiltro = document.getElementById('filtro-tipo').value;
            const buscaFiltro = document.getElementById('filtro-busca').value;
            const catFiltro = document.getElementById('filtro-categoria').value;

            let url = `/api/securitizadora/extrato?accountId=${contaSelecionadaId || ''}&tipo=${tipoFiltro}&busca=${encodeURIComponent(buscaFiltro)}&categoria=${encodeURIComponent(catFiltro)}`;

            try {
                const res = await MC_CONFIG.authFetch(url);
                if (!res.ok) throw new Error('Falha ao carregar extrato da conta');

                const dados = await res.json();
                transacoesCache = dados.results || [];

                document.getElementById('badge-total-filtrado').textContent = `${dados.total || 0} movimentações`;
                document.getElementById('rodape-totais').innerHTML = `
                    Entradas: <span class="text-emerald-600 font-black mr-3">${dados.total_entradas_formatado}</span>
                    Saídas: <span class="text-slate-800 font-black">${dados.total_saidas_formatado}</span>
                `;

                if (!transacoesCache.length) {
                    corpo.innerHTML = `
                        <tr>
                            <td colspan="5" class="py-12 text-center text-slate-400 text-xs">
                                Nenhuma movimentação encontrada com os filtros selecionados.
                            </td>
                        </tr>
                    `;
                    return;
                }

                corpo.innerHTML = transacoesCache.map(t => {
                    const isCredit = t.tipo === 'CREDIT';
                    const corValor = isCredit ? 'text-emerald-600 font-bold' : 'text-slate-800 font-bold';
                    const badgeTipo = isCredit 
                        ? '<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200"><i class="fa-solid fa-arrow-down text-[9px]"></i> Crédito</span>'
                        : '<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200"><i class="fa-solid fa-arrow-up text-[9px]"></i> Débito</span>';

                    let contraparteHtml = '';
                    if (t.contraparte) {
                        contraparteHtml = `<span class="text-[11px] text-slate-500 block mt-0.5"><i class="fa-regular fa-user text-[10px] text-slate-400 mr-1"></i>${MC_CONFIG.escapeHtml(t.contraparte)} ${t.contraparte_doc ? `(${t.contraparte_doc})` : ''}</span>`;
                    }

                    return `
                        <tr class="border-b border-slate-100 hover:bg-slate-50/80 transition text-xs">
                            <td class="py-3 px-3 sm:px-4 md:px-5 whitespace-nowrap text-slate-600 font-mono text-[11px]">
                                ${t.data}
                            </td>
                            <td class="py-3 px-3 sm:px-4 md:px-5 text-slate-800 font-medium max-w-xs md:max-w-md">
                                <div class="truncate" title="${MC_CONFIG.escapeHtml(t.descricao)}">${MC_CONFIG.escapeHtml(t.descricao)}</div>
                                ${contraparteHtml}
                            </td>
                            <td class="py-3 px-3 sm:px-4 md:px-5 whitespace-nowrap">
                                <span class="bg-blue-50/80 text-[#0985ff] border border-blue-100 px-2 py-0.5 rounded-md text-[10px] font-semibold">
                                    ${MC_CONFIG.escapeHtml(t.categoria)}
                                </span>
                            </td>
                            <td class="py-3 px-3 sm:px-4 md:px-5 text-center whitespace-nowrap">
                                ${badgeTipo}
                            </td>
                            <td class="py-3 px-3 sm:px-4 md:px-5 text-right whitespace-nowrap font-mono text-sm ${corValor}">
                                ${t.valor_formatado}
                            </td>
                        </tr>
                    `;
                }).join('');

                if (mostrarToast) {
                    MC_CONFIG.showToast('Extrato atualizado com sucesso!', 'success');
                }

            } catch (err) {
                console.error(err);
                corpo.innerHTML = `
                    <tr>
                        <td colspan="5" class="py-12 text-center text-rose-500 text-xs">
                            Erro ao consultar extrato: ${MC_CONFIG.escapeHtml(err.message)}
                        </td>
                    </tr>
                `;
            }
        }

        function debounceFiltrar() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                buscarExtratoSecuritizadora();
            }, 300);
        }

        async function sincronizarContasSecuritizadora() {
            const btn = document.getElementById('btn-sync-sec');
            btn.disabled = true;
            btn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin text-[#0985ff]"></i> Sincronizando...`;

            try {
                const res = await MC_CONFIG.authFetch('/api/securitizadora/sincronizar', { method: 'POST' });
                const dados = await res.json();
                if (dados.sucesso) {
                    if (dados.bloqueio_detectado) {
                        MC_CONFIG.showToast('Atenção: ' + (dados.mensagem || 'O banco reportou bloqueio de credenciais na agência.'), 'warning');
                    } else {
                        MC_CONFIG.showToast('Sincronização solicitada com o Bradesco! Atualizando em instantes...', 'success');
                    }
                    setTimeout(() => {
                        carregarResumoSecuritizadora();
                    }, 3000);
                } else {
                    MC_CONFIG.showToast(dados.erro || 'Falha ao sincronizar', 'warning');
                }
            } catch (e) {
                MC_CONFIG.showToast('Erro ao acionar sincronização bancária', 'error');
            } finally {
                setTimeout(() => {
                    btn.disabled = false;
                    btn.innerHTML = `<i class="fa-solid fa-rotate text-[#0985ff]"></i> Sincronizar com Banco`;
                }, 2000);
            }
        }

        async function reconectarContaSecuritizadora(itemId) {
            MC_CONFIG.showToast('Abrindo assistente de reconexão do Bradesco Empresas...', 'info');
            try {
                const res = await MC_CONFIG.authFetch('/api/securitizadora/conectar-token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_id: itemId })
                });
                const dados = await res.json();
                if (!dados.accessToken) throw new Error('Não foi possível obter o token de reconexão corporativa');

                const pluggyConnect = new PluggyConnect({
                    connectToken: dados.accessToken,
                    updateItem: itemId,
                    name: 'Openfinance MC',
                    title: 'Reconectar Bradesco Empresas',
                    onSuccess: async () => {
                        MC_CONFIG.showToast('Credenciais atualizadas com sucesso! Atualizando saldo...', 'success');
                        setTimeout(() => carregarResumoSecuritizadora(), 2500);
                    },
                    onError: (err) => {
                        console.error('Erro ao reconectar conta MC:', err);
                        MC_CONFIG.showToast('A reconexão não foi concluída. Verifique com a agência se a senha foi liberada.', 'warning');
                    }
                });

                pluggyConnect.init();
            } catch (e) {
                console.error(e);
                MC_CONFIG.showToast(e.message || 'Erro ao iniciar reconexão', 'error');
            }
        }

        function abrirConectarNovaContaMC() {
            document.getElementById('modal-conectar-mc').classList.remove('hidden');
        }

        function fecharModalConectarMC() {
            document.getElementById('modal-conectar-mc').classList.add('hidden');
        }

        async function iniciarConexaoPluggyMC() {
            const btn = document.getElementById('btn-iniciar-conectar-mc');
            btn.disabled = true;
            btn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Gerando conexão...`;

            try {
                const res = await MC_CONFIG.authFetch('/api/securitizadora/conectar-token', { method: 'POST' });
                const dados = await res.json();
                if (!dados.accessToken) throw new Error('Não foi possível obter o token de conexão corporativa');

                fecharModalConectarMC();

                const pluggyConnect = new PluggyConnect({
                    connectToken: dados.accessToken,
                    name: 'Openfinance MC',
                    title: 'Openfinance MC - Conta Própria',
                    onSuccess: async (dadosRetorno) => {
                        const itemId = (dadosRetorno && dadosRetorno.item && dadosRetorno.item.id) || (dadosRetorno && dadosRetorno.id);
                        if (itemId) {
                            await MC_CONFIG.authFetch('/salvar-conexao', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    cliente: 'MC MINHACONTA SECURITIZADORA SA',
                                    item_id: itemId,
                                    tipo: 'securitizadora',
                                    status: 'ativo'
                                })
                            });
                        }
                        MC_CONFIG.showToast('Nova conta corporativa conectada com sucesso!', 'success');
                        setTimeout(() => carregarResumoSecuritizadora(), 2000);
                    },
                    onError: (err) => {
                        console.error('Erro ao conectar conta MC:', err);
                        MC_CONFIG.showToast('Conexão não foi finalizada.', 'warning');
                    }
                });

                pluggyConnect.init();

            } catch (e) {
                console.error(e);
                MC_CONFIG.showToast(e.message || 'Erro ao iniciar conexão', 'error');
            } finally {
                btn.disabled = false;
                btn.innerHTML = `<i class="fa-solid fa-link"></i> Abrir Conexão`;
            }
        }

        function exportarExtratoCSV() {
            if (!transacoesCache.length) {
                MC_CONFIG.showToast('Nenhuma movimentação para exportar.', 'info');
                return;
            }

            let csvContent = "Data;Descricao;Contraparte;Documento;Categoria;Tipo;Valor\n";

            transacoesCache.forEach(t => {
                const linha = [
                    `"${t.data}"`,
                    `"${(t.descricao || '').replace(/"/g, '""')}"`,
                    `"${(t.contraparte || '').replace(/"/g, '""')}"`,
                    `"${t.contraparte_doc || ''}"`,
                    `"${t.categoria || ''}"`,
                    `"${t.tipo_label || ''}"`,
                    `"${t.valor}"`
                ].join(";");
                csvContent += linha + "\n";
            });

            // Adiciona BOM UTF-8 (\uFEFF) para garantir abertura correta de acentos no Excel Windows
            const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.setAttribute("href", url);
            link.setAttribute("download", `extrato_securitizadora_mc_${new Date().toISOString().slice(0, 10)}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            MC_CONFIG.showToast('Extrato exportado em CSV com sucesso!', 'success');
        }

        window.onload = () => {
            carregarResumoSecuritizadora();
        };
