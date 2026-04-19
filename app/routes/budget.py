from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from app.models import Orcamento, Categoria, Estabelecimento
from datetime import datetime

bp = Blueprint('budget', __name__)

@bp.route('/')
def index():
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month
    
    orcamentos = Orcamento.query.filter_by(ano=ano_atual, mes=mes_atual).all()
    categorias = Categoria.query.all()
    
    return render_template('budget/index.html', 
                           orcamentos=orcamentos, 
                           categorias=categorias, 
                           ano=ano_atual, 
                           mes=mes_atual)

@bp.route('/add', methods=['POST'])
def add():
    ano = request.form.get('ano', type=int)
    mes = request.form.get('mes', type=int)
    categoria_id = request.form.get('categoria_id') or None
    valor_previsto = request.form.get('valor_previsto', type=float)
    
    if ano and mes and valor_previsto and categoria_id:
        # Checar se ja existe p/ categoria e periodo
        existe = Orcamento.query.filter_by(ano=ano, mes=mes, categoria_id=categoria_id).first()
        if existe:
            existe.valor_previsto = valor_previsto
            flash('Orçamento atualizado para a categoria.', 'success')
        else:
            novo = Orcamento(ano=ano, mes=mes, categoria_id=categoria_id, valor_previsto=valor_previsto)
            db.session.add(novo)
            flash('Orçamento registrado.', 'success')
            
        db.session.commit()
    else:
        flash('Preencha os campos obrigatórios!', 'danger')
        
    return redirect(url_for('budget.index'))

