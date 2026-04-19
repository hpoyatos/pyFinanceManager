from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from io import BytesIO
from app import db
from app.models import Transacao, Conta, Categoria, Estabelecimento, TransacaoAnexo
from app.utils.document_parser import identify_document
from datetime import datetime

bp = Blueprint('transactions', __name__)

@bp.route('/')
def index():
    conta_id = request.args.get('conta_id', type=int)
    page = request.args.get('page', 1, type=int)
    
    selected_conta = None
    transacoes_pagination = None
    
    if conta_id:
        selected_conta = Conta.query.get_or_404(conta_id)
        transacoes_pagination = Transacao.query.filter_by(conta_id=conta_id)\
            .order_by(Transacao.data.desc())\
            .paginate(page=page, per_page=30, error_out=False)
            
    contas = Conta.query.all()
    categorias = Categoria.query.all()
    estabelecimentos = Estabelecimento.query.all()
    
    return render_template('transactions/index.html', 
                           transacoes_pagination=transacoes_pagination, 
                           selected_conta=selected_conta,
                           contas=contas, 
                           categorias=categorias,
                           estabelecimentos=estabelecimentos)

@bp.route('/add', methods=['POST'])
def add():
    conta_id = request.form.get('conta_id')
    tipo = request.form.get('tipo')
    data_str = request.form.get('data')
    valor = request.form.get('valor')
    descricao = request.form.get('descricao')
    estabelecimento_id = request.form.get('estabelecimento_id') or None
    categoria_id = request.form.get('categoria_id') or None
    is_previsao = 'is_previsao' in request.form
    fatura_periodo = request.form.get('fatura_periodo') or None
    observacoes = request.form.get('observacoes')
    
    
    anexo_files = request.files.getlist('anexos')
    
    
    if conta_id and tipo and data_str and valor:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        
        # Se n for passado categoria manualmente, mas tiver estabelecimento, puxar a do estabelecimento
        if estabelecimento_id and not categoria_id:
            estab = Estabelecimento.query.get(estabelecimento_id)
            if estab and estab.categoria_id:
                categoria_id = estab.categoria_id
                
        if tipo == 'transferencia':
            conta_destino_id = request.form.get('conta_destino_id')
            if not conta_destino_id:
                flash('Conta de destino obrigatória para transferências', 'danger')
                return redirect(url_for('transactions.index'))
                
            # Cria a Saída
            t_saida = Transacao(
                conta_id=conta_id, tipo='transferencia_saida', data=data, valor=float(valor),
                descricao=descricao or 'Transferência Enviada', estabelecimento_id=estabelecimento_id,
                categoria_id=categoria_id, conciliado=True, fatura_periodo=fatura_periodo,
                observacoes=observacoes
            )
            db.session.add(t_saida)
            
            # Cria a Entrada
            t_entrada = Transacao(
                conta_id=conta_destino_id, tipo='transferencia_entrada', data=data, valor=float(valor),
                descricao=descricao or 'Transferência Recebida', estabelecimento_id=estabelecimento_id,
                categoria_id=categoria_id, conciliado=True, fatura_periodo=fatura_periodo,
                observacoes=observacoes
            )
            db.session.add(t_entrada)
        else:
            nova_transacao = Transacao(
                conta_id=conta_id,
                tipo=tipo,
                data=data,
                valor=float(valor),
                descricao=descricao,
                estabelecimento_id=estabelecimento_id,
                categoria_id=categoria_id,
                is_previsao=is_previsao,
                conciliado=False, # Manuais n sao automaticamente conciliaes ate OFX virem
                anexo=anexo_data,
                anexo_filename=anexo_filename,
                fatura_periodo=fatura_periodo
            )
            db.session.add(nova_transacao)
            
        db.session.commit()
        flash('Lançamento adicionado!', 'success')
    else:
        flash('Preencha os campos obrigatórios!', 'danger')
        
    return redirect(url_for('transactions.index'))

@bp.route('/conciliar/<int:id>')
def conciliar_manual(id):
    transacao = Transacao.query.get_or_404(id)
    transacao.conciliado = not transacao.conciliado
    db.session.commit()
    return redirect(url_for('transactions.index'))

@bp.route('/delete/<int:id>')
def delete(id):
    transacao = Transacao.query.get_or_404(id)
    db.session.delete(transacao)
    db.session.commit()
    flash('Transação removida.', 'success')
    return redirect(url_for('transactions.index'))

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    transacao = Transacao.query.get_or_404(id)
    if request.method == 'POST':
        transacao.conta_id = request.form.get('conta_id')
        transacao.tipo = request.form.get('tipo')
        transacao.data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()
        transacao.valor = request.form.get('valor')
        transacao.descricao = request.form.get('descricao')
        transacao.estabelecimento_id = request.form.get('estabelecimento_id') or None
        transacao.categoria_id = request.form.get('categoria_id') or None
        transacao.is_previsao = 'is_previsao' in request.form
        transacao.fatura_periodo = request.form.get('fatura_periodo') or None
        transacao.observacoes = request.form.get('observacoes') or None
        
        # Salvar novos Anexos
        novos_anexos = request.files.getlist('anexos')
        for file in novos_anexos:
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                content = file.read()
                tipo_doc, icone = identify_document(content, filename)
                
                novo_anexo = TransacaoAnexo(
                    transacao_id=transacao.id,
                    anexo=content,
                    filename=filename,
                    tipo_documento=tipo_doc,
                    icone=icone
                )
                db.session.add(novo_anexo)
                
        db.session.commit()
        flash('Transação atualizada.', 'success')
        return redirect(url_for('transactions.index'))
        
    contas = Conta.query.all()
    categorias = Categoria.query.all()
    estabelecimentos = Estabelecimento.query.all()
    return render_template('transactions/edit.html', t=transacao, contas=contas, categorias=categorias, estabelecimentos=estabelecimentos)

from flask import jsonify

@bp.route('/api/quick_add_cat', methods=['POST'])
def quick_add_cat():
    data = request.get_json()
    nome = data.get('nome') if data else request.json.get('nome')
    tipo = data.get('tipo') if data else request.json.get('tipo')
    cor = data.get('cor', '#feca57') if data else '#feca57'
    icone = data.get('icone', 'fa-solid fa-tag') if data else 'fa-solid fa-tag'
    
    if not nome or not tipo:
        return jsonify(success=False)
        
    nova_cat = Categoria(nome=nome, tipo=tipo, cor=cor, icone=icone)
    db.session.add(nova_cat)
    db.session.commit()
    return jsonify(success=True, id=nova_cat.id, nome=nova_cat.nome, cor=nova_cat.cor, icone=nova_cat.icone)

@bp.route('/download_anexo/<int:id>')
def download_anexo(id):
    anexo = TransacaoAnexo.query.get_or_404(id)
    return send_file(
        BytesIO(anexo.anexo),
        as_attachment=True,
        download_name=anexo.filename
    )

@bp.route('/delete_anexo/<int:id>')
def delete_anexo(id):
    anexo = TransacaoAnexo.query.get_or_404(id)
    transacao_id = anexo.transacao_id
    db.session.delete(anexo)
    db.session.commit()
    flash('Anexo removido.', 'success')
    return redirect(url_for('transactions.edit', id=transacao_id))

import calendar
from dateutil.relativedelta import relativedelta

@bp.route('/faturas')
@bp.route('/faturas/<periodo>')
def faturas(periodo=None):
    # helper for o() -> %02d
    def o(m):
        return f"{m:02d}"

    if not periodo:
        # Default to current month/year
        hoje = datetime.now()
        periodo = f"{hoje.year}-{o(hoje.month)}"

    try:
        ano, mes = map(int, periodo.split('-'))
        data_atual = datetime(ano, mes, 1)
    except ValueError:
        flash('Período de fatura inválido. Use ano-mes.', 'danger')
        return redirect(url_for('transactions.faturas'))
        
    prev_date = data_atual - relativedelta(months=1)
    next_date = data_atual + relativedelta(months=1)
    
    prev_periodo = f"{prev_date.year}-{o(prev_date.month)}"
    next_periodo = f"{next_date.year}-{o(next_date.month)}"
    
    # Query transactions that have this particular fatura_periodo and are from type 'cartao'
    transacoes_fatura = Transacao.query.join(Conta).filter(
        Transacao.fatura_periodo == periodo,
        Conta.tipo == 'cartao'
    ).all()
    
    # Agrupar por Conta Bancária
    contas_agrupadas = {}
    for t in transacoes_fatura:
        c_id = t.conta_id
        if c_id not in contas_agrupadas:
            contas_agrupadas[c_id] = {
                'conta': t.conta,
                'transacoes': [],
                'total': 0.0
            }
            
        contas_agrupadas[c_id]['transacoes'].append(t)
        # Se for despesa conta como +, se for receita (estorno/pgto) conta como - pra baixar fatura
        if t.tipo in ['despesa', 'transferencia_saida']:
            contas_agrupadas[c_id]['total'] += t.valor
        elif t.tipo in ['receita', 'transferencia_entrada']:
            if t.tipo == 'transferencia_entrada':
                pass # É um pagamento de fatura ou transf, não abate o "Total Gasto" na visão da fatura
            else:
                # É uma receita comum, avaliamos se é um estorno manual ou reembolso válido
                desc = (t.descricao or "").lower()
                keywords_permitidas = ["estorno", "reembolso", "ajuste credito", "credito de compra"]
                pode_subtrair = any(k in desc for k in keywords_permitidas)
                
                if pode_subtrair:
                    contas_agrupadas[c_id]['total'] -= t.valor

    return render_template('transactions/faturas.html', 
                            periodo=periodo,
                            prev_periodo=prev_periodo,
                            next_periodo=next_periodo,
                            contas_agrupadas=contas_agrupadas)

