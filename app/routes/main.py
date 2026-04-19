from flask import Blueprint, render_template
from app import db
from app.models import Transacao, Orcamento, Categoria, Conta, Estabelecimento
from sqlalchemy import func
from datetime import datetime
from dateutil.relativedelta import relativedelta

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/dashboard/<periodo>')
def index(periodo=None):
    if not periodo:
        now = datetime.now()
        periodo = f"{now.year}-{now.month:02d}"
    
    try:
        ano_atual, mes_atual = map(int, periodo.split('-'))
        data_atual = datetime(ano_atual, mes_atual, 1)
    except ValueError:
        now = datetime.now()
        ano_atual, mes_atual = now.year, now.month
        data_atual = datetime(ano_atual, mes_atual, 1)

    prev_date = data_atual - relativedelta(months=1)
    next_date = data_atual + relativedelta(months=1)
    prev_periodo = f"{prev_date.year}-{prev_date.month:02d}"
    next_periodo = f"{next_date.year}-{next_date.month:02d}"
    
    # Label Formatada
    meses_pt = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    periodo_extenso = f"{meses_pt[mes_atual-1]} / {ano_atual}"

    # Receitas Mes Atual
    receitas_mes = Transacao.query.filter(
        Transacao.tipo == 'receita',
        db.extract('month', Transacao.data) == mes_atual,
        db.extract('year', Transacao.data) == ano_atual
    ).with_entities(func.sum(Transacao.valor)).scalar() or 0.0

    # Despesas Mes Atual
    despesas_mes = Transacao.query.filter(
        Transacao.tipo == 'despesa',
        db.extract('month', Transacao.data) == mes_atual,
        db.extract('year', Transacao.data) == ano_atual
    ).with_entities(func.sum(Transacao.valor)).scalar() or 0.0
    
    # Saldo Previsto Geral (Saldo Inicial + Receitas - Despesas)
    contas = Conta.query.all()
    saldo_inicial_total = sum([c.saldo_inicial for c in contas])
    
    receitas_total = Transacao.query.filter_by(tipo='receita').with_entities(func.sum(Transacao.valor)).scalar() or 0.0
    despesas_total = Transacao.query.filter_by(tipo='despesa').with_entities(func.sum(Transacao.valor)).scalar() or 0.0
    saldo_previsto = saldo_inicial_total + receitas_total - despesas_total
    
    # Despesas por Categoria (Pie Chart) - Mes atual
    from sqlalchemy.orm import joinedload
    transacoes_mes = Transacao.query.options(
        joinedload(Transacao.categoria),
        joinedload(Transacao.estabelecimento).joinedload(Estabelecimento.categoria)
    ).filter(
        Transacao.tipo == 'despesa',
        db.extract('month', Transacao.data) == mes_atual,
        db.extract('year', Transacao.data) == ano_atual
    ).all()
    
    from collections import defaultdict
    cat_agrupada = defaultdict(float)
    cat_cor = {}
    
    for t in transacoes_mes:
        # Tenta categoria direta, senão tenta herdar do estabelecimento
        cat = t.categoria
        if not cat and t.estabelecimento and t.estabelecimento.categoria:
            cat = t.estabelecimento.categoria

        if cat:
            # Agrupar pela categoria pai para o gráfico não ficar fragmentado
            cat_principal = cat.parent if cat.parent else cat
            cat_agrupada[cat_principal.nome] += float(t.valor)
            cat_cor[cat_principal.nome] = cat_principal.cor
        else:
            cat_agrupada['Outros'] += float(t.valor)
            cat_cor['Outros'] = '#95a5a6' # Cinza
            
    cat_labels = list(cat_agrupada.keys())
    cat_values = [cat_agrupada[nome] for nome in cat_labels]
    cat_colors = [cat_cor[nome] for nome in cat_labels]
    
    # Orçamento vs Realizado Mês Atual
    total_orcado = Orcamento.query.filter_by(ano=ano_atual, mes=mes_atual).with_entities(func.sum(Orcamento.valor_previsto)).scalar() or 0.0

    return render_template('dashboard.html', 
                           receitas_mes=receitas_mes, 
                           despesas_mes=despesas_mes, 
                           saldo_previsto=saldo_previsto,
                           cat_labels=cat_labels,
                           cat_values=cat_values,
                           cat_colors=cat_colors,
                           total_orcado=total_orcado,
                           total_realizado=despesas_mes,
                           periodo_extenso=periodo_extenso,
                           prev_periodo=prev_periodo,
                           next_periodo=next_periodo)

