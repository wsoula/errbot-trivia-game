""" Output the request ratio for the last X weeks for PA-UE1 to each service """
import logging
import urllib
import json
from errbot import BotPlugin, botcmd, arg_botcmd
from errbot import botflow, FlowRoot, BotFlow, FLOW_END

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TOTAL_QUESTIONS = 2


class GuessFlows(BotFlow):
    """ Conversation flows related to polls"""

    @botflow
    def guess(self, flow: FlowRoot):
        """ This is a flow that can set a guessing game."""
        # setup Flow
        # game_created = flow.connect('trivia', auto_trigger=True, room_flow=True)
        game_created = flow.connect('trivia', auto_trigger=True, room_flow=False)
        # question = game_created.connect('question', predicate=lambda ctx: 'trivias' in ctx) # ctx is {}
        question = game_created.connect('question')
        # question.connect(question, predicate=lambda ctx: 'correct' in ctx)  # loop on question: ctx is {}
        one_guess = question.connect('guess')
        one_guess.connect(one_guess)  # loop on itself
        one_guess.connect(question, predicate=lambda ctx: 'correct' in ctx)  # loop on question
        one_guess.connect(FLOW_END, predicate=lambda ctx: 'ended' in ctx)
        game_created.hints = False
        question.hints = False
        one_guess.hints = False


class TriviaGame(BotPlugin):
    """ Trivia Game """
    @botcmd
    def trivia(self, msg, args):
        """ Get trivia questions """
        logger.debug('msg=%s\nargs=%s', msg, args)
        url = 'https://opentdb.com/api.php?amount='+str(TOTAL_QUESTIONS)
        page = urllib.request.Request(url)
        response = json.loads(urllib.request.urlopen(page).read().decode('utf-8'))
        if 'results' in response:
            msg.ctx['trivias'] = response['results']
            msg.ctx['index'] = 0
            return 'Questions Retrieved'
        return 'No questions returned'

    @botcmd
    def question(self, msg, args):
        """ Get a question """
        logger.debug('msg=%s\nargs=%s', msg, args)
        if 'trivias' in msg.ctx:
            index = msg.ctx['index']
            msg.ctx['question'] = msg.ctx['trivias'][index]['question']
            msg.ctx['correct_answer'] = msg.ctx['trivias'][index]['correct_answer']
            msg.ctx['incorrect_answers'] = msg.ctx['trivias'][index]['incorrect_answers']
            answers = ''
            for answer in msg.ctx['incorrect_answers']:
                answers = answers + answer + '\n'
            answers = answers + msg.ctx['correct_answer']
            return msg.ctx['question']+'\n'+answers
        logger.info('msg.ctx=%s', msg.ctx)
        return 'Must initialize with trivia command first'

    @arg_botcmd('guess', type=str)
    def guess(self, msg, guess):
        """ Guess """
        if 'trivias' in msg.ctx and 'correct_answer' in msg.ctx:
            if guess == msg.ctx['correct_answer']:
                msg.ctx['index'] = msg.ctx['index'] + 1
                msg.ctx['correct'] = True
                if msg.ctx['index'] == TOTAL_QUESTIONS:
                    msg.ctx['ended'] = True
                return 'You got it!'
            else:
                return guess+' was not it'
        logger.info('msg.ctx=%s', msg.ctx)
        return 'Must initialize with trivia command and/or question command first'
