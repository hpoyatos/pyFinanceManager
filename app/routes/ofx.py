from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from app.models import Conta, Transacao, EstabelecimentoSinonimo, Estabelecimento
from ofxparse import OfxParser
from datetime import timedelta
import re

bp = Blueprint('ofx', __name__)

@bp.route('/')
def index():
    contas = Conta.query.all()
    return render_template('ofx/index.html', contas=contas)

@bp.route('/upload', methods=['POST'])
def upload():
    conta_id = request.form.get('conta_id')
    fatura_periodo = request.form.get('fatura_periodo') or None
    
    if 'ofx_file' not in request.files:
        flash('Nenhum arquivo enviado.', 'danger')
        return redirect(url_for('ofx.index'))
    
    file = request.files['ofx_file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'danger')
        return redirect(url_for('ofx.index'))
        
    conta = Conta.query.get(conta_id)
    if not conta:
        flash('Conta não encontrada.', 'danger')
        return redirect(url_for('ofx.index'))

    try:
        ofx = OfxParser.parse(file)
    except Exception as e:
        flash(f'Erro ao ler OFX: {str(e)}', 'danger')
        return redirect(url_for('ofx.index'))
        
    registros_importados = 0
    registros_conciliados = 0
    
    for account in ofx.accounts:
        for trans in account.statement.transactions:
            fitid = trans.id
            # Se já importamos este OFX FITID, pular (prevenção de duplicidade absoluta baseada em ID)
            if Transacao.query.filter_by(ofx_fitid=fitid).first():
                continue
                
            valor_original = float(trans.amount)
            if valor_original > 0:
                tipo_trans = 'receita'
                valor_abs = valor_original
            else:
                tipo_trans = 'despesa'
                valor_abs = abs(valor_original)
                    
            data_trans = trans.date.date()
            descricao = trans.memo
            
            # --- OVERRIDE INTELIGENTE PARA TRANSFERÊNCIAS ---
            # Se for classificado como receita ou despesa originalmente, ajusta caso seja quitação de cartão ou transferência
            desc_l = descricao.lower()
            if tipo_trans == 'receita':
                keywords_entrada = ["pagamento recebido", "estorno", "reembolso", "pagto recebido", "transferência recebida", "recebida pelo pix", "pagamento recebido"]
                if any(k in desc_l for k in keywords_entrada):
                    tipo_trans = 'transferencia_entrada'
            elif tipo_trans == 'despesa':
                keywords_saida = ["pagamento fatura", "pagto fatura", "pix transf", "transferencia", "ted ", "doc ", "transferência enviada"]
                if any(k in desc_l for k in keywords_saida):
                    tipo_trans = 'transferencia_saida'
            # ------------------------------------------------
            
            # Limpeza de sufixos de parcelamento padrão de faturas de cartão 
            # (ex: "LOJA - Parcela 2/2", "LOJA - parc 01/10", "LOJA - 1/3")
            descricao_limpa = re.sub(r'\s*-\s*(?:parcela|parc|)\s*\d+/\d+.*$', '', descricao, flags=re.IGNORECASE).strip()
            
            # Buscar sinônimo para categorização (Pular se for transferência)
            est_id = None
            cat_id = None
            
            if not tipo_trans.startswith('transferencia'):
                sinonimos = EstabelecimentoSinonimo.query.all()
                for sin in sinonimos:
                    if sin.nome_alternativo.lower() in descricao_limpa.lower():
                        est_id = sin.estabelecimento_id
                        if sin.estabelecimento.categoria_id:
                            cat_id = sin.estabelecimento.categoria_id
                        break
                        
                if not est_id and descricao_limpa:
                    est_nome = descricao_limpa[:100].strip()
                    estab = Estabelecimento.query.filter_by(nome=est_nome).first()
                    if not estab:
                        estab = Estabelecimento(nome=est_nome, categoria_id=None)
                        db.session.add(estab)
                        db.session.flush()  # to get ID
                    est_id = estab.id
                    
            # CONCILIAÇÃO (5% variância de valor e 5 dias de variância)
            limite_inferior = valor_abs * 0.95
            limite_superior = valor_abs * 1.05
            data_ini = data_trans - timedelta(days=5)
            data_fim = data_trans + timedelta(days=5)
            
            trans_existente = Transacao.query.filter(
                Transacao.conta_id == conta_id,
                Transacao.conciliado == False,
                Transacao.ofx_fitid == None,
                Transacao.tipo == tipo_trans,
                Transacao.data >= data_ini,
                Transacao.data <= data_fim,
                Transacao.valor >= limite_inferior,
                Transacao.valor <= limite_superior
            ).first()
            
            if trans_existente:
                # Atualizar a manual/prevista p/ os dados exatos do OFX e conciliar
                trans_existente.data = data_trans
                trans_existente.valor = valor_abs
                trans_existente.conciliado = True
                trans_existente.ofx_fitid = fitid
                if not trans_existente.estabelecimento_id and est_id:
                    trans_existente.estabelecimento_id = est_id
                if not trans_existente.categoria_id and cat_id:
                    trans_existente.categoria_id = cat_id
                if fatura_periodo:
                    trans_existente.fatura_periodo = fatura_periodo
                registros_conciliados += 1
            else:
                # Novo lançamento
                nova = Transacao(
                    conta_id=conta_id,
                    tipo=tipo_trans,
                    data=data_trans,
                    valor=valor_abs,
                    descricao=descricao,
                    estabelecimento_id=est_id,
                    categoria_id=cat_id,
                    conciliado=True,  # Veio do banco, então já ta conciliado
                    ofx_fitid=fitid,
                    is_previsao=False,
                    fatura_periodo=fatura_periodo
                )
                db.session.add(nova)
                registros_importados += 1
                
    db.session.commit()
    flash(f'OFX Processado! {registros_importados} novos registros e {registros_conciliados} conciliações realizadas.', 'success')
    return redirect(url_for('transactions.index'))

