# myroutes.py
from flask import Blueprint, render_template, request
import requests

myroutes = Blueprint('myroutes', __name__)

API_BASE = "https://api-rc-cibil-ei8h.onrender.com"

@myroutes.route('/hello')
def hello():
    return "Hello from myroutes!"


@myroutes.route('/car_lookup', methods=['GET', 'POST'])
def car_lookup():
    car_data = None
    cibil_data = None
    pan_data = None
    error = None
    action = None

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'car':
            id_number = request.form.get('id_number')
            if id_number:
                try:
                    response = requests.get(f"{API_BASE}/get_car", params={'id_number': id_number})
                    if response.status_code == 200:
                        car_data = response.json().get('data')
                    else:
                        error = response.json().get('message') or response.json().get('error')
                except Exception as e:
                    error = f"Error calling get_car: {str(e)}"
            else:
                error = "Please provide an ID number."
        
        elif action == 'cibil':
            pan = request.form.get('pan')
            if pan:
                try:
                    response = requests.get(f"{API_BASE}/get_cibil", params={'pan': pan})
                    if response.status_code == 200:
                        cibil_data = response.json().get('data')
                    else:
                        error = response.json().get('message') or response.json().get('error')
                except Exception as e:
                    error = f"Error calling get_cibil: {str(e)}"
            else:
                error = "Please provide a PAN."

        elif action == 'pan':
            mobile = request.form.get('mobile')
            if mobile:
                try:
                    response = requests.get(f"{API_BASE}/get_pan_by_mobile", params={'mobile': mobile})
                    if response.status_code == 200:
                        pan_data = response.json()
                    else:
                        error = response.json().get('message') or response.json().get('error')
                except Exception as e:
                    error = f"Error calling get_pan_by_mobile: {str(e)}"
            else:
                error = "Please provide a mobile number."

    return render_template('car_lookup.html', car_data=car_data, cibil_data=cibil_data, pan_data=pan_data, error=error)
