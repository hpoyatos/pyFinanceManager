from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import Instituicao, Conta, Categoria, Estabelecimento, EstabelecimentoSinonimo, Transacao, Orcamento

    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.accounts import bp as accounts_bp
    app.register_blueprint(accounts_bp, url_prefix='/accounts')

    from app.routes.categories import bp as categories_bp
    app.register_blueprint(categories_bp, url_prefix='/categories')

    from app.routes.establishments import bp as establishments_bp
    app.register_blueprint(establishments_bp, url_prefix='/establishments')

    from app.routes.transactions import bp as transactions_bp
    app.register_blueprint(transactions_bp, url_prefix='/transactions')

    from app.routes.ofx import bp as ofx_bp
    app.register_blueprint(ofx_bp, url_prefix='/ofx')

    from app.routes.budget import bp as budget_bp
    app.register_blueprint(budget_bp, url_prefix='/budget')

    @app.template_filter('currency')
    def currency_filter(value):
        if value is None:
            return "R$ 0,00"
        neg = value < 0
        # Formata o número absoluto com separador de milhar (,) e 2 decimais (.)
        # Depois troca , -> . e . -> , para o padrão brasileiro
        val_str = "{:,.2f}".format(abs(value)).replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"{'- ' if neg else ''}R$ {val_str}"

    return app
