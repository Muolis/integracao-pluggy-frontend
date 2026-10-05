# -*- coding: utf-8 -*-
"""
====================================================================
GUIA RÁPIDO DE TERMOS TÉCNICOS & NAVEGAÇÃO DO DOSSIÊ (ONE-PAGE PDF)
MC MINHACONTA SECURITIZADORA S/A — OPEN FINANCE & PIX AUTOMÁTICO
====================================================================
Gera um PDF executivo de EXATAMENTE 1 PÁGINA para consulta rápida
da Diretoria, Mesa de Crédito e Comitê de Risco.
"""

import os
import sys
import time
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PDF = os.path.join(BASE_DIR, "Guia_Termos_Tecnicos_Dossie_MC.pdf")
LOGO_PATH = os.path.join(BASE_DIR, "logo-mc-minhaconta.png")


class SinglePageCanvas(canvas.Canvas):
    """Garante layout de página única com rodapé executivo padronizado."""
    def __init__(self, *args, **kwargs):
        super(SinglePageCanvas, self).__init__(*args, **kwargs)

    def showPage(self):
        # Desenha rodapé corporativo
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#010157"))
        self.drawString(32, 22, "MC MINHACONTA SECURITIZADORA S/A")
        
        self.setFont("Helvetica", 7)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(185, 22, "• Guia Executivo de Consulta Rápida • Suporte ao Dossiê Técnico Oficial (5 Págs)")
        self.drawRightString(563, 22, "Página 1 de 1 (One-Page)")
        
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(32, 30, 563, 30)
        self.restoreState()
        super(SinglePageCanvas, self).showPage()


def gerar_pdf_uma_pagina(caminho_saida=OUTPUT_PDF):
    # Dimensões A4: 595 x 842. Margens compactas (32pt laterais, 26pt verticais)
    doc = SimpleDocTemplate(
        caminho_saida,
        pagesize=A4,
        leftMargin=32,
        rightMargin=32,
        topMargin=26,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Cores Corporativas
    c_primary = colors.HexColor("#010157")     # Azul MC Noturno
    c_secondary = colors.HexColor("#0985ff")   # Azul Elétrico
    c_dark = colors.HexColor("#0f172a")        # Ardósia
    c_text = colors.HexColor("#334155")        # Texto
    c_muted = colors.HexColor("#64748b")       # Mutado
    c_border = colors.HexColor("#cbd5e1")      # Bordas
    c_bg_head = colors.HexColor("#010157")     # Cabeçalho Azul
    c_bg_sub = colors.HexColor("#f1f5f9")      # Subtítulos
    c_danger = colors.HexColor("#be123c")      # Alerta

    # Estilos de Texto Ultracompactos e Elegantes
    st_title = ParagraphStyle(
        'OnePageTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=c_primary
    )

    st_sub = ParagraphStyle(
        'OnePageSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=c_secondary
    )

    st_desc = ParagraphStyle(
        'OnePageDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9.5,
        textColor=c_muted
    )

    st_cat = ParagraphStyle(
        'CategoryBanner',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=c_primary
    )

    st_term = ParagraphStyle(
        'TermText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.8,
        leading=8.8,
        textColor=c_primary
    )

    st_def = ParagraphStyle(
        'DefText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.6,
        leading=8.8,
        textColor=c_dark
    )

    st_page = ParagraphStyle(
        'PageRef',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.5,
        leading=8.5,
        alignment=1, # Centralizado
        textColor=colors.HexColor("#047857")
    )

    st_th = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # CABEÇALHO SUPERIOR (Logo + Título + Metadados em Linha Única)
    # =========================================================================
    header_data = []
    col_logo = Paragraph("<b>MC SECURITIZADORA</b>", st_title)
    if os.path.exists(LOGO_PATH):
        try:
            col_logo = Image(LOGO_PATH, width=125, height=35)
        except Exception:
            pass

    col_titulos = [
        Paragraph("GUIA RÁPIDO DE TERMOS TÉCNICOS & NAVEGAÇÃO DO DOSSIÊ", st_title),
        Paragraph("Tradução Executiva de Nomes Técnicos, Cibersegurança e Regras Anti-Calote (Open Finance ITP / VRP)", st_sub),
        Paragraph("Documento de apoio e consulta rápida vinculado ao <b>Dossiê Técnico de Conformidade e Segurança (5 Págs)</b>", st_desc)
    ]

    t_header = Table([[col_logo, col_titulos]], colWidths=[135, 396])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_header)
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=4, spaceAfter=6))

    # =========================================================================
    # TABELA MESTRA DE TERMOS (4 CATEGORIAS INTEGRADAS)
    # =========================================================================
    # Estrutura de Colunas: [Termo Técnico (110pt), Significado Executivo / Impacto no Negócio (360pt), Página no Dossiê (61pt)]
    rows = [
        # Cabeçalho da Tabela
        [Paragraph("Termo Técnico / Sigla", st_th), 
         Paragraph("Significado em Linguagem Simples & Impacto Prático para a MC Securitizadora", st_th), 
         Paragraph("Local no Dossiê", st_th)],

        # CATEGORIA 1: FINANCEIRO & REGRAS ANTI-CALOTE
        [Paragraph("<b>1. CONFIABILIDADE FINANCEIRA & TRAVA ANTI-CALOTE</b>", st_cat), "", ""],
        
        [Paragraph("<b>Trava Operacional</b><br/><code>liberacao_operacional</code>", st_term),
         Paragraph("<b>Regra lógica inviolável no servidor:</b> impede fisicamente que a mesa de crédito transfira o dinheiro do empréstimo antes da 1ª cobrança ser compensada. <b>Garante risco zero de calote imediato</b>.", st_def),
         Paragraph("Páginas 1, 3 e 5<br/>(Seção 3)", st_page)],

        [Paragraph("<b>CONSENT_GRANTED</b><br/>(ou <code>PENDING</code>)", st_term),
         Paragraph("<b>Consentimento Assinado:</b> O cliente autorizou o Pix no app do banco, mas <b>R$ 0,00 caiu na conta da MC</b>. O sistema marca <b>BLOQUEADO</b> e proíbe a liberação de recursos.", st_def),
         Paragraph("Página 3<br/>(Tabela 3.1)", st_page)],

        [Paragraph("<b>SCHEDULED</b><br/>(ou <code>AGENDADO</code>)", st_term),
         Paragraph("<b>Parcelas Futuras Agendadas:</b> Débitos dos meses seguintes registrados na câmara do banco. Classificado como <b>RETIDO</b>, pois é valor futuro e não caixa disponível hoje.", st_def),
         Paragraph("Página 3<br/>(Tabela 3.1)", st_page)],

        [Paragraph("<b>COMPLETED</b><br/>(ou <code>PAYMENT_COMPLETED</code>)", st_term),
         Paragraph("<b>Liquidação Financeira Confirmada:</b> O Pix da taxa de adesão (R$ 0,01) ou 1ª parcela caiu na conta da Securitizadora via SPI do Bacen. <b>Único gatilho que libera o crédito com segurança</b>.", st_def),
         Paragraph("Páginas 3 e 5<br/>(Tabela 3.1 / 7)", st_page)],

        # CATEGORIA 2: AMBIENTES & PROTOCOLOS DE TROUBLESHOOTING
        [Paragraph("<b>2. AMBIENTES DE OPERAÇÃO & CONTINGÊNCIA (TROUBLESHOOTING)</b>", st_cat), "", ""],

        [Paragraph("<b>Sandbox</b> vs.<br/><b>Produção (Live)</b>", st_term),
         Paragraph("<b>Sandbox:</b> Ambiente de simulação segura onde a tecnologia é testada com dados fictícios.<br/><b>Produção (Live):</b> Servidores oficiais em nuvem onde circulam os contratos e dinheiro real dos clientes.", st_def),
         Paragraph("Páginas 1, 4 e 5<br/>(Seção 4 e 6)", st_page)],

        [Paragraph("<b>Timeout Upstream</b><br/>(HTTP 500 / Connection Error)", st_term),
         Paragraph("<b>Lentidão no banco do cliente:</b> Ocorre quando o servidor do banco pagador (ex: Banco BMG) demora mais de 15s para responder. O backend trata sem travar a tela e orienta trocar de banco.", st_def),
         Paragraph("Página 4<br/>(Matriz Seção 5)", st_page)],

        [Paragraph("<b>HTTP 502 / 504</b><br/>(Bad Gateway / Timeout)", st_term),
         Paragraph("<b>Instabilidade transitória de rede:</b> Sobrecarga temporária entre os servidores da Pluggy e as câmaras bancárias. O sistema trata exibindo aviso amigável de espera de 30 segundos.", st_def),
         Paragraph("Página 4<br/>(Matriz Seção 5)", st_page)],

        [Paragraph("<b>Bloqueio nos 40%</b><br/>(Falha de Handshake)", st_term),
         Paragraph("Momento exato da troca de certificados de segurança (mTLS) entre a Pluggy e o banco. Se travar, indica divergência entre credenciais de teste e de produção.", st_def),
         Paragraph("Página 4<br/>(Matriz Seção 5)", st_page)],

        # CATEGORIA 3: OPEN FINANCE & CAPABILITIES BANCÁRIAS
        [Paragraph("<b>3. OPEN FINANCE & CAPACIDADES BANCÁRIAS (VRP / ITP)</b>", st_cat), "", ""],

        [Paragraph("<b>ITP</b> e <b>VRP</b><br/>(Pix Automático)", st_term),
         Paragraph("<b>ITP:</b> Iniciador de Transação de Pagamento (a Pluggy, autorizada pelo Bacen a debitar).<br/><b>VRP:</b> <i>Variable Recurring Payments</i> — Pix Automático com recorrência mensal sem gerar boleto.", st_def),
         Paragraph("Páginas 1, 3 e 5<br/>(Seção 1, 3, 4)", st_page)],

        [Paragraph("<b>supportsSmartTransfers</b><br/>vs <b>PaymentInitiation</b>", st_term),
         Paragraph("<b>Filtragem Estrita de Bancos:</b> <code>supportsPaymentInitiation</code> aceita apenas Pix comum à vista. Nossa ferramenta exige <code>supportsSmartTransfers == True</code>, listando apenas os <b>77 bancos que aceitam Pix Automático</b>.", st_def),
         Paragraph("Páginas 3, 4 e 5<br/>(Seção 4.1 e 7)", st_page)],

        [Paragraph("<b>SPI</b> e <b>CIP</b>", st_term),
         Paragraph("<b>SPI:</b> Sistema de Pagamentos Instantâneos do Banco Central (liquidação em 3s).<br/><b>CIP:</b> Câmara Interbancária de Pagamentos (registra a grade de agendamentos futuros das parcelas).", st_def),
         Paragraph("Página 1 e 3<br/>(Seção 1 e 3.1)", st_page)],

        # CATEGORIA 4: CIBERSEGURANÇA & ARQUITETURA
        [Paragraph("<b>4. CIBERSEGURANÇA & PROTEÇÃO DE DADOS BANCÁRIOS</b>", st_cat), "", ""],

        [Paragraph("<b>BFF</b> (Backend-for-Frontend)<br/>Zero Client Secret", st_term),
         Paragraph("<b>Proteção Absoluta de Senhas:</b> O navegador nunca acessa as chaves da Pluggy ou do Supabase. Toda requisição passa pelo nosso servidor blindado (proxy reverso), impedindo vazamento de credenciais.", st_def),
         Paragraph("Páginas 1, 2 e 5<br/>(Seção 2.1 e 7)", st_page)],

        [Paragraph("<b>PBKDF2</b> e <b>HMAC</b><br/>(Tokens de Sessão)", st_term),
         Paragraph("<b>Criptografia Militar:</b> Senhas dos operadores salvas em hash PBKDF2. Crachás de login assinados com chave criptográfica HMAC-SHA256, com expiração mandatória de 24 horas.", st_def),
         Paragraph("Páginas 2 e 5<br/>(Seção 2.2 e 7)", st_page)],

        [Paragraph("<b>Directory Traversal</b><br/>(Hardening OWASP)", st_term),
         Paragraph("Tentativa de invasão onde alguém digita caminhos como <code>../../.env</code> para roubar código. O sistema bloqueia imediatamente com código de segurança <b>HTTP 403 Forbidden</b>.", st_def),
         Paragraph("Páginas 2 e 4<br/>(Seção 2.3 e 6)", st_page)],

        [Paragraph("<b>Webhook</b> e<br/><b>Idempotência (ACID)</b>", st_term),
         Paragraph("<b>Notificação em Tempo Real:</b> A Pluggy avisa o servidor no segundo em que o cliente paga. A idempotência garante que reenvios de rede nunca criem cobranças ou contratos duplicados no Supabase.", st_def),
         Paragraph("Páginas 2 e 5<br/>(Seção 2.4 e 7)", st_page)],
    ]

    t_master = Table(rows, colWidths=[115, 345, 71])
    t_master.setStyle(TableStyle([
        # Cabeçalho Principal
        ('BACKGROUND', (0,0), (-1,0), c_bg_head),
        ('BOX', (0,0), (-1,-1), 0.6, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.4, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),

        # Banners de Categoria (Span das 3 colunas)
        ('SPAN', (0, 1), (2, 1)),
        ('BACKGROUND', (0, 1), (2, 1), colors.HexColor("#e0f2fe")),
        
        ('SPAN', (0, 6), (2, 6)),
        ('BACKGROUND', (0, 6), (2, 6), colors.HexColor("#e0f2fe")),

        ('SPAN', (0, 11), (2, 11)),
        ('BACKGROUND', (0, 11), (2, 11), colors.HexColor("#e0f2fe")),

        ('SPAN', (0, 15), (2, 15)),
        ('BACKGROUND', (0, 15), (2, 15), colors.HexColor("#e0f2fe")),

        # Cores Alternadas Suaves
        ('BACKGROUND', (0, 2), (-1, 2), colors.white),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0, 4), (-1, 4), colors.white),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor("#f8fafc")),

        ('BACKGROUND', (0, 7), (-1, 7), colors.white),
        ('BACKGROUND', (0, 8), (-1, 8), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0, 9), (-1, 9), colors.white),
        ('BACKGROUND', (0, 10), (-1, 10), colors.HexColor("#f8fafc")),

        ('BACKGROUND', (0, 12), (-1, 12), colors.white),
        ('BACKGROUND', (0, 13), (-1, 13), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0, 14), (-1, 14), colors.white),

        ('BACKGROUND', (0, 16), (-1, 16), colors.white),
        ('BACKGROUND', (0, 17), (-1, 17), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0, 18), (-1, 18), colors.white),
        ('BACKGROUND', (0, 19), (-1, 19), colors.HexColor("#f8fafc")),
    ]))

    story.append(t_master)

    # Constrói o PDF usando SinglePageCanvas
    doc.build(story, canvasmaker=SinglePageCanvas)
    return caminho_saida


if __name__ == "__main__":
    t0 = time.time()
    pdf_saida = gerar_pdf_uma_pagina()
    print(f"[OK] One-Page PDF gerado com sucesso em {round(time.time() - t0, 2)}s!")
    print(f"[CAMINHO]: {pdf_saida}")
    print(f"[TAMANHO]: {os.path.getsize(pdf_saida)} bytes")
