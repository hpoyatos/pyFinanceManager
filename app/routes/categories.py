from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Categoria

bp = Blueprint('categories', __name__)

@bp.route('/')
def index():
    categorias = Categoria.query.all()
    return render_template('categories/index.html', categorias=categorias)

@bp.route('/add_categoria', methods=['POST'])
def add_categoria():
    nome = request.form.get('nome')
    tipo = request.form.get('tipo')
    parent_id = request.form.get('parent_id') or None
    cor = request.form.get('cor') or '#95a5a6'
    icone = request.form.get('icone') or 'fa-solid fa-tag'
    
    if nome and tipo:
        nova_cat = Categoria(nome=nome, tipo=tipo, parent_id=parent_id, cor=cor, icone=icone)
        db.session.add(nova_cat)
        db.session.commit()
        flash('Categoria adicionada!', 'success')
    else:
        flash('Campos obrigatórios não preenchidos.', 'danger')
    return redirect(url_for('categories.index'))

@bp.route('/edit_categoria/<int:id>', methods=['GET', 'POST'])
def edit_categoria(id):
    cat = Categoria.query.get_or_404(id)
    if request.method == 'POST':
        cat.nome = request.form.get('nome')
        cat.tipo = request.form.get('tipo')
        cat.cor = request.form.get('cor') or '#95a5a6'
        cat.icone = request.form.get('icone') or 'fa-solid fa-tag'
        cat.parent_id = request.form.get('parent_id') or None
        db.session.commit()
        flash('Categoria atualizada.', 'success')
        return redirect(url_for('categories.index'))
        
    categorias = Categoria.query.filter(Categoria.id != id).all()
    return render_template('categories/edit_categoria.html', cat=cat, categorias=categorias)

@bp.route('/<int:id>/transactions/<periodo>')
def transactions_detail(id, periodo):
    from app.models import Transacao, Estabelecimento
    
    ano, mes = map(int, periodo.split('-'))
    
    if id == 0:
        # "Outros" - Transações sem categoria definida (nem direta nem via estabelecimento)
        transacoes = Transacao.query.filter(
            Transacao.tipo == 'despesa',
            db.extract('month', Transacao.data) == mes,
            db.extract('year', Transacao.data) == ano,
            Transacao.categoria_id == None
        ).all()
        
        # Filtro adicional manual para garantir que o estabelecimento também não tenha categoria
        transacoes = [t for t in transacoes if not (t.estabelecimento and t.estabelecimento.categoria_id)]
        cat = type('Category', (), {'nome': 'Outros', 'cor': '#95a5a6', 'icone': 'fa-solid fa-layer-group', 'id': 0})
    else:
        cat = Categoria.query.get_or_404(id)
        # Buscar todas as subcategorias
        cat_ids = [c.id for c in cat.subcategorias] + [cat.id]
        
        # Transações dessa categoria ou de suas subcategorias
        transacoes = Transacao.query.filter(
            Transacao.tipo == 'despesa',
            db.extract('month', Transacao.data) == mes,
            db.extract('year', Transacao.data) == ano
        ).all()
        
        # Filtrar manualmente para considerar herança de estabelecimento
        def matches_cat(t):
            t_cat_id = t.categoria_id
            if not t_cat_id and t.estabelecimento:
                t_cat_id = t.estabelecimento.categoria_id
            return t_cat_id in cat_ids
            
        transacoes = [t for t in transacoes if matches_cat(t)]

    # Ordenar por data desc
    transacoes.sort(key=lambda x: x.data, reverse=True)
    
    return render_template('categories/transactions.html', cat=cat, transacoes=transacoes, periodo=periodo)

