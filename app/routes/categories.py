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

