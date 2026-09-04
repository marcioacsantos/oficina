"""
Aplicação de Gestão de Equipamentos e Materiais de Oficina/Laboratório
Curso: Programador/a de Sistemas Informáticos

Versão com base de dados MySQL (normalizada), compatível com MySQL Workbench.
Ver database/gestao_oficina.sql para o script de criação da base de dados.
"""

import os
import sys
from datetime import datetime
from functools import wraps

# ---------------------------------------------------------------------------
# Se os componentes necessários (Flask, PyMySQL, etc.) não estiverem
# instalados — por exemplo, por ainda não se ter corrido
# "pip install -r requirements.txt" — a aplicação nem chega a arrancar.
# Sem este bloco, isso apareceria como um erro técnico do Python no
# terminal (traceback). Em vez disso, mostramos uma mensagem simples e
# terminamos de forma controlada.
# ---------------------------------------------------------------------------
try:
    import pymysql
    import pymysql.cursors
    from flask import (
        Flask, render_template, request, redirect, url_for,
        session, flash, g, abort
    )
    from werkzeug.security import generate_password_hash, check_password_hash
except ImportError:
    print(
        "\nNão foi possível iniciar a aplicação: faltam alguns componentes "
        "necessários para o funcionamento do programa.\n"
        "Instala-os e tenta novamente.\n"
    )
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()  # lê o ficheiro .env (se existir) e define as variáveis de ambiente
except ImportError:
    pass

app = Flask(__name__)
# A SECRET_KEY deve vir sempre de uma variável de ambiente (.env), nunca fixa
# no código. Em desenvolvimento cai numa chave só para não partir a app se
# te esqueceres do .env — mas define sempre SECRET_KEY antes de ir para produção.
app.secret_key = os.environ.get("SECRET_KEY", "dev-apenas-define-SECRET_KEY-no-.env")

# Mesmo com FLASK_DEBUG=true (usado durante o desenvolvimento), qualquer
# erro inesperado deve mostrar sempre a página de erro "erro.html" ao
# utilizador, nunca o depurador interativo do Werkzeug com o traceback —
# esse é o comportamento apropriado para um servidor de demonstração/
# produção. Sem esta linha, com FLASK_DEBUG=true, uma exceção não prevista
# ignora os errorhandler() abaixo e mostra o erro técnico completo.
app.config["PROPAGATE_EXCEPTIONS"] = False

# ---------------------------------------------------------------------------
# Configuração da ligação à base de dados MySQL
# Pode ser alterada aqui ou através de variáveis de ambiente.
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "gestao_oficina"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": False,
    # Sem estes limites, se o servidor não responder (em vez de recusar a
    # ligação de imediato — ex.: firewall a bloquear silenciosamente, ou
    # servidor em bloqueio), o pedido ficava "pendurado" indefinidamente e
    # o utilizador via apenas uma página a carregar sem fim. Com os
    # timeouts definidos, a aplicação falha ao fim de poucos segundos e
    # mostra a página de erro em vez de ficar bloqueada.
    "connect_timeout": 5,
    "read_timeout": 10,
    "write_timeout": 10,
}

# Mensagens específicas por código de erro do MySQL. São escritas em
# linguagem simples, sem termos técnicos (nomes de variáveis, códigos de
# erro, nomes de pacotes) — o pormenor técnico fica só nos registos
# internos (app.logger), nunca na página mostrada ao utilizador.
_MENSAGENS_ERRO_DB = {
    1045: "Não foi possível confirmar o acesso à base de dados. Contacta o administrador da aplicação.",
    1044: "Não tens permissões para aceder à base de dados. Contacta o administrador da aplicação.",
    1049: "A base de dados da aplicação ainda não está configurada. Contacta o administrador da aplicação.",
    2003: "Não foi possível ligar ao servidor da base de dados. Tenta novamente dentro de instantes.",
    2005: "Não foi possível encontrar o servidor da base de dados. Contacta o administrador da aplicação.",
    2006: "A ligação à base de dados foi interrompida a meio do pedido. Tenta novamente.",
    2013: "A ligação à base de dados foi interrompida a meio do pedido. Tenta novamente.",
}


def _mensagem_erro_db(exc):
    """Traduz uma exceção do PyMySQL (ou RuntimeError relacionado) numa
    mensagem simples para o utilizador, sem pormenores técnicos. Os
    pormenores completos vão sempre para app.logger, não para o ecrã."""
    if isinstance(exc, RuntimeError):
        # Ex.: falta um pacote auxiliar necessário para o método de
        # autenticação usado pelo servidor MySQL.
        return (
            "A aplicação não está corretamente configurada para ligar à "
            "base de dados. Contacta o administrador da aplicação."
        )
    codigo = exc.args[0] if exc.args else None
    return _MENSAGENS_ERRO_DB.get(codigo, (
        "Não foi possível comunicar com a base de dados. Tenta novamente "
        "dentro de instantes."
    ))


def get_db():
    if "db" not in g:
        try:
            g.db = pymysql.connect(**DB_CONFIG)
        except (pymysql.err.MySQLError, RuntimeError) as e:
            # MySQLError: serviço parado, DB_HOST/DB_PORT errados, ou
            # credenciais erradas. RuntimeError: o servidor MySQL pede um
            # método de autenticação (sha256_password /
            # caching_sha2_password) que precisa do pacote "cryptography",
            # que pode não estar instalado. Em qualquer um destes casos,
            # em vez de rebentar com um erro feio (500), mostramos uma
            # página explicativa ao utilizador.
            app.logger.error(f"Falha ao ligar à base de dados: {e}")
            abort(503, description=_mensagem_erro_db(e))
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ---------------------------------------------------------------------------
# Autenticação e Permissões
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, inicia sessão para continuar.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped


def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if session.get("perfil") != "Administrador":
            flash("Acesso restrito a administradores.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_user():
    return dict(
        current_user_nome=session.get("nome"),
        current_user_perfil=session.get("perfil"),
    )


# ---------------------------------------------------------------------------
# Páginas de erro
# Mostram uma página explicativa em vez do erro genérico do Flask/Werkzeug.
# Nota: com FLASK_DEBUG=true (desenvolvimento), erros inesperados que não
# passem por abort()/errorhandler continuam a mostrar o depurador interativo
# do Werkzeug — o que é útil enquanto se está a programar. Em produção
# (FLASK_DEBUG=false) estas páginas cobrem também esses casos.
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def erro_404(e):
    return render_template(
        "erro.html", codigo=404, titulo="Página não encontrada",
        mensagem="O endereço que tentaste abrir não existe ou foi movido.",
    ), 404


@app.errorhandler(403)
def erro_403(e):
    return render_template(
        "erro.html", codigo=403, titulo="Acesso não autorizado",
        mensagem="Não tens permissões para aceder a esta página.",
    ), 403


@app.errorhandler(503)
def erro_503(e):
    mensagem = getattr(e, "description", None) or (
        "O serviço está temporariamente indisponível. Tenta novamente "
        "dentro de instantes."
    )
    return render_template(
        "erro.html", codigo=503, titulo="Serviço indisponível",
        mensagem=mensagem,
    ), 503


@app.errorhandler(pymysql.err.MySQLError)
def erro_base_dados(e):
    # Apanha erros do MySQL que aconteçam a meio de um pedido (não apenas
    # ao ligar) — por exemplo, o servidor cair ou a ligação perder-se
    # enquanto uma consulta está a decorrer. Sem isto, esse tipo de falha
    # cairia no errorhandler(500) genérico, com uma mensagem menos clara.
    app.logger.error(f"Erro de base de dados durante o pedido: {e}")
    db = g.pop("db", None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass
    return render_template(
        "erro.html", codigo=503, titulo="Serviço indisponível",
        mensagem=_mensagem_erro_db(e),
    ), 503


@app.errorhandler(500)
def erro_500(e):
    app.logger.exception("Erro interno não tratado")
    return render_template(
        "erro.html", codigo=500, titulo="Ocorreu um erro",
        mensagem=(
            "Algo correu mal ao processar o teu pedido. Tenta novamente "
            "ou contacta o administrador se o problema persistir."
        ),
    ), 500


@app.errorhandler(Exception)
def erro_inesperado(e):
    # Rede de segurança final: qualquer exceção que não tenha sido apanhada
    # em nenhum outro sítio (incluindo tipos que não sejam do MySQL nem
    # HTTPException, como erros de validação de dados, chaves em falta,
    # etc.) acaba aqui, em vez de rebentar com um erro técnico. As
    # exceções HTTP "normais" (404, 403, 503...) já têm handler próprio
    # e não voltam a passar por aqui.
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
    return erro_500(e)


# ---------------------------------------------------------------------------
# Rotas - Autenticação
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Preenche o utilizador e a palavra-passe.", "warning")
            return render_template("login.html")
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT u.*, p.nome_perfil FROM utilizadores u
                   JOIN perfis p ON p.id_perfil = u.id_perfil
                   WHERE u.username=%s AND u.ativo=1""",
                (username,),
            )
            user = cur.fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id_utilizador"]
            session["nome"] = user["nome"]
            session["perfil"] = user["nome_perfil"]
            flash(f"Bem-vindo(a), {user['nome']}!", "success")
            return redirect(url_for("dashboard"))
        flash("Credenciais inválidas.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão terminada.", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Rotas - Dashboard
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) c FROM equipamentos")
        total_equip = cur.fetchone()["c"]

        cur.execute(
            """SELECT COUNT(*) c FROM equipamentos e
               JOIN estados_equipamento es ON es.id_estado = e.id_estado
               WHERE es.nome_estado='Disponível'"""
        )
        disponiveis = cur.fetchone()["c"]

        cur.execute(
            """SELECT COUNT(*) c FROM equipamentos e
               JOIN estados_equipamento es ON es.id_estado = e.id_estado
               WHERE es.nome_estado='Em uso'"""
        )
        em_uso = cur.fetchone()["c"]

        cur.execute(
            """SELECT COUNT(*) c FROM equipamentos e
               JOIN estados_equipamento es ON es.id_estado = e.id_estado
               WHERE es.nome_estado='Avariado'"""
        )
        avariados = cur.fetchone()["c"]

        cur.execute(
            """SELECT COUNT(*) c FROM equipamentos e
               JOIN estados_equipamento es ON es.id_estado = e.id_estado
               WHERE es.nome_estado='Em manutenção'"""
        )
        em_manutencao = cur.fetchone()["c"]

        cur.execute(
            """SELECT data_inicio, data_fim, equipamento, utilizador
               FROM vw_utilizacoes_detalhe ORDER BY id_utilizacao DESC LIMIT 5"""
        )
        ultimas = cur.fetchall()

        cur.execute("SELECT COALESCE(SUM(valor_aquisicao),0) v FROM equipamentos")
        valor_Equipamento = cur.fetchone()["v"]

        cur.execute("SELECT COUNT(*) c FROM manutencoes WHERE data_fim IS NULL")
        manutencoes_ativas = cur.fetchone()["c"]

        cur.execute(
            """SELECT COALESCE(c.nome_categoria, 'Sem categoria') AS nome_categoria, COUNT(*) c
               FROM equipamentos e
               LEFT JOIN categorias c ON c.id_categoria = e.id_categoria
               GROUP BY COALESCE(c.nome_categoria, 'Sem categoria') ORDER BY c DESC"""
        )
        por_categoria = cur.fetchall()

        # Tendência mensal de utilizações (últimos 6 meses)
        # Nota: sem passar parâmetros ao execute(), o pymysql não faz a
        # conversão "%%" -> "%" (só o faz quando há args). Por isso aqui
        # usa-se um único "%", tal como é enviado diretamente ao MySQL.
        cur.execute(
            """SELECT DATE_FORMAT(data_inicio, '%Y-%m') AS mes, COUNT(*) c
               FROM utilizacoes
               WHERE data_inicio >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
               GROUP BY DATE_FORMAT(data_inicio, '%Y-%m')
               ORDER BY mes"""
        )
        tendencia_mensal = cur.fetchall()

        # Top 5 equipamentos mais utilizados
        cur.execute(
            """SELECT e.designacao, COUNT(*) c
               FROM utilizacoes u
               JOIN equipamentos e ON e.id_equipamento = u.id_equipamento
               GROUP BY e.designacao
               ORDER BY c DESC
               LIMIT 5"""
        )
        top_equipamentos = cur.fetchall()

    return render_template(
        "dashboard.html",
        total_equip=total_equip,
        disponiveis=disponiveis,
        em_uso=em_uso,
        avariados=avariados,
        em_manutencao=em_manutencao,
        ultimas=ultimas,
        valor_Equipamento=valor_Equipamento,
        manutencoes_ativas=manutencoes_ativas,
        por_categoria=por_categoria,
        tendencia_mensal=tendencia_mensal,
        top_equipamentos=top_equipamentos,
    )


# ---------------------------------------------------------------------------
# Rotas - Equipamentos (CRUD)
# ---------------------------------------------------------------------------

@app.route("/equipamentos")
@login_required
def listar_equipamentos():
    db = get_db()
    pesquisa = request.args.get("q", "").strip()
    agora = datetime.now()
    with db.cursor() as cur:
        if pesquisa:
            like = f"%{pesquisa}%"
            cur.execute(
                """SELECT e.*, c.nome_categoria, l.designacao AS localizacao_nome,
                          es.nome_estado, rr.data_inicio AS reserva_inicio,
                          rr.data_fim AS reserva_fim, ru.nome AS reserva_utilizador
                   FROM equipamentos e
                   LEFT JOIN categorias c ON c.id_categoria = e.id_categoria
                   LEFT JOIN localizacoes l ON l.id_localizacao = e.id_localizacao
                   LEFT JOIN estados_equipamento es ON es.id_estado = e.id_estado
                   LEFT JOIN reservas rr ON rr.id_equipamento = e.id_equipamento
                        AND rr.data_inicio <= %s AND rr.data_fim > %s
                   LEFT JOIN utilizadores ru ON ru.id_utilizador = rr.id_utilizador
                   WHERE e.designacao LIKE %s OR c.nome_categoria LIKE %s
                      OR e.numero_inventario LIKE %s
                   ORDER BY e.designacao""",
                (agora, agora, like, like, like),
            )
        else:
            cur.execute(
                """SELECT e.*, c.nome_categoria, l.designacao AS localizacao_nome,
                          es.nome_estado, rr.data_inicio AS reserva_inicio,
                          rr.data_fim AS reserva_fim, ru.nome AS reserva_utilizador
                   FROM equipamentos e
                   LEFT JOIN categorias c ON c.id_categoria = e.id_categoria
                   LEFT JOIN localizacoes l ON l.id_localizacao = e.id_localizacao
                   LEFT JOIN estados_equipamento es ON es.id_estado = e.id_estado
                   LEFT JOIN reservas rr ON rr.id_equipamento = e.id_equipamento
                        AND rr.data_inicio <= %s AND rr.data_fim > %s
                   LEFT JOIN utilizadores ru ON ru.id_utilizador = rr.id_utilizador
                   ORDER BY e.designacao""",
                (agora, agora),
            )
        equipamentos = cur.fetchall()

    # Pedido feito via JavaScript (pesquisa em tempo real): devolve apenas
    # as linhas da tabela, sem o resto da página.
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template("_equipamentos_linhas.html", equipamentos=equipamentos)

    return render_template("equipamentos_lista.html", equipamentos=equipamentos, pesquisa=pesquisa)


def _proximo_numero_inventario(db):
    """Calcula o próximo número de inventário automaticamente (formato EQ-0001).

    Olha para o maior número já usado e soma 1, mantendo sempre o padrão
    EQ-XXXX com zeros à esquerda. A coluna numero_inventario continua a ser
    um VARCHAR normal na base de dados (nada é alterado no esquema), por
    isso não há qualquer conflito com o que já está criado no MySQL Workbench.
    """
    with db.cursor() as cur:
        cur.execute(
            """SELECT numero_inventario FROM equipamentos
               WHERE numero_inventario REGEXP '^EQ-[0-9]+$'
               ORDER BY CAST(SUBSTRING(numero_inventario, 4) AS UNSIGNED) DESC
               LIMIT 1"""
        )
        ultimo = cur.fetchone()
    if ultimo:
        try:
            numero = int(ultimo["numero_inventario"].split("-")[1]) + 1
        except (ValueError, IndexError):
            numero = 1
    else:
        numero = 1
    return f"EQ-{numero:04d}"


def _listas_apoio(db):
    """Devolve categorias, localizações, estados e fornecedores para preencher dropdowns."""
    with db.cursor() as cur:
        cur.execute("SELECT * FROM categorias ORDER BY nome_categoria")
        categorias = cur.fetchall()
        cur.execute("SELECT * FROM localizacoes ORDER BY designacao")
        localizacoes = cur.fetchall()
        cur.execute("SELECT * FROM estados_equipamento ORDER BY id_estado")
        estados = cur.fetchall()
        cur.execute("SELECT * FROM fornecedores ORDER BY nome")
        fornecedores = cur.fetchall()
    return categorias, localizacoes, estados, fornecedores


def _reserva_ativa_agora(db, eq_id):
    """Devolve a reserva (com o nome de quem reservou) que cobre este preciso
    momento para o equipamento indicado, ou None se não houver nenhuma.

    Isto é o que liga as Reservas às Utilizações: antes de deixar alguém
    começar a usar um equipamento, verificamos se não há uma reserva de
    outra pessoa a decorrer agora mesmo para esse equipamento.
    """
    agora = datetime.now()
    with db.cursor() as cur:
        cur.execute(
            """SELECT r.*, ut.nome AS utilizador_nome FROM reservas r
               JOIN utilizadores ut ON ut.id_utilizador = r.id_utilizador
               WHERE r.id_equipamento=%s AND r.data_inicio <= %s AND r.data_fim > %s
               ORDER BY r.data_inicio LIMIT 1""",
            (eq_id, agora, agora),
        )
        return cur.fetchone()


def _proxima_reserva_futura(db, eq_id, excluir_utilizador_id=None):
    """Devolve a próxima reserva futura (ainda não começada) de OUTRA pessoa
    para este equipamento, ou None se não houver nenhuma.

    Isto fecha a outra ponta da ligação Reservas <-> Utilizações: uma
    utilização não tem hora de fim garantida (fica aberta até alguém a
    terminar), por isso, além de verificar reservas já a decorrer, também
    é preciso impedir iniciar uma utilização que iria previsivelmente
    colidir com uma reserva futura de outra pessoa - caso contrário essa
    reserva fica "queimada" quando o equipamento continuar em uso.
    """
    agora = datetime.now()
    with db.cursor() as cur:
        if excluir_utilizador_id is not None:
            cur.execute(
                """SELECT r.*, ut.nome AS utilizador_nome FROM reservas r
                   JOIN utilizadores ut ON ut.id_utilizador = r.id_utilizador
                   WHERE r.id_equipamento=%s AND r.data_inicio > %s
                     AND r.id_utilizador <> %s
                   ORDER BY r.data_inicio LIMIT 1""",
                (eq_id, agora, excluir_utilizador_id),
            )
        else:
            cur.execute(
                """SELECT r.*, ut.nome AS utilizador_nome FROM reservas r
                   JOIN utilizadores ut ON ut.id_utilizador = r.id_utilizador
                   WHERE r.id_equipamento=%s AND r.data_inicio > %s
                   ORDER BY r.data_inicio LIMIT 1""",
                (eq_id, agora),
            )
        return cur.fetchone()


@app.route("/equipamentos/novo", methods=["GET", "POST"])
@login_required
@admin_required
def novo_equipamento():
    db = get_db()
    categorias, localizacoes, estados, fornecedores = _listas_apoio(db)
    if request.method == "POST":
        designacao = request.form.get("designacao", "").strip()
        if not designacao:
            flash("A designação do equipamento é obrigatória.", "warning")
            return render_template(
                "equipamento_form.html", equipamento=None,
                categorias=categorias, localizacoes=localizacoes, estados=estados,
                fornecedores=fornecedores,
                proximo_numero_inventario=_proximo_numero_inventario(db),
            )
        try:
            with db.cursor() as cur:
                numero_inventario = _proximo_numero_inventario(db)
                cur.execute(
                    """INSERT INTO equipamentos
                       (designacao, numero_inventario, id_categoria, id_localizacao, id_estado,
                        id_fornecedor, data_aquisicao, valor_aquisicao, observacoes)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        designacao,
                        numero_inventario,
                        request.form.get("id_categoria") or None,
                        request.form.get("id_localizacao") or None,
                        request.form.get("id_estado"),
                        request.form.get("id_fornecedor") or None,
                        request.form.get("data_aquisicao") or None,
                        request.form.get("valor_aquisicao") or None,
                        request.form.get("observacoes", "").strip() or None,
                    ),
                )
            db.commit()
            flash("Equipamento adicionado com sucesso.", "success")
            return redirect(url_for("listar_equipamentos"))
        except pymysql.err.IntegrityError:
            db.rollback()
            flash("Já existe um equipamento com esse número de inventário.", "danger")
    return render_template(
        "equipamento_form.html", equipamento=None,
        categorias=categorias, localizacoes=localizacoes, estados=estados,
        fornecedores=fornecedores,
        proximo_numero_inventario=_proximo_numero_inventario(db),
    )


@app.route("/equipamentos/<int:eq_id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar_equipamento(eq_id):
    db = get_db()
    categorias, localizacoes, estados, fornecedores = _listas_apoio(db)
    with db.cursor() as cur:
        cur.execute("SELECT * FROM equipamentos WHERE id_equipamento=%s", (eq_id,))
        equipamento = cur.fetchone()
    if not equipamento:
        flash("Equipamento não encontrado.", "danger")
        return redirect(url_for("listar_equipamentos"))
    if request.method == "POST":
        designacao = request.form.get("designacao", "").strip()
        if not designacao:
            flash("A designação do equipamento é obrigatória.", "warning")
            return render_template(
                "equipamento_form.html", equipamento=equipamento,
                categorias=categorias, localizacoes=localizacoes, estados=estados,
                fornecedores=fornecedores,
            )
        try:
            novo_id_estado = request.form.get("id_estado")
            with db.cursor() as cur:
                # Nome do novo estado escolhido, para saber se é "Em uso"
                cur.execute(
                    "SELECT nome_estado FROM estados_equipamento WHERE id_estado=%s",
                    (novo_id_estado,),
                )
                novo_estado_row = cur.fetchone()
                novo_nome_estado = novo_estado_row["nome_estado"] if novo_estado_row else None

                # Existe alguma utilização em aberto (data_fim IS NULL) para este equipamento?
                cur.execute(
                    """SELECT id_utilizacao FROM utilizacoes
                       WHERE id_equipamento=%s AND data_fim IS NULL""",
                    (eq_id,),
                )
                utilizacao_aberta = cur.fetchone()

                # Existe alguma manutenção em aberto (data_fim IS NULL) para este equipamento?
                cur.execute(
                    """SELECT id_manutencao FROM manutencoes
                       WHERE id_equipamento=%s AND data_fim IS NULL""",
                    (eq_id,),
                )
                manutencao_aberta = cur.fetchone()

                # Impede marcar "Em uso" manualmente sem existir uma utilização aberta,
                # para não dessincronizar equipamentos vs. utilizações.
                if novo_nome_estado == "Em uso" and not utilizacao_aberta:
                    flash(
                        "Não é possível definir o estado como 'Em uso' diretamente. "
                        "Para colocar este equipamento em uso, regista uma nova utilização.",
                        "warning",
                    )
                    return render_template(
                        "equipamento_form.html", equipamento=equipamento,
                        categorias=categorias, localizacoes=localizacoes, estados=estados,
                        fornecedores=fornecedores,
                    )

                # Impede marcar "Em manutenção" manualmente sem existir uma manutenção aberta,
                # para não dessincronizar equipamentos vs. manutenções.
                if novo_nome_estado == "Em manutenção" and not manutencao_aberta:
                    flash(
                        "Não é possível definir o estado como 'Em manutenção' diretamente. "
                        "Para colocar este equipamento em manutenção, regista uma nova manutenção "
                        "a partir da página de histórico do equipamento.",
                        "warning",
                    )
                    return render_template(
                        "equipamento_form.html", equipamento=equipamento,
                        categorias=categorias, localizacoes=localizacoes, estados=estados,
                        fornecedores=fornecedores,
                    )

                cur.execute(
                    """UPDATE equipamentos SET designacao=%s, numero_inventario=%s,
                       id_categoria=%s, id_localizacao=%s, id_estado=%s,
                       id_fornecedor=%s, data_aquisicao=%s, valor_aquisicao=%s, observacoes=%s
                       WHERE id_equipamento=%s""",
                    (
                        designacao,
                        request.form.get("numero_inventario", "").strip(),
                        request.form.get("id_categoria") or None,
                        request.form.get("id_localizacao") or None,
                        novo_id_estado,
                        request.form.get("id_fornecedor") or None,
                        request.form.get("data_aquisicao") or None,
                        request.form.get("valor_aquisicao") or None,
                        request.form.get("observacoes", "").strip() or None,
                        eq_id,
                    ),
                )

                # Se o estado deixou de ser "Em uso" mas havia uma utilização aberta,
                # fecha-a automaticamente para manter equipamentos e utilizações sincronizados.
                if novo_nome_estado != "Em uso" and utilizacao_aberta:
                    cur.execute(
                        "UPDATE utilizacoes SET data_fim=%s WHERE id_utilizacao=%s",
                        (datetime.now(), utilizacao_aberta["id_utilizacao"]),
                    )

                # Se o estado deixou de ser "Em manutenção" mas havia uma manutenção aberta,
                # fecha-a automaticamente para manter equipamentos e manutenções sincronizados.
                if novo_nome_estado != "Em manutenção" and manutencao_aberta:
                    cur.execute(
                        "UPDATE manutencoes SET data_fim=%s WHERE id_manutencao=%s",
                        (hoje := datetime.now().strftime("%Y-%m-%d"), manutencao_aberta["id_manutencao"]),
                    )
            db.commit()
            flash("Equipamento atualizado com sucesso.", "success")
            return redirect(url_for("listar_equipamentos"))
        except pymysql.err.IntegrityError:
            db.rollback()
            flash("Já existe um equipamento com esse número de inventário.", "danger")
    return render_template(
        "equipamento_form.html", equipamento=equipamento,
        categorias=categorias, localizacoes=localizacoes, estados=estados,
        fornecedores=fornecedores,
    )


@app.route("/equipamentos/<int:eq_id>/remover", methods=["POST"])
@login_required
@admin_required
def remover_equipamento(eq_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT es.nome_estado
               FROM equipamentos e
               JOIN estados_equipamento es ON es.id_estado = e.id_estado
               WHERE e.id_equipamento=%s""",
            (eq_id,),
        )
        equipamento = cur.fetchone()

        if equipamento is None:
            flash("Equipamento não encontrado.", "warning")
            return redirect(url_for("listar_equipamentos"))

        if equipamento["nome_estado"] == "Em uso":
            flash("Não é possível remover este equipamento porque está atualmente em uso.", "warning")
            return redirect(url_for("listar_equipamentos"))

        cur.execute("DELETE FROM equipamentos WHERE id_equipamento=%s", (eq_id,))
    db.commit()
    flash("Equipamento removido.", "info")
    return redirect(url_for("listar_equipamentos"))


@app.route("/equipamentos/<int:eq_id>/historico")
@login_required
def historico_equipamento(eq_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT e.*, c.nome_categoria, l.designacao AS localizacao_nome,
                      es.nome_estado, f.nome AS fornecedor_nome
               FROM equipamentos e
               LEFT JOIN categorias c ON c.id_categoria = e.id_categoria
               LEFT JOIN localizacoes l ON l.id_localizacao = e.id_localizacao
               LEFT JOIN estados_equipamento es ON es.id_estado = e.id_estado
               LEFT JOIN fornecedores f ON f.id_fornecedor = e.id_fornecedor
               WHERE e.id_equipamento=%s""",
            (eq_id,),
        )
        equipamento = cur.fetchone()
        cur.execute(
            """SELECT u.*, ut.nome AS utilizador_nome FROM utilizacoes u
               JOIN utilizadores ut ON ut.id_utilizador = u.id_utilizador
               WHERE id_equipamento=%s ORDER BY u.id_utilizacao DESC""",
            (eq_id,),
        )
        historico = cur.fetchall()
        cur.execute(
            """SELECT * FROM manutencoes WHERE id_equipamento=%s
               ORDER BY id_manutencao DESC""",
            (eq_id,),
        )
        manutencoes = cur.fetchall()
    return render_template(
        "historico_equipamento.html", equipamento=equipamento,
        historico=historico, manutencoes=manutencoes,
    )


# ---------------------------------------------------------------------------
# Rotas - Manutenções (aproveita a tabela 'manutencoes' já existente na BD)
# ---------------------------------------------------------------------------

@app.route("/equipamentos/<int:eq_id>/manutencoes/nova", methods=["POST"])
@login_required
@admin_required
def nova_manutencao(eq_id):
    db = get_db()
    descricao = request.form.get("descricao", "").strip()
    if not descricao:
        flash("Descreve o motivo da manutenção.", "danger")
        return redirect(url_for("historico_equipamento", eq_id=eq_id))
    hoje = datetime.now().strftime("%Y-%m-%d")
    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO manutencoes (id_equipamento, data_inicio, descricao)
               VALUES (%s,%s,%s)""",
            (eq_id, hoje, descricao),
        )
        cur.execute(
            """UPDATE equipamentos SET id_estado =
               (SELECT id_estado FROM estados_equipamento WHERE nome_estado='Em manutenção')
               WHERE id_equipamento=%s""",
            (eq_id,),
        )
        # Se o equipamento estava "Em uso", a utilização aberta fica órfã
        # (o equipamento passa a "Em manutenção" mas a utilização nunca é
        # fechada). Fecha-a automaticamente para manter tudo sincronizado,
        # tal como já acontece ao editar o equipamento manualmente.
        cur.execute(
            """SELECT id_utilizacao FROM utilizacoes
               WHERE id_equipamento=%s AND data_fim IS NULL""",
            (eq_id,),
        )
        utilizacao_aberta = cur.fetchone()
        if utilizacao_aberta:
            cur.execute(
                "UPDATE utilizacoes SET data_fim=%s WHERE id_utilizacao=%s",
                (datetime.now(), utilizacao_aberta["id_utilizacao"]),
            )
    db.commit()
    flash("Manutenção registada. Equipamento marcado como 'Em manutenção'.", "success")
    return redirect(url_for("historico_equipamento", eq_id=eq_id))


@app.route("/manutencoes/<int:man_id>/concluir", methods=["POST"])
@login_required
@admin_required
def concluir_manutencao(man_id):
    db = get_db()
    custo = request.form.get("custo") or None
    with db.cursor() as cur:
        cur.execute("SELECT * FROM manutencoes WHERE id_manutencao=%s", (man_id,))
        manutencao = cur.fetchone()
        if not manutencao:
            flash("Manutenção não encontrada.", "danger")
            return redirect(url_for("listar_equipamentos"))
        hoje = datetime.now().strftime("%Y-%m-%d")
        cur.execute(
            "UPDATE manutencoes SET data_fim=%s, custo=%s WHERE id_manutencao=%s",
            (hoje, custo, man_id),
        )
        cur.execute(
            """UPDATE equipamentos SET id_estado =
               (SELECT id_estado FROM estados_equipamento WHERE nome_estado='Disponível')
               WHERE id_equipamento=%s""",
            (manutencao["id_equipamento"],),
        )
        db.commit()
        flash("Manutenção concluída. Equipamento novamente disponível.", "success")
    return redirect(url_for("historico_equipamento", eq_id=manutencao["id_equipamento"]))


# ---------------------------------------------------------------------------
# Rotas - Registo de Utilização
# ---------------------------------------------------------------------------

@app.route("/utilizacoes/nova", methods=["GET", "POST"])
@login_required
def nova_utilizacao():
    db = get_db()
    if request.method == "POST":
        equipamento_id = request.form.get("equipamento_id")
        if not equipamento_id:
            flash("Escolhe um equipamento.", "danger")
            return redirect(url_for("nova_utilizacao"))

        with db.cursor() as cur:
            cur.execute(
                """SELECT e.*, es.nome_estado FROM equipamentos e
                   JOIN estados_equipamento es ON es.id_estado = e.id_estado
                   WHERE e.id_equipamento=%s""",
                (equipamento_id,),
            )
            equipamento = cur.fetchone()

        if not equipamento:
            flash("Equipamento não encontrado.", "danger")
            return redirect(url_for("nova_utilizacao"))

        # O estado tem de estar "Disponível" — verificado outra vez aqui
        # (e não só ao construir a lista de opções) para o caso de o
        # pedido ser alterado manualmente ou o estado ter mudado entretanto.
        if equipamento["nome_estado"] != "Disponível":
            flash(
                f"'{equipamento['designacao']}' já não está disponível "
                f"(estado atual: {equipamento['nome_estado']}). Escolhe outro equipamento.",
                "danger",
            )
            return redirect(url_for("nova_utilizacao"))

        # Ligação com as Reservas: se houver uma reserva a decorrer agora
        # mesmo para este equipamento e não for do próprio utilizador,
        # impede o registo da utilização — é isso que evita o conflito de
        # alguém "roubar" um equipamento que outra pessoa reservou.
        reserva_agora = _reserva_ativa_agora(db, equipamento_id)
        if reserva_agora and reserva_agora["id_utilizador"] != session["user_id"]:
            fim_str = reserva_agora["data_fim"].strftime("%d/%m/%Y %H:%M")
            flash(
                f"'{equipamento['designacao']}' está reservado por "
                f"{reserva_agora['utilizador_nome']} até {fim_str}. "
                "Escolhe outro equipamento ou aguarda o fim da reserva.",
                "danger",
            )
            return redirect(url_for("nova_utilizacao"))

        # Também impede iniciar uma utilização se houver uma reserva futura
        # de outra pessoa para este equipamento. Como uma utilização não tem
        # hora de fim garantida, deixar isto passar arriscaria "roubar" a
        # reserva de outra pessoa por o equipamento continuar em uso quando
        # essa reserva começasse.
        reserva_futura = _proxima_reserva_futura(db, equipamento_id, session["user_id"])
        if reserva_futura:
            inicio_str = reserva_futura["data_inicio"].strftime("%d/%m/%Y %H:%M")
            flash(
                f"'{equipamento['designacao']}' tem uma reserva de "
                f"{reserva_futura['utilizador_nome']} a começar às {inicio_str}. "
                "Não é possível iniciar uma utilização sem hora de fim garantida "
                "para este equipamento. Escolhe outro equipamento, ou termina a "
                "utilização antes desse horário.",
                "danger",
            )
            return redirect(url_for("nova_utilizacao"))

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with db.cursor() as cur:
            cur.execute(
                """INSERT INTO utilizacoes (id_equipamento, id_utilizador, data_inicio, observacoes)
                   VALUES (%s,%s,%s,%s)""",
                (equipamento_id, session["user_id"], agora, request.form.get("observacoes", "")),
            )
            cur.execute(
                """UPDATE equipamentos SET id_estado =
                   (SELECT id_estado FROM estados_equipamento WHERE nome_estado='Em uso')
                   WHERE id_equipamento=%s""",
                (equipamento_id,),
            )
            # Se esta utilização cumpre a própria reserva do utilizador,
            # a reserva deixa de fazer sentido — removê-la para não ficar
            # a "duplicar" o mesmo período nas duas listas.
            if reserva_agora and reserva_agora["id_utilizador"] == session["user_id"]:
                cur.execute(
                    "DELETE FROM reservas WHERE id_reserva=%s",
                    (reserva_agora["id_reserva"],),
                )
        db.commit()
        flash("Utilização registada. Equipamento marcado como 'Em uso'.", "success")
        return redirect(url_for("minhas_utilizacoes"))

    agora = datetime.now()
    with db.cursor() as cur:
        # Só mostra equipamento marcado como "Disponível" E que não esteja
        # reservado (agora, ou numa reserva futura) por OUTRA pessoa. Se o
        # próprio utilizador tiver uma reserva para o equipamento, continua
        # a poder escolhê-lo (está a cumprir a sua própria reserva).
        cur.execute(
            """SELECT e.* FROM equipamentos e
               JOIN estados_equipamento es ON es.id_estado = e.id_estado
               WHERE es.nome_estado='Disponível'
                 AND NOT EXISTS (
                     SELECT 1 FROM reservas r
                     WHERE r.id_equipamento = e.id_equipamento
                       AND r.data_fim > %s
                       AND r.id_utilizador <> %s
                 )
               ORDER BY e.designacao""",
            (agora, session["user_id"]),
        )
        equipamentos = cur.fetchall()
    return render_template("utilizacao_form.html", equipamentos=equipamentos)


@app.route("/utilizacoes/<int:ut_id>/terminar", methods=["POST"])
@login_required
def terminar_utilizacao(ut_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM utilizacoes WHERE id_utilizacao=%s", (ut_id,))
        utilizacao = cur.fetchone()
        if utilizacao and (
            session["perfil"] == "Administrador" or utilizacao["id_utilizador"] == session["user_id"]
        ):
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("UPDATE utilizacoes SET data_fim=%s WHERE id_utilizacao=%s", (agora, ut_id))
            cur.execute(
                """UPDATE equipamentos SET id_estado =
                   (SELECT id_estado FROM estados_equipamento WHERE nome_estado='Disponível')
                   WHERE id_equipamento=%s""",
                (utilizacao["id_equipamento"],),
            )
            db.commit()
            flash("Utilização terminada. Equipamento novamente disponível.", "success")
    return redirect(url_for("minhas_utilizacoes"))


@app.route("/minhas-utilizacoes")
@login_required
def minhas_utilizacoes():
    db = get_db()
    with db.cursor() as cur:
        if session["perfil"] == "Administrador":
            cur.execute(
                """SELECT u.*, e.designacao, ut.nome AS utilizador_nome FROM utilizacoes u
                   JOIN equipamentos e ON e.id_equipamento = u.id_equipamento
                   JOIN utilizadores ut ON ut.id_utilizador = u.id_utilizador
                   ORDER BY u.id_utilizacao DESC"""
            )
        else:
            cur.execute(
                """SELECT u.*, e.designacao, ut.nome AS utilizador_nome FROM utilizacoes u
                   JOIN equipamentos e ON e.id_equipamento = u.id_equipamento
                   JOIN utilizadores ut ON ut.id_utilizador = u.id_utilizador
                   WHERE u.id_utilizador=%s ORDER BY u.id_utilizacao DESC""",
                (session["user_id"],),
            )
        registos = cur.fetchall()
    return render_template("utilizacoes_lista.html", registos=registos)


# ---------------------------------------------------------------------------
# Rotas - Reservas de Equipamentos
# ---------------------------------------------------------------------------

@app.route("/reservas")
@login_required
def listar_reservas():
    db = get_db()
    with db.cursor() as cur:
        if session["perfil"] == "Administrador":
            cur.execute(
                """SELECT r.*, e.designacao, e.numero_inventario, ut.nome AS utilizador_nome
                   FROM reservas r
                   JOIN equipamentos e ON e.id_equipamento = r.id_equipamento
                   JOIN utilizadores ut ON ut.id_utilizador = r.id_utilizador
                   ORDER BY r.data_inicio DESC"""
            )
        else:
            cur.execute(
                """SELECT r.*, e.designacao, e.numero_inventario, ut.nome AS utilizador_nome
                   FROM reservas r
                   JOIN equipamentos e ON e.id_equipamento = r.id_equipamento
                   JOIN utilizadores ut ON ut.id_utilizador = r.id_utilizador
                   WHERE r.id_utilizador=%s ORDER BY r.data_inicio DESC""",
                (session["user_id"],),
            )
        reservas = cur.fetchall()
    agora = datetime.now()
    return render_template("reservas_lista.html", reservas=reservas, agora=agora)


@app.route("/reservas/nova", methods=["GET", "POST"])
@login_required
def nova_reserva():
    db = get_db()
    with db.cursor() as cur:
        # Só é possível reservar equipamento que esteja disponível. Um
        # equipamento em uso, em manutenção ou avariado não pode ser
        # reservado enquanto não voltar a ficar "Disponível".
        cur.execute(
            """SELECT e.*, es.nome_estado FROM equipamentos e
               JOIN estados_equipamento es ON es.id_estado = e.id_estado
               WHERE es.nome_estado = 'Disponível'
               ORDER BY e.designacao"""
        )
        equipamentos = cur.fetchall()

    if request.method == "POST":
        equipamento_id = request.form.get("equipamento_id")
        data_inicio = request.form.get("data_inicio", "").strip()
        data_fim = request.form.get("data_fim", "").strip()
        observacoes = request.form.get("observacoes", "").strip() or None

        erro = None
        inicio_dt = fim_dt = None
        if not equipamento_id or not data_inicio or not data_fim:
            erro = "Preenche o equipamento e o período da reserva."

        equipamento = None
        if not erro:
            with db.cursor() as cur:
                cur.execute(
                    """SELECT e.*, es.nome_estado FROM equipamentos e
                       JOIN estados_equipamento es ON es.id_estado = e.id_estado
                       WHERE e.id_equipamento=%s""",
                    (equipamento_id,),
                )
                equipamento = cur.fetchone()
            if not equipamento:
                erro = "Equipamento não encontrado."
            elif equipamento["nome_estado"] != "Disponível":
                erro = (
                    f"'{equipamento['designacao']}' está atualmente "
                    f"'{equipamento['nome_estado']}' e não pode ser reservado."
                )

        if not erro:
            try:
                inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%dT%H:%M")
                fim_dt = datetime.strptime(data_fim, "%Y-%m-%dT%H:%M")
            except ValueError:
                erro = "Datas inválidas."
            else:
                if fim_dt <= inicio_dt:
                    erro = "A data/hora de fim tem de ser depois da data/hora de início."
                elif fim_dt <= datetime.now():
                    erro = "Não é possível reservar para um período que já passou."

        if not erro:
            with db.cursor() as cur:
                # Impede sobreposição com outra reserva já existente para o mesmo equipamento.
                cur.execute(
                    """SELECT id_reserva FROM reservas
                       WHERE id_equipamento=%s AND data_inicio < %s AND data_fim > %s""",
                    (equipamento_id, fim_dt, inicio_dt),
                )
                conflito = cur.fetchone()
            if conflito:
                erro = "Já existe uma reserva para este equipamento nesse período."

        if erro:
            flash(erro, "danger")
            return render_template("reserva_form.html", equipamentos=equipamentos, form=request.form)

        with db.cursor() as cur:
            cur.execute(
                """INSERT INTO reservas (id_equipamento, id_utilizador, data_inicio, data_fim, observacoes)
                   VALUES (%s,%s,%s,%s,%s)""",
                (equipamento_id, session["user_id"], inicio_dt, fim_dt, observacoes),
            )
        db.commit()
        flash("Reserva criada com sucesso.", "success")
        return redirect(url_for("listar_reservas"))

    return render_template("reserva_form.html", equipamentos=equipamentos, form={})


@app.route("/reservas/<int:res_id>/cancelar", methods=["POST"])
@login_required
def cancelar_reserva(res_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM reservas WHERE id_reserva=%s", (res_id,))
        reserva = cur.fetchone()
        if reserva and (
            session["perfil"] == "Administrador" or reserva["id_utilizador"] == session["user_id"]
        ):
            cur.execute("DELETE FROM reservas WHERE id_reserva=%s", (res_id,))
            db.commit()
            flash("Reserva cancelada.", "info")
        else:
            flash("Reserva não encontrada.", "warning")
    return redirect(url_for("listar_reservas"))


# ---------------------------------------------------------------------------
# Rotas - Utilizadores (apenas Administrador)
# ---------------------------------------------------------------------------

@app.route("/utilizadores")
@login_required
@admin_required
def listar_utilizadores():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT u.*, p.nome_perfil FROM utilizadores u
               JOIN perfis p ON p.id_perfil = u.id_perfil ORDER BY u.nome"""
        )
        utilizadores = cur.fetchall()
    return render_template("utilizadores_lista.html", utilizadores=utilizadores)


@app.route("/utilizadores/novo", methods=["GET", "POST"])
@login_required
@admin_required
def novo_utilizador():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM perfis ORDER BY id_perfil")
        perfis = cur.fetchall()
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        id_perfil = request.form.get("id_perfil")
        if not nome or not username or not password or not id_perfil:
            flash("Preenche o nome, o utilizador, a palavra-passe e o perfil.", "warning")
            return render_template("utilizador_form.html", perfis=perfis)
        try:
            password_hash = generate_password_hash(password)
            with db.cursor() as cur:
                cur.execute(
                    """INSERT INTO utilizadores (nome, username, password_hash, id_perfil)
                       VALUES (%s,%s,%s,%s)""",
                    (nome, username, password_hash, id_perfil),
                )
            db.commit()
            flash("Utilizador criado com sucesso.", "success")
            return redirect(url_for("listar_utilizadores"))
        except pymysql.err.IntegrityError:
            db.rollback()
            flash("Já existe um utilizador com esse username.", "danger")
    return render_template("utilizador_form.html", perfis=perfis)


@app.route("/utilizadores/<int:uid>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_utilizador(uid):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM utilizadores WHERE id_utilizador=%s", (uid,))
        user = cur.fetchone()
        if user:
            novo_estado = 0 if user["ativo"] else 1
            cur.execute("UPDATE utilizadores SET ativo=%s WHERE id_utilizador=%s", (novo_estado, uid))
    db.commit()
    flash("Estado do utilizador atualizado.", "info")
    return redirect(url_for("listar_utilizadores"))


# ---------------------------------------------------------------------------
# Rotas - Relatórios
# ---------------------------------------------------------------------------

@app.route("/relatorios")
@login_required
def relatorios():
    db = get_db()
    if session.get("perfil") == "Administrador":
        with db.cursor() as cur:
            cur.execute("SELECT * FROM equipamentos ORDER BY designacao")
            equipamentos = cur.fetchall()
            cur.execute("SELECT * FROM utilizadores ORDER BY nome")
            utilizadores = cur.fetchall()
        return render_template("relatorios.html", equipamentos=equipamentos, utilizadores=utilizadores)

    # Utilizador comum: só vê o cartão do relatório pessoal, sem listas de
    # todos os equipamentos/utilizadores (que só interessam aos relatórios
    # de administrador).
    return render_template("relatorios.html", equipamentos=[], utilizadores=[])


def _tipo_e_args_relatorio(request_args):
    """Decide que relatório vai realmente ser gerado.

    Um Administrador pode pedir qualquer tipo de relatório (geral, por
    equipamento, por utilizador, manutenções). Um utilizador comum só pode
    ver o SEU PRÓPRIO relatório de utilização — independentemente do que
    for enviado no pedido (ex: alguém a tentar mudar o "utilizador_id" ou
    o "tipo" diretamente no URL). Isto evita que um utilizador veja dados
    de outra pessoa ou relatórios que só fazem sentido para a gestão.
    """
    if session.get("perfil") == "Administrador":
        return request_args.get("tipo", "geral"), request_args
    return "utilizador", {"utilizador_id": session["user_id"]}


def _obter_dados_relatorio(tipo, args):
    """Executa as queries do relatório pedido e devolve (titulo, registos, resumo).

    O "resumo" é uma contagem de quantas vezes cada utilizador/equipamento
    aparece nos registos — permite responder rapidamente a "quantas vezes
    é que o Fulano usou este equipamento?" sem ter de contar as linhas à mão.
    """
    db = get_db()
    resumo = []
    with db.cursor() as cur:
        if tipo == "equipamento":
            eq_id = args.get("equipamento_id")
            cur.execute("SELECT * FROM equipamentos WHERE id_equipamento=%s", (eq_id,))
            equipamento = cur.fetchone()
            cur.execute(
                """SELECT u.*, ut.nome AS utilizador_nome FROM utilizacoes u
                   JOIN utilizadores ut ON ut.id_utilizador = u.id_utilizador
                   WHERE id_equipamento=%s ORDER BY u.id_utilizacao DESC""",
                (eq_id,),
            )
            registos = cur.fetchall()
            titulo = f"Relatório de Utilização — {equipamento['designacao']}" if equipamento else "Relatório de Utilização"

            # Resumo: quantas vezes cada utilizador usou este equipamento.
            cur.execute(
                """SELECT ut.nome AS nome, COUNT(*) AS vezes FROM utilizacoes u
                   JOIN utilizadores ut ON ut.id_utilizador = u.id_utilizador
                   WHERE u.id_equipamento=%s
                   GROUP BY ut.nome ORDER BY vezes DESC""",
                (eq_id,),
            )
            resumo = cur.fetchall()
        elif tipo == "manutencoes":
            cur.execute(
                """SELECT m.*, e.designacao FROM manutencoes m
                   JOIN equipamentos e ON e.id_equipamento = m.id_equipamento
                   ORDER BY m.id_manutencao DESC"""
            )
            registos = cur.fetchall()
            titulo = "Relatório de Manutenções e Custos"
        elif tipo == "utilizador":
            uid = args.get("utilizador_id")
            cur.execute("SELECT * FROM utilizadores WHERE id_utilizador=%s", (uid,))
            utilizador = cur.fetchone()
            cur.execute(
                """SELECT u.*, e.designacao FROM utilizacoes u
                   JOIN equipamentos e ON e.id_equipamento = u.id_equipamento
                   WHERE id_utilizador=%s ORDER BY u.id_utilizacao DESC""",
                (uid,),
            )
            registos = cur.fetchall()
            titulo = f"Relatório de Utilização — {utilizador['nome']}" if utilizador else "Relatório de Utilização"

            # Resumo: quantas vezes este utilizador usou cada equipamento.
            cur.execute(
                """SELECT e.designacao AS nome, COUNT(*) AS vezes FROM utilizacoes u
                   JOIN equipamentos e ON e.id_equipamento = u.id_equipamento
                   WHERE u.id_utilizador=%s
                   GROUP BY e.designacao ORDER BY vezes DESC""",
                (uid,),
            )
            resumo = cur.fetchall()
        else:
            cur.execute(
                """SELECT u.*, e.designacao, ut.nome AS utilizador_nome FROM utilizacoes u
                   JOIN equipamentos e ON e.id_equipamento = u.id_equipamento
                   JOIN utilizadores ut ON ut.id_utilizador = u.id_utilizador
                   ORDER BY u.id_utilizacao DESC"""
            )
            registos = cur.fetchall()
            titulo = "Relatório Geral de Utilizações"
    return titulo, registos, resumo


@app.route("/relatorios/gerar")
@login_required
def gerar_relatorio():
    tipo, args = _tipo_e_args_relatorio(request.args)
    titulo, registos, resumo = _obter_dados_relatorio(tipo, args)

    db = get_db()
    if session.get("perfil") == "Administrador":
        with db.cursor() as cur:
            cur.execute("SELECT * FROM equipamentos ORDER BY designacao")
            equipamentos = cur.fetchall()
            cur.execute("SELECT * FROM utilizadores ORDER BY nome")
            utilizadores = cur.fetchall()
    else:
        equipamentos, utilizadores = [], []

    return render_template(
        "relatorio_resultado.html",
        titulo=titulo,
        registos=registos,
        resumo=resumo,
        tipo=tipo,
        equipamentos=equipamentos,
        utilizadores=utilizadores,
        gerado_em=datetime.now().strftime("%d/%m/%Y %H:%M"),
    )


@app.route("/relatorios/gerar/pdf")
@login_required
def gerar_relatorio_pdf():
    """Gera e devolve o relatório como ficheiro PDF (exportação profissional)."""
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from flask import send_file

    tipo, args = _tipo_e_args_relatorio(request.args)
    titulo, registos, resumo = _obter_dados_relatorio(tipo, args)
    gerado_em = datetime.now().strftime("%d/%m/%Y %H:%M")

    BRAND = colors.HexColor("#4f46e5")
    INK = colors.HexColor("#0f172a")
    LINE = colors.HexColor("#e3e7f0")
    ROW_ALT = colors.HexColor("#f4f6fb")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        topMargin=18 * mm, bottomMargin=16 * mm, leftMargin=16 * mm, rightMargin=16 * mm,
        title=titulo,
    )
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle("TituloRel", parent=styles["Title"], textColor=INK, fontSize=18, spaceAfter=2)
    sub_style = ParagraphStyle("SubRel", parent=styles["Normal"], textColor=colors.HexColor("#64748b"), fontSize=9)

    elementos = [
        Paragraph("Gestão de Oficina &middot; Enterprise Suite", sub_style),
        Paragraph(titulo, titulo_style),
        Paragraph(f"Gerado em {gerado_em}", sub_style),
        Spacer(1, 10 * mm),
    ]

    if tipo == "manutencoes":
        cabecalho = ["Equipamento", "Descrição", "Início", "Fim", "Custo"]
        linhas = [
            [
                r.get("designacao", ""),
                r.get("descricao", ""),
                str(r.get("data_inicio", "")),
                str(r.get("data_fim") or "— em curso —"),
                f"{r['custo']:.2f} €" if r.get("custo") else "-",
            ]
            for r in registos
        ]
        total_custo = sum(r["custo"] for r in registos if r.get("custo"))
        rodape = f"Total de registos: {len(registos)}    |    Custo total: {total_custo:.2f} €"
    else:
        cabecalho = []
        if tipo != "equipamento":
            cabecalho.append("Equipamento")
        if tipo != "utilizador":
            cabecalho.append("Utilizador")
        cabecalho += ["Início", "Fim", "Observações"]
        linhas = []
        for r in registos:
            linha = []
            if tipo != "equipamento":
                linha.append(r.get("designacao", ""))
            if tipo != "utilizador":
                linha.append(r.get("utilizador_nome", ""))
            linha += [str(r.get("data_inicio", "")), str(r.get("data_fim") or "— em curso —"), r.get("observacoes") or "-"]
            linhas.append(linha)
        rodape = f"Total de registos: {len(registos)}"

    dados_tabela = [cabecalho] + (linhas if linhas else [["Sem registos para este relatório."] + [""] * (len(cabecalho) - 1)])
    tabela = Table(dados_tabela, repeatRows=1, hAlign="LEFT")
    estilo_tabela = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8.5),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]
    for i in range(1, len(dados_tabela)):
        if i % 2 == 0:
            estilo_tabela.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    tabela.setStyle(TableStyle(estilo_tabela))
    elementos.append(tabela)
    elementos.append(Spacer(1, 6 * mm))
    elementos.append(Paragraph(rodape, sub_style))

    if resumo:
        coluna_resumo = "Utilizador" if tipo == "equipamento" else "Equipamento"
        elementos.append(Spacer(1, 8 * mm))
        elementos.append(Paragraph(f"Resumo — nº de utilizações por {coluna_resumo.lower()}", sub_style))
        elementos.append(Spacer(1, 3 * mm))
        dados_resumo = [[coluna_resumo, "Nº de utilizações"]] + [[r["nome"], str(r["vezes"])] for r in resumo]
        tabela_resumo = Table(dados_resumo, repeatRows=1, hAlign="LEFT", colWidths=[80 * mm, 40 * mm])
        estilo_resumo = [
            ("BACKGROUND", (0, 0), (-1, 0), BRAND),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("TEXTCOLOR", (0, 1), (-1, -1), INK),
            ("GRID", (0, 0), (-1, -1), 0.5, LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]
        for i in range(1, len(dados_resumo)):
            if i % 2 == 0:
                estilo_resumo.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
        tabela_resumo.setStyle(TableStyle(estilo_resumo))
        elementos.append(tabela_resumo)

    def rodape_pagina(canvas, doc_):
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.line(16 * mm, 12 * mm, doc_.pagesize[0] - 16 * mm, 12 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.drawString(16 * mm, 8 * mm, "Gestão de Oficina — documento gerado automaticamente")
        canvas.drawRightString(doc_.pagesize[0] - 16 * mm, 8 * mm, f"Página {doc_.page}")
        canvas.restoreState()

    doc.build(elementos, onFirstPage=rodape_pagina, onLaterPages=rodape_pagina)
    buffer.seek(0)

    nome_ficheiro = f"relatorio_{tipo}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(
        buffer, mimetype="application/pdf", as_attachment=True, download_name=nome_ficheiro
    )


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
