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
# @app.route('/detail/<user_name>/', methods=['GET', 'POST'])
# def detail(user_name):
# 	if request.method == 'GET':
# 		cursor = books.find_one({'user_name':user_name})

# 	elif request.method == 'POST':
# 		#Add new values of all pre-existing attributes
# 		updated_document = {attribute: value for attribute, value in request.form.iteritems() if attribute[:9] != 'new_field' and attribute[:9] != 'new_value'}
# 		num_old_fields = len(updated_document)
# 		num_new_fields = (len(request.form)-num_old_fields)/2
# 		#Add values of new fields, if any
# 		if(num_new_fields > 0):
# 			for i in range(1, num_new_fields + 1):
# 				new_attribute = request.form['new_field'+str(i)]
# 				new_value = request.form['new_value'+str(i)]
# 				updated_document[new_attribute] = new_value
# 		books.update({'user_name':user_name}, updated_document)
# 		cursor = books.find_one({'user_name': request.form['user_name']})
			
# 	results = {field:value for field, value in cursor.items()}
# 	return render_template('detail.html', result=results)

#serves image in image file for a particular book
# @app.route('/static/images/<image>/')
# def image(image):
# 	return app.send_static_file('images/'+image)

#Leads to detail page of a randomly chosen book
# @app.route('/featured/')
# def featured():
# 	random = books.find_one()
# 	return redirect('/detail/'+random['title']+'/'+random['author']+'/')


#The search page
# @app.route('/search/', methods=['GET', 'POST'])
# def search():
# 	#Return results for titles, authors and genres that match the search query
# 	if request.method == 'POST':
# 		query = request.form['query']
		
# 		user_cursor = books.find({'user_name':query})
# 		driver_cursor = books.find({'driver_name':query})
# 		start_location_cursor = books.find({'starting_location':query})
# 		end_location_cursor = books.find({'ending_location':query})

# 		no_results = user_cursor.count() == 0 and driver_cursor.count() == 0 and start_location_cursor.count() == 0 and end_location_cursor.count() == 0

# 		user_dict = convert_to_dict(user_cursor)
# 		driver_dict = convert_to_dict(driver_cursor)
# 		start_location_dict = convert_to_dict(start_location_cursor)
# 		end_location_dict = convert_to_dict(end_location_cursor)

# 		# title_cursor = books.find({'title':query})
# 		# author_cursor = books.find({'author':query})

# 		# no_results = author_cursor.count() == 0 and title_cursor.count() == 0
	
# 		# title_dict = convert_to_dict(title_cursor)
# 		# author_dict = convert_to_dict(author_cursor)     

# 		return render_template('search.html', posting=True, query=query, no_results=no_results, user_results=user_dict, driver_results=driver_dict, start_location_results=start_location_dict, end_location_results=end_location_dict)  
# 	else:
# 		return render_template('search.html', posting=False)


# def convert_to_dict(iterable):
# 	outer_dict = {}
# 	for element in iterable:
# 		inner_dict = {} 
# 		for key in element:
# 			inner_dict[key] = element[key]	
# 		outer_dict[element['_id']]= inner_dict
# 	return outer_dict


#The page to add a book to the database
@app.route('/add/', methods=['GET', 'POST'])
def add():
	if request.method == 'POST':
		new_data = {k : v for k, v in request.form.items()}
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



