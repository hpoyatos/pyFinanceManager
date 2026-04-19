from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Estabelecimento, EstabelecimentoSinonimo, Categoria

bp = Blueprint('establishments', __name__)

@bp.route('/')
def index():
    estabelecimentos = Estabelecimento.query.order_by(Estabelecimento.nome).all()
    categorias = Categoria.query.all()
    return render_template('establishments/index.html', estabelecimentos=estabelecimentos, categorias=categorias)

@bp.route('/add', methods=['POST'])
def add():
    nome = request.form.get('nome')
    categoria_id = request.form.get('categoria_id') or None
    sinonimos = request.form.get('sinonimos')
    
    if nome:
        estado = request.form.get('estado') or None
        municipio = request.form.get('municipio') or None
        novo_estab = Estabelecimento(nome=nome, categoria_id=categoria_id, estado=estado, municipio=municipio)
        db.session.add(novo_estab)
        db.session.commit()
        
        if sinonimos:
            for sinc in sinonimos.split(','):
                sin_nome = sinc.strip()
                if sin_nome:
                    novo_sin = EstabelecimentoSinonimo(estabelecimento_id=novo_estab.id, nome_alternativo=sin_nome)
                    db.session.add(novo_sin)
            db.session.commit()
            
        flash('Estabelecimento adicionado com sucesso!', 'success')
    else:
        flash('Nome do estabelecimento é obrigatório.', 'danger')
        
    return redirect(url_for('establishments.index'))

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    estab = Estabelecimento.query.get_or_404(id)
    if request.method == 'POST':
        novo_nome = request.form.get('nome')
        categoria_id = request.form.get('categoria_id') or None
        novos_sinonimos = request.form.get('sinonimos')
        merge_to_id = request.form.get('merge_to_id')
        
        if merge_to_id:
            merge_to_id = int(merge_to_id)
            if merge_to_id != id:
                from app.models import Transacao
                
                # Mover transações
                Transacao.query.filter_by(estabelecimento_id=id).update({'estabelecimento_id': merge_to_id})
                
                # Mover sinônimos
                sinonimos_atuais = EstabelecimentoSinonimo.query.filter_by(estabelecimento_id=id).all()
                for sin in sinonimos_atuais:
                    exists = EstabelecimentoSinonimo.query.filter_by(estabelecimento_id=merge_to_id, nome_alternativo=sin.nome_alternativo).first()
                    if exists:
                        db.session.delete(sin)
                    else:
                        sin.estabelecimento_id = merge_to_id
                
                # Adicionar o nome atual como sinônimo no destino
                nome_exists = EstabelecimentoSinonimo.query.filter_by(estabelecimento_id=merge_to_id, nome_alternativo=estab.nome).first()
                if not nome_exists:
                    novo_sin = EstabelecimentoSinonimo(estabelecimento_id=merge_to_id, nome_alternativo=estab.nome)
                    db.session.add(novo_sin)
                    
                # Deletar este estabelecimento original
                db.session.delete(estab)
                db.session.commit()
                flash('Estabelecimentos mesclados com sucesso! As transações foram movidas e este estabelecimento foi excluído.', 'success')
                return redirect(url_for('establishments.index'))
        
        
        if novo_nome and novo_nome != estab.nome:
            # Salvar old name como sinônimo antes de mudar
            exists = EstabelecimentoSinonimo.query.filter_by(estabelecimento_id=id, nome_alternativo=estab.nome).first()
            if not exists:
                novo_sin = EstabelecimentoSinonimo(estabelecimento_id=id, nome_alternativo=estab.nome)
                db.session.add(novo_sin)
            estab.nome = novo_nome
            
        estab.categoria_id = categoria_id
        estab.estado = request.form.get('estado') or None
        estab.municipio = request.form.get('municipio') or None
        
        if novos_sinonimos:
            for sinc in novos_sinonimos.split(','):
                sin_nome = sinc.strip()
                if sin_nome:
                    exists = EstabelecimentoSinonimo.query.filter_by(estabelecimento_id=id, nome_alternativo=sin_nome).first()
                    if not exists:
                        novo_sin = EstabelecimentoSinonimo(estabelecimento_id=id, nome_alternativo=sin_nome)
                        db.session.add(novo_sin)
                        
        db.session.commit()
        flash('Estabelecimento atualizado.', 'success')
        return redirect(url_for('establishments.index'))
        
    categorias = Categoria.query.all()
    outros_estabelecimentos = Estabelecimento.query.filter(Estabelecimento.id != id).order_by(Estabelecimento.nome).all()
    return render_template('establishments/edit.html', estab=estab, categorias=categorias, outros_estabelecimentos=outros_estabelecimentos)
