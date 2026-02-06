from flask import Flask, render_template, redirect, request, url_for
from datetime import datetime
from config.database import SupabaseConnection
from dao.funcionario_dao import FuncionarioDAO
from models.funcionario import Funcionario

app = Flask(__name__)

client = SupabaseConnection().client
funcionario_dao = FuncionarioDAO(client)

@app.route("/")
def index():
    return render_template("index.html", title="CRUD LEGAL", app_name="TABELA DE USER", funcionarios=funcionario_dao.read_all())

@app.template_filter('format_cpf')
def format_cpf(cpf):
    if not cpf or len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"

@app.route("/funcionario/<string:pk>/<int:id>")
def details(pk, id):
    funcionario = funcionario_dao.read(pk, id)
    return render_template("details.html", funcionario=funcionario, datetime=datetime)

@app.route('/funcionario/novo', methods=['GET', 'POST'])
def create():
    if request.method == "POST":
        dados = request.form

        from datetime import datetime as dt

        data_nasc = None
        if dados.get('data_nasc'):
            try:
                data_nasc = dt.strptime(dados['data_nasc'], '%Y-%m-%d').date()
            except:
                pass

        salario = None
        try:
            salario = float(dados.get('salario'))
        except:
            pass

        numero_departamento = None
        try:
            numero_departamento = int(dados.get('numero_departamento'))
        except:
            pass

        cpf = dados.get('cpf')
        if cpf:
            cpf = cpf.replace('.', '').replace('-', '')

        cpf_supervisor = dados.get('cpf_supervisor')
        if cpf_supervisor:
            cpf_supervisor = cpf_supervisor.replace('.', '').replace('-', '')
            if len(cpf_supervisor) != 11:
                cpf_supervisor = None

        funcionario = Funcionario(
            _cpf=cpf,
            _pnome=dados.get('pnome'),
            _unome=dados.get('unome'),
            _data_nasc=data_nasc,
            _endereco=dados.get('endereco'),
            _salario=salario,
            _sexo=dados.get('sexo'),
            _cpf_supervisor=cpf_supervisor,
            _numero_departamento=numero_departamento,
            _created_at=datetime.now()
        )

        criar = funcionario_dao.create(funcionario)

        if criar:
            return redirect(url_for('index'))

    return render_template('create.html', datetime=datetime)

@app.route('/funcionario/edit/<string:pk>', methods=['GET', 'POST'])
def update(pk):
    if request.method == 'POST':
        dados = request.form
        
        funcionario_atual = funcionario_dao.read('cpf', pk)
        
        from datetime import datetime as dt
        
        data_nasc = funcionario_atual.data_nasc
        if dados.get('data_nasc'):
            try:
                data_nasc = dt.strptime(dados['data_nasc'], '%Y-%m-%d').date()
            except:
                pass
        
        salario = funcionario_atual.salario
        try:
            salario = float(dados.get('salario', salario))
        except:
            pass
        
        num_depto = dados.get('numero_departamento')
        numero_departamento = None
        if num_depto and num_depto.strip():
            try:
                numero_departamento = int(num_depto)
            except:
                numero_departamento = funcionario_atual.numero_departamento
        
        cpf_supervisor = dados.get('cpf_supervisor')
        if cpf_supervisor and cpf_supervisor.strip():
            cpf_supervisor = cpf_supervisor.replace('.', '').replace('-', '')
            if len(cpf_supervisor) != 11:
                cpf_supervisor = None
        else:
            cpf_supervisor = None
        
        funcionario_atualizado = Funcionario(
            _cpf=pk,
            _pnome=dados.get('pnome', funcionario_atual.pnome),
            _unome=dados.get('unome', funcionario_atual.unome),
            _data_nasc=data_nasc,
            _endereco=dados.get('endereco', funcionario_atual.endereco),
            _salario=salario,
            _sexo=dados.get('sexo', funcionario_atual.sexo),
            _cpf_supervisor=cpf_supervisor,
            _numero_departamento=numero_departamento,
            _created_at=funcionario_atual.created_at
        )
        
        atualizar = funcionario_dao.update('cpf', pk, funcionario_atualizado)
        
        if atualizar:
            return redirect(url_for('index'))
    
    funcionario = funcionario_dao.read('cpf', pk)
    
    return render_template('edit.html', funcionario=funcionario, datetime=datetime)

@app.route('/funcionario/delete/<string:pk>', methods=['GET', 'POST'])
def delete(pk):
    if request.method == 'POST':
        deletar = funcionario_dao.delete('cpf', pk)
        
        if deletar:
            return redirect(url_for('index'))
    
    funcionario = funcionario_dao.read('cpf', pk)
        
    return render_template('delete.html', funcionario=funcionario, datetime=datetime)