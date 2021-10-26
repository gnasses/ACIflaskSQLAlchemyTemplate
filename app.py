from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from netmiko import Netmiko
import util
import json
from ntc_templates.parse import parse_output
from pythonping import ping
import acitoolkit.acitoolkit as aci
import sys
import re
# Init app
app = Flask(__name__)
# Database
# This containst the default config for a local SQLite flat file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mysqlitedb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init Marshmallow
ma = Marshmallow(app)
# BGP Database Class/Model
#Here is the class to create/use the SQL table/columns, a primary key is edit/replace columns as needed
class TABLE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac = db.Column(db.String(50), nullable=False)
    ip = db.Column(db.String(50))
    interface = db.Column(db.String(60))

    
    def __repr__(self):
        return '<%r>' % self.id
# BGP Schema for Marshmallow API Functionality
# fields in the schema should match columns in the db
class TABLESchema(ma.Schema):
    class Meta:
        fields = ('id', 'mac', 'ip', 'interface')
# Init Schema        
TABLE_schema = TABLESchema()
TABLES_schema = TABLESchema(many=True)

"""
To build/rebuild the db, execute the following after stopping the app, closing the python console and deleting the old .db file:
from app import db
db.create_all()
"""
# APIC Vars
apic_ip = '10.10.20.14'
#apic_ip = 'sandboxapicdc.cisco.com'
apic_username = 'admin'
apic_password = 'C1sco12345'
#apic_password = '!v3G@!4@Y'
apic_url = 'https://' + apic_ip

#App Routes
#The first route is the index route which is required. Best practive is to limit methods to those supported.
# Typical function show with a post method for form, otherise a default listing of all db entries
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        mac = request.form['mac']
        data = TABLE.query.filter(TABLE.mac == mac).all()
        return render_template('index.html', data=data)
    else:
        data = TABLE.query.all()
        return render_template('index.html', data=data)

#This route links to the first python action, things to populate your DB or manipulate it's fields
@app.route('/action', methods=['POST', 'GET'])
def action():
    if request.method == 'POST':
        macrequest = request.form['mac']
        session = aci.Session(apic_url, apic_username, apic_password)
        resp = session.login()
        if not resp.ok:
            print("ERROR: Could not login into APIC: %s" % apic_ip)
            sys.exit(0)
        else:
            print("SUCCESS: Logged into APIC: %s" % apic_ip)
        endpoints = aci.Endpoint.get(session)
        table_data = []
        for endpoint in endpoints:
            if endpoint.if_dn:
                for dn in endpoint.if_dn:
                    match = re.match('protpaths-(\d+)-(\d+)', dn.split('/')[2])
                    if match:
                        if match.group(1) and match.group(2):
                            interf = "Nodes: " + match.group(1) + "-" + match.group(2) + " " + endpoint.if_name
                            table_row = { "mac": endpoint.mac, "ip": endpoint.ip, "interface": interf}
                            table_data.append(table_row)
            else:
                interf = endpoint.if_name
                table_row = { "mac": endpoint.mac, "ip": endpoint.ip, "int": interf}
                table_data.append(table_row)
        return render_template('action.html', data=table_data) 
    else:       
        return redirect('/')        
@app.route('/collect', methods=['GET', 'POST'])
def collect():    
    if request.method == 'POST':
        session = aci.Session(apic_url, apic_username, apic_password)
        resp = session.login()
        if not resp.ok:
            print("ERROR: Could not login into APIC: %s" % apic_ip)
            sys.exit(0)
        else:
            print("SUCCESS: Logged into APIC: %s" % apic_ip)
            db.session.query(TABLE).delete()
        endpoints = aci.Endpoint.get(session)
        table_data = []
        for endpoint in endpoints:
            if endpoint.if_dn:
                for dn in endpoint.if_dn:
                    match = re.match('protpaths-(\d+)-(\d+)', dn.split('/')[2])
                    if match:
                        if match.group(1) and match.group(2):
                            interf = "Nodes: " + match.group(1) + "-" + match.group(2) + " " + endpoint.if_name
                            table_row = { "MAC": endpoint.mac, "IP": endpoint.ip, "INT": interf}
                            table_data.append(table_row)
            else:
                interf = endpoint.if_name
                table_row = { "MAC": endpoint.mac, "IP": endpoint.ip, "INT": interf}
                table_data.append(table_row)
        print (table_data)
        for row in table_data:
                mac=row['MAC']
                ip=row['IP']
                interface=row['INT']
                new_entry = TABLE(mac=mac, ip=ip, interface=interface)
                db.session.add(new_entry)
                db.session.commit()
        data = TABLE.query.all()
        print (data)
        return render_template('action.html', data=data)     
    else:       
        return redirect('/')  
    


# API Routes
# API GET Query
@app.route('/api/mac', methods = ['GET'])
def api_function():
    data = TABLE.query.all()
    result = TABLES_schema.dump(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
