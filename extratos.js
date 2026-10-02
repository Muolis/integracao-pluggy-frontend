/**
 * EXTRATOS.JS - Lógica de Controle Frontend
 * MC Securitizadora Open Finance
 */

const parametrosUrl = new URLSearchParams(window.location.search);
        const itemId = parametrosUrl.get('item');
        const clienteId = parametrosUrl.get('cliente');

        const statusBox = document.getElementById('status-box');
        const bannerUpdating = document.getElementById('banner-updating');
        const cardsResumo = document.getElementById('cards-resumo');
        const secaoIdentidade = document.getElementById('secao-identidade');
        const secaoContas = document.getElementById('secao-contas');
        const secaoExtrato = document.getElementById('secao-extrato');
        const secaoExtras = document.getElementById('secao-extras');

        // Estado global de dados em memória
        let DADOS_OF = null;
        let FILTRO_TIPO_ATUAL = 'TODOS'; // 'TODOS', 'ENTRADA', 'SAIDA'

        if (clienteId) {
            document.getElementById('header-nome-cliente').textContent = MC_CONFIG.escapeHtml(clienteId);
        }

        async function forcarSincronizacaoExtratoTelaCheia() {
            if (!itemId) return;
            const btnSync = document.getElementById('btn-sync-extrato');
            if (btnSync) {
                btnSync.disabled = true;
                btnSync.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Sincronizando...`;
            }
            try {
                const res = await MC_CONFIG.authFetch(`/api/openfinance/completo/${itemId}?sync=true`);
                const data = await res.json();
                if (data.sucesso) {
                    MC_CONFIG.showToast("Sincronização com o banco solicitada com sucesso!", "success");
                    renderizarTelaCompleta(data);
                } else {
                    MC_CONFIG.showToast(data.erro || "Não foi possível sincronizar agora.", "warning");
                }
            } catch (e) {
                MC_CONFIG.showToast("Erro ao conectar ao servidor de sincronização.", "error");
            } finally {
                if (btnSync) {
                    btnSync.disabled = false;
                    btnSync.innerHTML = `<i class="fa-solid fa-rotate"></i> Sincronizar com Banco`;
                }
            }
        }

        async function buscarDados(silencioso = false) {
            if (!itemId) {
                mostrarErro("Nenhum código de conexão (Item ID) foi fornecido na URL.");
                return;
            }

            if (!silencioso) {
                statusBox.style.display = 'flex';
                statusBox.className = 'bg-blue-50 border border-blue-200 text-[#010157] text-xs font-semibold p-4 rounded-xl flex items-center justify-center gap-2';
                statusBox.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-[#0985ff]"></i> Extraindo informações completas do Open Finance (Extratos, Entradas, Saídas, Identidade, Contas)...';
            }

            try {
                // Chama a rota consolidada de extração 100% completa
                const resposta = await MC_CONFIG.authFetch(`/api/openfinance/completo/${itemId}`);
                if (!resposta.ok) {
                    throw new Error('Falha ao consultar API de Open Finance.');
                }

                const dados = await resposta.json();
                DADOS_OF = dados;
                renderizarTelaCompleta(dados);

            } catch (erro) {
                console.error('[ERRO BUSCAR DADOS OF]:', erro);
                mostrarErro(erro.message || "Erro ao consultar dados completos do Open Finance.");
            }
        }

        function renderizarTelaCompleta(dados) {
            statusBox.style.display = 'none';
            const item = dados.item || {};
            const ident = dados.identidade || {};
            const contas = dados.contas || [];
            const transacoes = dados.transacoes || [];
            const metricas = dados.metricas || {};

            // 1. Header & Status
            const bancoNome = item.connector?.name || 'Instituição Bancária';
            document.getElementById('header-banco-nome').textContent = bancoNome;
            
            const nomeCliente = ident.fullName || ident.document || clienteId || 'Cliente Open Finance';
            document.getElementById('header-nome-cliente').textContent = nomeCliente;

            // Formatação correta da data real de conexão
            const dataConexaoReal = item.createdAt ? MC_CONFIG.formatDate(item.createdAt) : '---';
            document.getElementById('header-data-conexao').textContent = dataConexaoReal;

            const badgeStatus = document.getElementById('badge-status-item');
            if (item.status === 'UPDATING') {
                badgeStatus.className = 'text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 animate-pulse';
                badgeStatus.textContent = 'Sincronizando';
                bannerUpdating.classList.remove('hidden');
            } else if (item.status === 'LOGIN_ERROR') {
                badgeStatus.className = 'text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800';
                badgeStatus.textContent = 'Requer Nova Senha';
                bannerUpdating.classList.add('hidden');
            } else {
                badgeStatus.className = 'text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800';
                badgeStatus.textContent = 'Conectado';
                bannerUpdating.classList.add('hidden');
            }

            // 2. Cards de Resumo Financeiro
            cardsResumo.classList.remove('hidden');
            document.getElementById('card-saldo-total').textContent = MC_CONFIG.formatMoney(metricas.saldo_total_contas || 0);
            document.getElementById('card-qtd-contas').textContent = `${metricas.quantidade_contas || 0} conta(s) conectada(s)`;
            
            document.getElementById('card-total-entradas').textContent = MC_CONFIG.formatMoney(metricas.total_entradas || 0);
            document.getElementById('card-qtd-entradas').textContent = `${metricas.quantidade_entradas || 0} créditos recebidos`;
            
            document.getElementById('card-total-saidas').textContent = MC_CONFIG.formatMoney(metricas.total_saidas || 0);
            document.getElementById('card-qtd-saidas').textContent = `${metricas.quantidade_saidas || 0} débitos realizados`;

            const saldoLiq = metricas.saldo_liquido || 0;
            const elSaldoLiq = document.getElementById('card-saldo-liquido');
            elSaldoLiq.textContent = MC_CONFIG.formatMoney(saldoLiq);
            elSaldoLiq.className = `text-lg md:text-xl font-black ${saldoLiq >= 0 ? 'text-[#0985ff]' : 'text-rose-600'}`;

            document.getElementById('card-total-tx').textContent = String(metricas.quantidade_transacoes || 0);

            // 3. Ficha Cadastral / Identidade
            secaoIdentidade.classList.remove('hidden');
            document.getElementById('id-nome').textContent = ident.fullName || 'Não informado';
            document.getElementById('id-documento').textContent = ident.document || 'Não informado';
            
            let outrosDocsTexto = 'Nenhum outro doc';
            if (ident.otherDocuments && ident.otherDocuments.length > 0) {
                outrosDocsTexto = ident.otherDocuments.map(d => `${d.type || 'Doc'}: ${d.number || ''}`).join(', ');
            }
            document.getElementById('id-outros-docs').textContent = outrosDocsTexto;

            let dtNasc = '---';
            if (ident.birthDate) {
                dtNasc = MC_CONFIG.formatDate(ident.birthDate).split(' às ')[0];
            }
            document.getElementById('id-nascimento').textContent = dtNasc;

            const ocupacao = ident.jobTitle || (ident.qualifications?.occupationDescription) || 'Não especificada';
            document.getElementById('id-ocupacao').textContent = ocupacao;

            // Renda Declarada
            const rendaObj = ident.qualifications?.informedIncome;
            const badgeRenda = document.getElementById('badge-renda-declarada');
            if (rendaObj && rendaObj.amount) {
                badgeRenda.classList.remove('hidden');
                const freq = rendaObj.frequency ? ` (${rendaObj.frequency.toLowerCase()})` : '';
                document.getElementById('val-renda-declarada').textContent = `${MC_CONFIG.formatMoney(rendaObj.amount)}${freq}`;
            } else {
                badgeRenda.classList.add('hidden');
            }

            // Telefones
            const telefones = (ident.phoneNumbers || []).map(p => p.value || `${p.areaCode || ''} ${p.number || ''}`).filter(Boolean);
            document.getElementById('id-telefones').textContent = telefones.join(', ') || 'Nenhum telefone registrado';

            // Emails
            const emails = (ident.emails || []).map(e => e.value).filter(Boolean);
            document.getElementById('id-emails').textContent = emails.join(', ') || 'Nenhum e-mail registrado';

            // Relacionamento Bancário
            let relac = '---';
            if (ident.financialRelationships?.startDate) {
                relac = `Cliente desde ${MC_CONFIG.formatDate(ident.financialRelationships.startDate).split(' às ')[0]}`;
            }
            document.getElementById('id-relacionamento').textContent = relac;

            // Endereço
            let enderecoCompleto = 'Não informado';
            if (ident.addresses && ident.addresses.length > 0) {
                const adr = ident.addresses[0];
                enderecoCompleto = [
                    adr.primaryAddress || adr.fullAddress,
                    adr.district,
                    adr.city,
                    adr.state,
                    adr.postalCode ? `CEP: ${adr.postalCode}` : null
                ].filter(Boolean).join(' - ');
            }
            document.getElementById('id-endereco').textContent = enderecoCompleto;

            // Filiação
            if (ident.relations && ident.relations.length > 0) {
                document.getElementById('div-filiacao').classList.remove('hidden');
                document.getElementById('id-filiacao').textContent = ident.relations.map(r => `${r.name} (${r.type || 'Parente'})`).join(' | ');
            }

            // 4. Seção de Contas Conectadas
            secaoContas.classList.remove('hidden');
            const gridContas = document.getElementById('grid-contas-cards');
            const selectConta = document.getElementById('select-conta-filtro');
            gridContas.innerHTML = '';
            selectConta.innerHTML = '<option value="">Todas as Contas</option>';

            contas.forEach(c => {
                const cardC = document.createElement('div');
                cardC.className = 'p-5 bg-slate-50 rounded-2xl border border-slate-200/80 shadow-2xs space-y-2';
                const subTipoFormatado = (c.subtype || c.type || 'Conta').toUpperCase();
                const saldoContaFormatado = MC_CONFIG.formatMoney(c.balance || 0);

                cardC.innerHTML = `
                    <div class="flex justify-between items-start gap-2">
                        <div>
                            <span class="text-[10px] font-bold uppercase tracking-wider text-[#0985ff] bg-blue-50 px-2 py-0.5 rounded-md border border-blue-100">
                                ${MC_CONFIG.escapeHtml(subTipoFormatado)}
                            </span>
                            <h3 class="text-xs font-bold text-[#010157] mt-1 truncate">${MC_CONFIG.escapeHtml(c.name || 'Conta')}</h3>
                            <p class="text-[11px] text-slate-500 font-mono mt-0.5">
                                Ag: ${MC_CONFIG.escapeHtml(c.agency || '---')} | C/C: ${MC_CONFIG.escapeHtml(c.number || '---')}
                            </p>
                        </div>
                        <div class="text-right">
                            <span class="text-[9px] uppercase font-bold text-slate-400 block">Saldo</span>
                            <strong class="text-base font-extrabold text-slate-800">${saldoContaFormatado}</strong>
                        </div>
                    </div>
                    <div class="pt-2 border-t border-slate-200/60 flex justify-between items-center text-[10px] text-slate-500">
                        <span>${c.total_transacoes || 0} lançamentos</span>
                        <span class="font-bold text-[#0985ff]">${c.currencyCode || 'BRL'}</span>
                    </div>
                `;
                gridContas.appendChild(cardC);

                // Preenche select de filtro
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.textContent = `${c.name || 'Conta'} (${c.number || '---'})`;
                selectConta.appendChild(opt);
            });

            // 5. Seção de Extrato de Transações
            secaoExtrato.classList.remove('hidden');
            document.getElementById('cont-filtro-todos').textContent = String(transacoes.length);
            document.getElementById('cont-filtro-entradas').textContent = String(metricas.quantidade_entradas || 0);
            document.getElementById('cont-filtro-saidas').textContent = String(metricas.quantidade_saidas || 0);

            renderizarTabelaTransacoes();

            // 6. Investimentos / Extras
            const invs = dados.investimentos || [];
            const loans = dados.emprestimos || [];
            if (invs.length > 0 || loans.length > 0) {
                secaoExtras.classList.remove('hidden');
                let extrasHtml = '';
                if (invs.length > 0) {
                    extrasHtml += `<h4 class="font-bold text-slate-700 mb-2">Investimentos (${invs.length})</h4><ul class="list-disc pl-5 space-y-1 mb-4">`;
                    invs.forEach(iv => {
                        extrasHtml += `<li><strong>${MC_CONFIG.escapeHtml(iv.name || 'Ativo')}</strong> - Saldo: ${MC_CONFIG.formatMoney(iv.balance || 0)} (${iv.type || ''})</li>`;
                    });
                    extrasHtml += `</ul>`;
                }
                if (loans.length > 0) {
                    extrasHtml += `<h4 class="font-bold text-slate-700 mb-2">Operações de Empréstimo / Financiamento (${loans.length})</h4><ul class="list-disc pl-5 space-y-1">`;
                    loans.forEach(ln => {
                        extrasHtml += `<li>Contrato <strong>${ln.contractNumber || ''}</strong> - Valor Contratado: ${MC_CONFIG.formatMoney(ln.contractAmount || 0)} | Saldo Devedor: ${MC_CONFIG.formatMoney(ln.totalDebt || 0)}</li>`;
                    });
                    extrasHtml += `</ul>`;
                }
                document.getElementById('conteudo-extras').innerHTML = extrasHtml;
            } else {
                secaoExtras.classList.add('hidden');
            }
        }

        function filtrarTipoTransacao(tipo) {
            FILTRO_TIPO_ATUAL = tipo;
            const btnTodos = document.getElementById('btn-filtro-todos');
            const btnEntradas = document.getElementById('btn-filtro-entradas');
            const btnSaidas = document.getElementById('btn-filtro-saidas');

            btnTodos.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition cursor-pointer';
            btnEntradas.className = 'px-3 py-1.5 rounded-lg text-emerald-700 hover:text-emerald-900 transition cursor-pointer flex items-center gap-1';
            btnSaidas.className = 'px-3 py-1.5 rounded-lg text-rose-700 hover:text-rose-900 transition cursor-pointer flex items-center gap-1';

            if (tipo === 'TODOS') {
                btnTodos.className = 'px-3 py-1.5 rounded-lg bg-[#010157] text-white shadow-2xs transition cursor-pointer';
            } else if (tipo === 'ENTRADA') {
                btnEntradas.className = 'px-3 py-1.5 rounded-lg bg-emerald-600 text-white shadow-2xs transition cursor-pointer flex items-center gap-1';
            } else if (tipo === 'SAIDA') {
                btnSaidas.className = 'px-3 py-1.5 rounded-lg bg-rose-600 text-white shadow-2xs transition cursor-pointer flex items-center gap-1';
            }

            renderizarTabelaTransacoes();
        }

        function filtrarTransacoesTexto() {
            renderizarTabelaTransacoes();
        }

        function renderizarTabelaTransacoes() {
            if (!DADOS_OF || !DADOS_OF.transacoes) return;

            const tbody = document.getElementById('tabela-transacoes-corpo');
            const textoBusca = (document.getElementById('input-busca-tx').value || '').trim().toLowerCase();
            const contaIdFiltro = document.getElementById('select-conta-filtro').value;

            let lista = DADOS_OF.transacoes;

            // Filtro por tipo
            if (FILTRO_TIPO_ATUAL === 'ENTRADA') {
                lista = lista.filter(t => t.type === 'CREDIT' || t.is_entrada);
            } else if (FILTRO_TIPO_ATUAL === 'SAIDA') {
                lista = lista.filter(t => t.type === 'DEBIT' || t.is_saida);
            }

            // Filtro por conta
            if (contaIdFiltro) {
                lista = lista.filter(t => t.conta_id === contaIdFiltro);
            }

            // Filtro por texto
            if (textoBusca) {
                lista = lista.filter(t => {
                    const desc = (t.description || '').toLowerCase();
                    const descRaw = (t.descriptionRaw || '').toLowerCase();
                    const cat = (t.category || '').toLowerCase();
                    const val = String(t.amount || '');
                    const payerName = (t.paymentData?.payer?.name || '').toLowerCase();
                    const receiverName = (t.paymentData?.receiver?.name || '').toLowerCase();
                    return desc.includes(textoBusca) || 
                           descRaw.includes(textoBusca) || 
                           cat.includes(textoBusca) || 
                           val.includes(textoBusca) ||
                           payerName.includes(textoBusca) ||
                           receiverName.includes(textoBusca);
                });
            }

            document.getElementById('label-contagem-tabela').textContent = `Exibindo ${lista.length} de ${DADOS_OF.transacoes.length} movimentações`;

            if (lista.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="py-10 text-center text-slate-400">
                            <i class="fa-solid fa-filter text-2xl text-slate-300 block mb-2"></i>
                            Nenhuma movimentação corresponde aos filtros selecionados.
                        </td>
                    </tr>
                `;
                return;
            }

            let htmlRows = '';
            lista.forEach(tx => {
                const isEntrada = tx.type === 'CREDIT' || tx.is_entrada;
                const corValor = isEntrada ? 'text-emerald-600 font-extrabold' : 'text-rose-600 font-bold';
                const sinal = isEntrada ? '+ ' : '- ';
                const badgeTipo = isEntrada 
                    ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">ENTRADA</span>' 
                    : '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">SAÍDA</span>';

                const dataFormatada = tx.date ? MC_CONFIG.formatDate(tx.date) : '---';
                const desc = MC_CONFIG.escapeHtml(tx.description || tx.descriptionRaw || 'Transação');
                const cat = MC_CONFIG.escapeHtml(tx.category || 'Outros');
                const contaNome = MC_CONFIG.escapeHtml(tx.conta_nome || 'Conta');
                const contaNum = MC_CONFIG.escapeHtml(tx.conta_numero || '');
                const valorFormatado = MC_CONFIG.formatMoney(Math.abs(tx.amount || 0));

                // Detalhe de pagador / recebedor se houver
                let contraparte = '---';
                if (tx.paymentData) {
                    if (isEntrada && tx.paymentData.payer?.name) {
                        contraparte = `De: ${MC_CONFIG.escapeHtml(tx.paymentData.payer.name)}`;
                    } else if (!isEntrada && tx.paymentData.receiver?.name) {
                        contraparte = `Para: ${MC_CONFIG.escapeHtml(tx.paymentData.receiver.name)}`;
                    } else if (tx.paymentData.paymentMethod) {
                        contraparte = `Via: ${MC_CONFIG.escapeHtml(tx.paymentData.paymentMethod)}`;
                    }
                }

                htmlRows += `
                    <tr class="hover:bg-slate-50/80 transition group">
                        <td class="py-3 px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                            ${dataFormatada}
                        </td>
                        <td class="py-3 px-4 text-slate-800 font-medium">
                            <div class="flex items-center gap-2">
                                ${badgeTipo}
                                <span class="truncate max-w-xs md:max-w-sm" title="${desc}">${desc}</span>
                            </div>
                        </td>
                        <td class="py-3 px-4 text-slate-600">
                            <span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md text-[10px] font-medium border border-slate-200/60">
                                ${cat}
                            </span>
                        </td>
                        <td class="py-3 px-4 text-slate-500 text-[11px]">
                            ${contaNome} <span class="font-mono text-slate-400">(${contaNum})</span>
                        </td>
                        <td class="py-3 px-4 text-slate-500 text-[11px] truncate max-w-xs">
                            ${contraparte}
                        </td>
                        <td class="py-3 px-4 text-right font-mono text-xs whitespace-nowrap ${corValor}">
                            ${sinal}${valorFormatado}
                        </td>
                    </tr>
                `;
            });

            tbody.innerHTML = htmlRows;
        }

        function exportarCSVCompleto() {
            if (!DADOS_OF || !DADOS_OF.transacoes || DADOS_OF.transacoes.length === 0) {
                MC_CONFIG.showToast("Nenhuma transação disponível para exportação.", "warning");
                return;
            }

            const nomeCliente = (DADOS_OF.identidade?.fullName || clienteId || 'cliente').replace(/[^a-zA-Z0-9]/g, '_');
            const dataHoje = new Date().toISOString().slice(0, 10);
            const nomeArquivo = `extrato_openfinance_${nomeCliente}_${dataHoje}.csv`;

            // Cabeçalho CSV
            let csv = '\uFEFF'; // UTF-8 BOM para abrir com acentos perfeitos no Microsoft Excel
            csv += 'Data;Tipo;Descricao;Categoria;Conta;Numero Conta;Contraparte;Valor (R$)\n';

            DADOS_OF.transacoes.forEach(t => {
                const dataFmt = t.date ? MC_CONFIG.formatDate(t.date).replace(';', ' ') : '';
                const tipo = t.type === 'CREDIT' ? 'ENTRADA' : 'SAIDA';
                const desc = (t.description || t.descriptionRaw || '').replace(/;/g, ' ');
                const cat = (t.category || '').replace(/;/g, ' ');
                const conta = (t.conta_nome || '').replace(/;/g, ' ');
                const cnum = (t.conta_numero || '').replace(/;/g, ' ');
                
                let contraparte = '';
                if (t.paymentData?.payer?.name) contraparte = t.paymentData.payer.name;
                else if (t.paymentData?.receiver?.name) contraparte = t.paymentData.receiver.name;
                contraparte = contraparte.replace(/;/g, ' ');

                const valor = (t.amount || 0).toFixed(2).replace('.', ',');

                csv += `"${dataFmt}";"${tipo}";"${desc}";"${cat}";"${conta}";"${cnum}";"${contraparte}";"${valor}"\n`;
            });

            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.setAttribute('href', url);
            link.setAttribute('download', nomeArquivo);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            MC_CONFIG.showToast("Extrato exportado em formato CSV com sucesso!", "success");
        }

        function mostrarErro(mensagem) {
            statusBox.className = 'bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold p-4 rounded-xl flex items-center justify-center gap-2';
            statusBox.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${MC_CONFIG.escapeHtml(mensagem)}`;
        }

        window.onload = () => {
            buscarDados();
        };
