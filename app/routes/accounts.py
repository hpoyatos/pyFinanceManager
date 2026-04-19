from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Instituicao, Conta

bp = Blueprint('accounts', __name__)

@bp.route('/')
def index():
    contas = Conta.query.join(Instituicao).all()
    instituicoes = Instituicao.query.all()
    return render_template('accounts/index.html', contas=contas, instituicoes=instituicoes)

@bp.route('/add_conta', methods=['POST'])
def add_conta():
    nome = request.form.get('nome')
    tipo = request.form.get('tipo')
    instituicao_id = request.form.get('instituicao_id')
    saldo_inicial = request.form.get('saldo_inicial', 0.0)
    
    if nome and tipo and instituicao_id:
        nova_conta = Conta(
            nome=nome, 
            tipo=tipo, 
            instituicao_id=instituicao_id, 
            saldo_inicial=float(saldo_inicial) if saldo_inicial else 0.0
        )
        db.session.add(nova_conta)
        db.session.commit()
        flash('Conta adicionada com sucesso!', 'success')
    else:
        flash('Preencha os campos obrigatórios.', 'danger')
        
    return redirect(url_for('accounts.index'))

@bp.route('/add_instituicao', methods=['POST'])
def add_instituicao():
    nome = request.form.get('nome')
    codigo_compensacao = request.form.get('codigo_compensacao')
    
    if nome:
        nova_inst = Instituicao(nome=nome, codigo_compensacao=codigo_compensacao)
        db.session.add(nova_inst)
        db.session.commit()
        flash('Instituição adicionada com sucesso!', 'success')
    else:
        flash('O nome da instituição é obrigatório.', 'danger')
        
    return redirect(url_for('accounts.index'))

@bp.route('/edit_conta/<int:id>', methods=['GET', 'POST'])
def edit_conta(id):
    conta = Conta.query.get_or_404(id)
    if request.method == 'POST':
        conta.nome = request.form.get('nome')
        conta.tipo = request.form.get('tipo')
        conta.instituicao_id = request.form.get('instituicao_id')
        conta.saldo_inicial = request.form.get('saldo_inicial', type=float, default=0.0)
        db.session.commit()
        flash('Conta editada com sucesso.', 'success')
        return redirect(url_for('accounts.index'))
        
    instituicoes = Instituicao.query.all()
    return render_template('accounts/edit_conta.html', conta=conta, instituicoes=instituicoes)

