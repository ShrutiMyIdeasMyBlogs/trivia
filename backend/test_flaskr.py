import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"       
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres','kitten','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            
    def tearDown(self):
        """Executed after reach test"""
        pass
        
    def test_retrive_questions_paginated(self):
        '''
        At this point, when you start the application
        you should see questions and categories generated,
        ten questions per page and pagination at the bottom of the screen for three pages.
        Clicking on the page numbers should update the questions.
        '''
        res = self.client().get('/questions')
        data = json.loads(res.data)        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
    
    def test_retrive_questions_paginated_not_prcessable(self):
       
        '''
        At this point, when you start the application
        you should see questions and categories generated,
        ten questions per page and pagination at the bottom of the screen for three pages.
        Clicking on the page numbers should update the questions.
        '''
        res = self.client().get('/questions&page=1000')
        data = json.loads(res.data)        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
       
        
    def test_add_questions(self):
        new_question = {"question": "test add question", "answer": "test Add",
                   "category": 1, "difficulty": 4}        
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)        
        self.assertTrue(data['created'])
    
    
    def test_add_questions_not_processable(self):        
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)        
        
        
    def test_retrive_categories_paginated(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)         
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['category'])
        self.assertTrue(data['total_categories'])
        
    def test_retrive_categories_paginated_not_found(self):
        res = self.client().get('/categories&page=999999')
        data = json.loads(res.data)         
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])
        
        
    def test_delete_question(self):
        new_question = Question(question='It is a trial question 3',                                                          
                                    answer='trial answer 3',      
                                    category=1,
                                    difficulty=1)        
        model = Question    #to get the column names of Question table
        columns = [m.key for m in model.__table__.columns]                            
        new_question.insert()        
        question_id = new_question.id          
        res = self.client().delete('/questions/{}/remove'.format(question_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['id of question deleted'])
    
    def test_delete_question_not_found(self):             
        res = self.client().delete('/questions/{}/remove'.format('999999999999999'))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)        
        self.assertTrue(data['message'])
        
    def test_search_question(self):
        '''
        The questions list will update to include 
        only question that include that string within their question. 
        Try using the word "title" to start. 
        '''
        res = self.client().post('/questions/search', json={"searchTerm":"is"})        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['categories'],None)
    
    def test_search_question_not_found(self):
        '''
        The questions list will update to include 
        only question that include that string within their question.        
        '''
        res = self.client().post('/questions/search', json={"searchTerm":"abcdefgh"})        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)        
        self.assertTrue(data['message'])
        
    def test_question_based_on_category(self):
        '''
        The questions list will update to include 
        only question that include that are in the specified category.        
        '''
        res = self.client().get('categories/{}/questions'.format('1'))        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)        
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['categories'],1)    
        
    def test_question_based_on_category_not_found(self):
        '''
        The questions list will update to include 
        only question that include that are in the specified category.        
        '''
        res = self.client().get('questions/{}/categories'.format('99999'))        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False) 
        self.assertTrue(data['message'])   
    
    def test_game(self):
        '''
        In the "Play" tab, after a user selects "All" or a category,
        one question at a time is displayed, the user is allowed to answer
        and shown whether they were correct or not. 
        '''
        res = self.client().post('/quizzes',json={"previous_questions": [20, 21], "quiz_category": {"type": "Science", "id": 1}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)        
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['categories'],1) 
        
    def test_game_not_found(self):
        '''
        In the "Play" tab, after a user selects "All" or a category,
        one question at a time is displayed, the user is allowed to answer
        and shown whether they were correct or not. 
        '''
        res = self.client().post('/quizzes',json={"previous_questions": [20, 21]})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)        
        self.assertTrue(data['message'])
           


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()