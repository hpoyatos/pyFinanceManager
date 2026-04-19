from app import db
from datetime import datetime

class Instituicao(db.Model):
    __tablename__ = 'instituicoes_bancarias'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo_compensacao = db.Column(db.String(10))
    contas = db.relationship('Conta', backref='instituicao', lazy=True)

class Conta(db.Model):
    __tablename__ = 'contas'
    id = db.Column(db.Integer, primary_key=True)
    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicoes_bancarias.id'))
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # banco ou cartao
    descricao = db.Column(db.String(255))
    saldo_inicial = db.Column(db.Float, default=0.0)
    transacoes = db.relationship('Transacao', backref='conta', lazy=True)

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # receita ou despesa
    cor = db.Column(db.String(7), default='#95a5a6')
    icone = db.Column(db.String(50), default='fa-solid fa-tag')
    parent_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    subcategorias = db.relationship('Categoria', backref=db.backref('parent', remote_side=[id]))
    estabelecimentos = db.relationship('Estabelecimento', backref='categoria', lazy=True)

class Estabelecimento(db.Model):
    __tablename__ = 'estabelecimentos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    estado = db.Column(db.String(2), nullable=True) # UF
    municipio = db.Column(db.String(100), nullable=True)
    sinonimos = db.relationship('EstabelecimentoSinonimo', backref='estabelecimento', lazy=True)

class EstabelecimentoSinonimo(db.Model):
    __tablename__ = 'estabelecimentos_sinonimos'
    id = db.Column(db.Integer, primary_key=True)
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('estabelecimentos.id'), nullable=False)
    nome_alternativo = db.Column(db.String(100), nullable=False)

class Transacao(db.Model):
    __tablename__ = 'transacoes'
    id = db.Column(db.Integer, primary_key=True)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # receita ou despesa
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(255))
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('estabelecimentos.id'), nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    conciliado = db.Column(db.Boolean, default=False)
    ofx_fitid = db.Column(db.String(255), unique=True, nullable=True)
    is_previsao = db.Column(db.Boolean, default=False)
    
    # Novos campos para Anexo (Deprecated/Legado substituído por TransacaoAnexo)
    anexo = db.Column(db.LargeBinary(length=(2**32)-1), nullable=True) # LONGBLOB
    anexo_filename = db.Column(db.String(255), nullable=True)
    
    # Marcador de Fatura de Cartão de Crédito
    fatura_periodo = db.Column(db.String(7), nullable=True) # Ex: 2026-04

    # Campo de detalhamento longo
    observacoes = db.Column(db.Text, nullable=True)
    
    estabelecimento = db.relationship('Estabelecimento', backref='transacoes', lazy=True)
    categoria = db.relationship('Categoria', backref='transacoes', lazy=True)

class TransacaoAnexo(db.Model):
    __tablename__ = 'transacoes_anexos'
    id = db.Column(db.Integer, primary_key=True)
    transacao_id = db.Column(db.Integer, db.ForeignKey('transacoes.id'), nullable=False)
    anexo = db.Column(db.LargeBinary(length=(2**32)-1), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    tipo_documento = db.Column(db.String(100), default='Outro') 
    icone = db.Column(db.String(50), default='fa-file')
    
    transacao = db.relationship('Transacao', backref=db.backref('anexos_multiplos', lazy=True, cascade='all, delete-orphan'))


class Orcamento(db.Model):
    __tablename__ = 'orcamentos'
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('estabelecimentos.id'), nullable=True)
    valor_previsto = db.Column(db.Float, nullable=False)
    
    categoria = db.relationship('Categoria', backref='orcamentos', lazy=True)
    estabelecimento = db.relationship('Estabelecimento', backref='orcamentos', lazy=True)
