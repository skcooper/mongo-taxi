from flask import Flask, render_template, redirect, request
import pymongo

app = Flask(__name__, static_url_path = "")
connection_string = "mongodb://127.0.0.1"
connection = pymongo.MongoClient(connection_string)
database = connection.taxi
rides = database.rides

#Homepage
@app.route('/')
def splash():
	return app.send_static_file('splash.html')

#Individual information page for each book
@app.route('/detail/<name>/', methods=['GET', 'POST'])
def detail(name):
	if request.method == 'GET':
		cursor = rides.find_one({'name':name})

	elif request.method == 'POST':
		#Add new values of all pre-existing attributes
		updated_document = {attribute: value for attribute, value in request.form.iteritems() if attribute[:9] != 'new_field' and attribute[:9] != 'new_value'}
		num_old_fields = len(updated_document)
		num_new_fields = (len(request.form)-num_old_fields)/2
		#Add values of new fields, if any
		if(num_new_fields > 0):
			for i in range(1, num_new_fields + 1):
				new_attribute = request.form['new_field'+str(i)]
				new_value = request.form['new_value'+str(i)]
				updated_document[new_attribute] = new_value
		rides.update({'name':name}, updated_document)
		cursor = rides.find_one({'name': request.form['name']})
			
	results = {field:value for field, value in cursor.items() if field != 'claimed'}
	return render_template('detail.html', result=results)


@app.route('/claim/<name>/', methods=['GET', 'POST'])
def claim(name):	
	cursor = rides.find_one({'name':name})
	cursor_dict = {field:value for field, value in cursor.items()}
	already_claimed = cursor_dict['claimed']
	if request.method == 'GET':
		claimed_result = {field:value for field, value in cursor.items()}
		claimed_result['claimed'] = True
		rides.update({'name':name}, claimed_result)

	elif request.method == 'POST':
		new_data = {k : v for k, v in request.form.items()}
		new_data.update({field:value for field, value in cursor.items()})
		#Add values of driver fields
		rides.update({'name':name}, new_data)
		cursor = rides.find_one({'name':name})
			
	results = {field:value for field, value in cursor.items() if field != 'claimed'}
	return render_template('claim.html', result = results, already_claimed = already_claimed)

@app.route('/cancel_claim/<name>/', methods=['POST'])
def cancel_claim(name):
	unclaimed_result = {field:value for field, value in rides.find_one({'name':name}).items()}
	unclaimed_result['claimed'] = False;
	rides.update({'name':name}, unclaimed_result)
	return render_template('cancel_claim.html', result=unclaimed_result)


@app.route('/unclaimed_rides/', methods=['GET', 'POST'])
def unclaimed_rides():
	if request.method == 'GET':
		results = rides.find({'claimed':False})
		return_dict = convert_to_dict(results)

		return render_template('unclaimed_rides.html', posting=False, result=return_dict)


# serves image in image file for a particular book
@app.route('/static/images/<image>/')
def image(image):
	return app.send_static_file('images/'+image)

# Leads to detail page of a randomly chosen book
@app.route('/featured/')
def featured():
	random = rides.find_one()
	return redirect('/detail/'+random['name']+'/')


# The search page
@app.route('/search/', methods=['GET', 'POST'])
def search():
	#Return results for titles, authors and genres that match the search query
	if request.method == 'POST':
		query = request.form['query']
		
		# can add more fields to check for them too
		cursor = rides.find({"$or": [{'name':query}, {'destination':query}, {'pickup':query}, {'phone':query}]})
		no_results = cursor.count() == 0
		cursor_dict = convert_to_dict(cursor)
		return render_template('search.html', posting=True, query=query, no_results=no_results, cursor_result = cursor_dict)  
	else:
		return render_template('search.html', posting=False)


def convert_to_dict(iterable):
	outer_dict = {}
	for element in iterable:
		inner_dict = {} 
		for key in element:
			inner_dict[key] = element[key]	
		outer_dict[element['_id']]= inner_dict
	return outer_dict


#The page to add a book to the database
@app.route('/add/', methods=['GET', 'POST'])
def add():
	if request.method == 'POST':
		new_data = {k : v for k, v in request.form.items()}
		new_data['claimed'] = False
		#If the user leaves a field blank
		if new_data['name'] == '' or new_data['phone'] == '' or new_data['pickup'] == '' or new_data['destination'] == '':
			return render_template('add.html', alert="required")
		#If the user tries to add a book that's already in the database
		elif rides.find({'name':new_data['name'], 'phone':new_data['phone'], 'pickup':new_data['pickup'], 'destination':new_data['destination']}).count() > 0: 
			return render_template('add.html', alert="exists")
		else:
			rides.insert(new_data)
			return render_template('add.html', alert = "success")
	else:
		return render_template('add.html', alert="")

if __name__ == '__main__':
	app.debug = True
	app.run()



