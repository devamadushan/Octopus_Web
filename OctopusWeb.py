'''

pip install flask
pip install json
pip instal requests
pip install Flask-SQLAlchemy

'''

############################################################################################################

from flask import Flask, render_template, request, jsonify, url_for, redirect
import json
import requests
import json
import requests
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from Connexion import utilisateur,session, password, base_de_donne, port, Base, DB_URL
from History import Historiy_cells
from Experiment import Experiment
from Cells import Cells
from User import User
from OctopusDB import octopus

############################################################################################################

# App setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{utilisateur}:{password}@localhost:{port}/{base_de_donne}'

############################################################################################################

# Recovery of configuration informations
with open('/home/deva/Bureau/Octopus_Web/Octopus_Web/config.json', 'r') as config:
    config = json.load(config)
    ip = config['IP']
    port = config['Port']
    debug = config['Debug']

############################################################################################################
# Auteur Luca et Deva

# Basic role 
role = "visiteur"

# Web pages

# Connection
@app.route('/connexion')
def forms():
    return render_template('connection.html',ip=ip, port=port)

# Index
@app.route('/')
def index():
    global role
    try:
        # Retrieving data in Json Ecolab 2
        #ecolab2 = "http://10.119.20.100:8080/"
        

        # Retrieving data in Json Ecolab 4
        ecolab4 = "http://10.119.40.100:8080/"
        json_data4 = requests.get(ecolab4).json()
        json_data2 = requests.get(ecolab4).json()
       
        return render_template('index.html', role= role, info2=json_data2, info4=json_data4)
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return "Erreur lors de la récupération des données depuis l'API."
    
    
# Détails
@app.route('/detail',methods=['POST'])
def detail():
    global session
    try:
        #I collect the name of the cell that the client clicked using the POST method.
        cellule_name =request.form.get('name')
        #cellule_name = "E2C3"

        #I'm trying to get the Ecolab and Cell numbers by their names
        ecolab = cellule_name[1]
        cell =  cellule_name[3]

        #Collection of parameters of cells
        # Ip according to ecolab
        data = requests.get(f'http://10.119.{ecolab}0.100:8080/')
        parameters = data.json()

        #I utilize the collected numbers to create patterns such as 'ecolab_(number of ecolab)' 
        #and 'Cellule_(number of cellule)
        jsonEcolab = f"ecolab_{ecolab}"
        jsonCellule = f"Cellule_{cell}"

        #Obtaining the Cellule object using its name
        cellule = octopus.get_cellule_by_name(cellule_name)
        
        #Obtaining the Experiment object using its ID
        ExperimentInProgress = cellule.Experiment_id

        #Obtaining a list of all historique of cellule using its ID
        historique = octopus.get_historique_by_id(cellule.id)

        #Obtaining a list of all Experiment with satus "a venir" are "en cours"
        future_and_current_Experiments = octopus.get_futur_and_current_Experiment()
        session.commit()

        return render_template('detail.html',Experiment_avenir_encours = future_and_current_Experiments ,nom_cellule=cellule_name, 
                           cellule = cellule, Experiment=ExperimentInProgress,info = parameters, historique= historique, jsonEcolab = jsonEcolab, jsonCellule=jsonCellule )
    except requests.exceptions.RequestException as e:
        return render_template('error.html', error_message=str(e))
    
# Experiments
@app.route('/Experiments')
def Experiments():
    global session
    #Obtaining all Experiments existing in the database
    Experiments = octopus.get_all_Experiment()
    session.commit()
    return render_template('Experiment.html',Experiments=Experiments)

# Add Experiment
@app.route('/add-Experiments')
def addExperiment():
    return render_template('addExperiment.html')

# Edit Experiment
@app.route('/edit-Experiments',methods=['POST'])
def editExperiments():
    id_Experiment = int(request.form.get('id_Experiment'))

    #Obtaining the object of Experiment using its ID
    Experiment = octopus.get_Experiment_by_id(id_Experiment)
    #print(Experiment)
    return render_template('editExperiment.html',Experiment=Experiment)

############################################################################################################
# Action Methods 

# Disconnection
@app.route('/deconnexion')
def deconnexion():
    global role
    role='visiteur'
    return redirect(url_for('index'))

# Connection processing
@app.route('/traitement', methods=['POST'])
def traitement():
    global role

    login = request.form.get('login')
    mdp = request.form.get('password')


    authentification = octopus.user_exists(login,mdp)

    if authentification == True:
        role = octopus.get_role_by_user(login)

         # Admin template
        if role == 'admin':
            try:
                # Retrieving data in Json Ecolab 2
                ecolab2 = "http://10.119.20.100:8080/"
                json_data2 = requests.get(ecolab2).json()

                # Retrieving data in Json Ecolab 4
                ecolab4 = "http://10.119.40.100:8080/"
                json_data4 = requests.get(ecolab4).json()

                return render_template('adminTemplate.html', role=role, info2=json_data2, info4=json_data4)
            except Exception as e:
                print(f"Une erreur s'est produite : {e}")
            return "Erreur lors de la récupération des données depuis l'API."
        
        elif role == 'normal':
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    else:
        return render_template('connection.html', authentification=authentification)
    
# Return admin template
@app.route('/', methods=['POST'])
def retour():
    global role
    try:
        # Retrieving data in Json Ecolab 2
        ecolab2 = "http://10.119.20.100:8080/"
        json_data2 = requests.get(ecolab2).json()

        # Retrieving data in Json Ecolab 4
        ecolab4 = "http://10.119.40.100:8080/"
        json_data4 = requests.get(ecolab4).json()
       
        return render_template('adminTemplate.html', role=role, info2=json_data2, info4=json_data4)
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return "Erreur lors de la récupération des données depuis l'API."

# Add Experiment passed
@app.route('/new-Experiment-in-cellule', methods=['POST'])
def new_Experiment_in_cellule():
    global session
    try: 
        #Obtaining ID of Experiment using method POST
        Experiment_id= int(request.form.get('Experiment')) 

         #Obtaining ID of cellule using method POST
        cellule_id = int(request.form.get('cellule'))

         #Obtaining name of cell 
        cellule_name = octopus.get_cellule_name_from_id(cellule_id)

         #Obtaining the experiens in Progress
        ExperimentInProgress = request.form.get('ExperimentEnCours')#int()

        #update column status of historique using cell ID
        update_historique = octopus.update_historique(cellule_id)

        update_cellule = octopus.new_Experiment_of_cellule(cellule_id,Experiment_id)
        add_historique = octopus.new_historique(cellule_id,Experiment_id)

        session.commit()
        return render_template('successAddExperimentInCellule.html',cellule = cellule_name)
    
    except requests.exceptions.RequestException as e:
        return render_template('error.html', error_message=str(e))

# Add Experiment 
@app.route('/process-add-Experiments',methods=['POST'])
def processToAddExperiment():
    global session
    #Obtaining the new datas of Experiment for creat an object 
    name = request.form.get('nom')
    starting_date = request.form.get('date_debut')
    finishing_date = request.form.get('date_fin')
    status = request.form.get('etat_Experiment')
    newExperiment = Experiment(nom=name,date_debut=starting_date,date_fin=finishing_date,etat_Experiment=status)
    session.add(newExperiment)
    session.commit()
    return redirect(url_for('Experiments'))

# Edit Experiment
@app.route('/process-edit-Experiments',methods=['POST'])
def processToEditExperiments():
    global session
    #Obtaining the new datas of Experiment for edit the object 
    id_Experiment = int(request.form.get('id_Experiment'))
    nom = request.form.get('nom')
    date_debut = request.form.get('date_debut')
    date_fin = request.form.get('date_fin')
    etat = request.form.get('etat_Experiment')

    #Obtaining the relevant object in the database
    Experiment = octopus.get_Experiment_by_id(id_Experiment)

    #edit the datas
    Experiment.nom=nom
    if date_debut:
        Experiment.date_debut = date_debut
    if date_fin:
        Experiment.date_fin = date_fin
    Experiment.etat_Experiment = etat   
    session.commit()
    return redirect(url_for('Experiments'))

# Start Flask server
if __name__ == '__main__':
    app.run(host=ip,port=5500,debug=debug)