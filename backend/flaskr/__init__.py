import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page',1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE    
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
 
    # CORS Headers 
    @app.after_request
    def after_request(response):
        '''
        Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs 
        '''
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')        
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    @app.route('/questions',methods=['GET'])
    def retrive_questions():
        '''    
        Create an endpoint to handle GET requests for questions, 
        including pagination (every 10 questions). 
        This endpoint should return a list of questions, 
        number of total questions, current category, categories.  
        '''
        
        all_ques = Question.query.order_by(Question.id).all()
        current_questions_paginated = paginate_questions(request, all_ques) 
        if (len(current_questions_paginated) == 0):
            abort(404)
        try:
            all_categories = Category.query.all()    
            categories_dict = {}
            for category in all_categories:
                categories_dict[category.id] = category.type
            
            return jsonify({
            'success': True,
            'questions': current_questions_paginated,
            'total_questions': len(Question.query.all()),
            'categories': categories_dict,
            'current_category': None
            })
        except:
            abort(422)
    
    @app.route('/questions', methods=['POST'])
    def new_question():
        '''    
        Create an endpoint to POST a new question, 
        which will require the question and answer text, 
        category, and difficulty score.
        '''        
        body = request.get_json()               
        question_new = body.get('question')
        answer_new = body.get('answer')
        difficulty_new = body.get('difficulty')
        category_new = body.get('category')

        # ensure all fields have data
        if ((question_new.strip() == "") or (answer_new.strip() == "")
                or (difficulty_new == None) or (category_new == None)):
            abort(422)

        try:
            # create and insert new question
            question = Question(question=question_new, answer=answer_new,
                                difficulty=difficulty_new, category=category_new)
            question.insert()     
            
            #get all questions and paginate
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            
            #return data to view
            return jsonify({
                'success': True,
                'created': question.id,
                'question_created': question.question,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
            
        except:
            # abort unprocessable if exception
            abort(422)
        
        
    @app.route('/categories', methods=['GET'])
    def retrive_categories():
        '''   
        Create an endpoint to handle GET requests 
        for all available categories.
        '''             
        categories = Category.query.order_by(Category.id).all()
        if len(categories)==0:
            abort(404)
        try:
            categories_dict = {}
            for category in categories:
                categories_dict[category.id] = category.type
           
            return jsonify({
                
                'categories': categories_dict
                
                })
        except:
            abort(404)
        
        
    @app.route('/questions/<int:ques_id>', methods=['DELETE'])
    def delete_question(ques_id):   
        '''
        Create an endpoint to DELETE question using a question ID.   
        '''
        ques_delete = Question.query.filter(Question.id == ques_id).one_or_none()         
        if ques_delete is None:
            abort(404)
        try:
            ques_delete.delete()            
            selection = Question.query.order_by(Question.id)
            current_questions = paginate_questions(request, selection)
            return jsonify({
            'success': True,
            'id of question deleted': ques_id,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
            })
        except: 
            abort(422)
    
    @app.route('/questions/search', methods=['POST'])
    def search_question(): 
        '''        
        Create a POST endpoint to get questions based on a search term. 
        It should return any questions for whom the search term 
        is a substring of the question.       
        '''
        body = request.get_json()        
        term_to_be_search = body.get('searchTerm', None)         
        search_results  = Question.query.filter(
                Question.question.ilike(f'%{term_to_be_search}%')).all()
        if len(search_results) == 0:
            return not_found(404)
        try:
            searched_question = [question.format()for question in search_results]
            return jsonify({
            'success': True,            
            'questions': searched_question,
            'totalQuestions': len(searched_question), 
            'categories': None
            })
        except:
            abort(422)
    
    
    @app.route('/categories/<int:cat_id>/questions')
    def question_based_on_category(cat_id): 
        '''        
        Create a GET endpoint to get questions based on category.        
        '''
        category_data = Category.query.filter(Category.id == cat_id).all() 
        if len(category_data) == 0:
                return not_found(404)       
        ques_cat = Question.query.filter(Question.category == cat_id).all()         
        current_ques_cat = paginate_questions(request, ques_cat)         
        if (len(current_ques_cat) == 0):
            abort(404)
        try:            
            return  jsonify({            
            'questions': current_ques_cat,
            'totalQuestions': len(ques_cat),
            'currentCategory': category_data[0].type
            })
        except:
            abort(422)
            
    @app.route('/quizzes',methods=['POST'])
    def game(): 
        '''        
        Create a POST endpoint to get questions to play the quiz. 
        This endpoint should take category and previous question parameters 
        and return a random questions within the given category, 
        if provided, and that is not one of the previous questions.         
        '''
        body = request.get_json()

        # get the previous questions
        previous_number = body.get('previous_questions',None)

        # get the category
        category_string = body.get('quiz_category',None)
        try:
        # abort 400 if category or previous questions isn't found
            if ((category_string is not None) or (previous_number is not None)):
                if (category_string['id'] != 0):
                    questions = Question.query.filter_by(category=category_string['id']).all()                  
                # load questions all questions if "ALL" is selected
                else:
                    questions = Question.query.all()                
                list_question = []
                for q in questions:
                    list_question.append(q.id)
                #print(list_question)
                questions_not_asked=[]
                for  q in list(set(list_question)):
                    if q not in list(set(previous_number)):
                        questions_not_asked.append(q) 
                if len(questions_not_asked) == 0:
                     return jsonify({
                    'success': True
                    })
                else:
                    random_ques_id = random.choice(questions_not_asked)
                
                    question = Question.query.filter(Question.id == random_ques_id).first()     
                    return jsonify({
                    'success': True,
                    'question': question.format()
                    })
            else:
                abort(400)
        except:
            abort(422)
            
            
       
            
    @app.errorhandler(404)
    def not_found(error):
        '''   
        Create error handlers for all expected errors 
        including 404. 
        '''
        return jsonify({
        'success': False,
        'error': 404,
        'message':"Resource Not Found"}),404
        
    
    @app.errorhandler(422)
    def unprocessable(error):
        '''   
        Create error handlers for all expected errors 
        including 422. 
        '''
        return jsonify({
        'success':False,
        'error':422,
        'message':"Resource not processable"}),422
        
        
    return app

    
    

    
